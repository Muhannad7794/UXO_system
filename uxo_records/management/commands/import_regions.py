# uxo_records/management/commands/import_regions.py

import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import (
    GEOSGeometry,
    Polygon,
    MultiPolygon,
)  # Import Polygon and MultiPolygon
from django.db import transaction
from uxo_records.models import Region


class Command(BaseCommand):
    help = "Imports administrative regions from a CSV file into the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file_path",
            type=str,
            help="The path to the regions CSV file to import.",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing Region data before importing.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        csv_file_path = options["csv_file_path"]
        clear_data = options["clear"]

        if clear_data:
            self.stdout.write(self.style.WARNING("Clearing existing Region data..."))
            Region.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Existing Region data cleared."))

        try:
            df = pd.read_csv(csv_file_path)
        except FileNotFoundError:
            raise CommandError(f'Error: CSV file not found at "{csv_file_path}"')

        self.stdout.write(f"Starting import of regions from {csv_file_path}...")

        for index, row in df.iterrows():
            try:
                name = row["name"]
                wkt_geometry = row["geometry"]

                if not isinstance(wkt_geometry, str) or not wkt_geometry.strip():
                    self.stderr.write(
                        self.style.ERROR(
                            f"Row {index+2}: Skipping region '{name}' due to missing geometry."
                        )
                    )
                    continue

                parsed_geometry = GEOSGeometry(wkt_geometry, srid=4326)

                # --- FIX: Check geometry type and convert if necessary ---
                if isinstance(parsed_geometry, Polygon):
                    # If it's a Polygon, wrap it in a MultiPolygon before saving.
                    geometry_to_save = MultiPolygon(parsed_geometry)
                elif isinstance(parsed_geometry, MultiPolygon):
                    # If it's already a MultiPolygon, use it as is.
                    geometry_to_save = parsed_geometry
                else:
                    self.stderr.write(
                        self.style.ERROR(
                            f"Row {index+2}: Geometry for '{name}' is not a Polygon or MultiPolygon. Skipping."
                        )
                    )
                    continue
                # --------------------------------------------------------

                Region.objects.update_or_create(
                    name=name, defaults={"geometry": geometry_to_save}
                )

            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(f"Error processing row {index+2}: {e}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Region import complete. Total regions in DB: {Region.objects.count()}"
            )
        )
