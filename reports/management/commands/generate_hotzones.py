from django.core.management.base import BaseCommand
from django.db import connection
from django.db.models import Avg

from uxo_records.models import UXORecord
from reports.models import HotZone


class Command(BaseCommand):
    help = 'Generates risk "hot zones" by clustering UXO records using DBSCAN.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting hot zone generation..."))

        # Step 1: Clear all existing HotZone records for a fresh calculation
        self.stdout.write("Deleting old hot zone data...")
        HotZone.objects.all().delete()

        # Step 2 & 3: Use a raw SQL query to perform clustering and generate convex hull polygons.
        # ST_ClusterDBSCAN groups points into clusters.
        # ST_ConvexHull creates a polygon around each cluster of points.
        self.stdout.write("Clustering UXO records and generating polygons...")
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    ST_ConvexHull(ST_Collect(location)) AS cluster_polygon,
                    ARRAY_AGG(id) as id_list
                FROM (
                    SELECT
                        id,
                        location,
                        ST_ClusterDBSCAN(location, eps := 0.050, minpoints := 3) OVER() AS cluster_id
                    FROM uxo_records_uxorecord
                ) AS clustered_points
                WHERE cluster_id IS NOT NULL
                GROUP BY cluster_id;
            """
            )
            clusters = cursor.fetchall()

        self.stdout.write(
            self.style.SUCCESS(f"Found {len(clusters)} potential hot zones.")
        )

        # Step 4 & 5: For each generated polygon, calculate stats and save the HotZone object
        self.stdout.write("Aggregating data and saving new hot zones...")
        for cluster_polygon_hex, id_list in clusters:
            # Find all UXORecord objects within this new polygon
            records_in_cluster = UXORecord.objects.filter(id__in=id_list)

            # Calculate the count and average danger score
            record_count = records_in_cluster.count()
            aggregation_results = records_in_cluster.aggregate(
                avg_danger_score=Avg("danger_score")
            )
            avg_danger_score = aggregation_results.get("avg_danger_score", 0.0)

            # Create and save the new HotZone object
            HotZone.objects.create(
                geometry=cluster_polygon_hex,
                record_count=record_count,
                avg_danger_score=avg_danger_score,
            )

        self.stdout.write(self.style.SUCCESS("Hot zone generation complete!"))
