import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import (
    GEOSGeometry,
    Polygon,
    MultiPolygon,
)  # Import Polygon, MultiPolygon
from django.contrib.gis.geos.error import GEOSException
from uxo_records.models import UXORecord
from django.db import transaction


class Command(BaseCommand):
    help = "Imports UXO data from a CSV file into the database. Each row becomes a UXORecord with its own geometry."

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file_path", type=str, help="The path to the CSV file to import."
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing UXORecord data before importing.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        csv_file_path = options["csv_file_path"]
        clear_data = options["clear"]

        if clear_data:
            self.stdout.write(self.style.WARNING("Clearing existing UXORecord data..."))
            UXORecord.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Existing UXORecord data cleared."))

        try:
            df = pd.read_csv(csv_file_path)
        except FileNotFoundError:
            raise CommandError(f'Error: CSV file not found at "{csv_file_path}"')
        except Exception as e:
            raise CommandError(f"Error reading CSV file: {e}")

        self.stdout.write(f"Starting import of UXO records from {csv_file_path}...")
        records_created_count = 0
        records_failed_count = 0  # To count records that couldn't be created

        expected_columns = [
            "region",
            "geometry",
            "environmental_conditions",
            "ordnance_type",
            "burial_depth_cm",
            "ordnance_condition",
            "ordnance_age",
            "population_estimate",
            "uxo_count",
        ]
        for col in expected_columns:
            if col not in df.columns:
                raise CommandError(
                    f"Error: Missing expected column '{col}' in CSV file."
                )

        for index, row in df.iterrows():
            try:
                region_name_csv = str(row["region"]) if pd.notna(row["region"]) else ""
                wkt_geometry_csv = (
                    str(row["geometry"]) if pd.notna(row["geometry"]) else None
                )

                geometry_obj_for_model = None  # Initialize

                if wkt_geometry_csv:
                    try:
                        # Ensure wkt_geometry_csv is a string before parsing
                        if not isinstance(wkt_geometry_csv, str):
                            self.stderr.write(
                                self.style.WARNING(
                                    f"Geometry for region '{region_name_csv}' at CSV row {index+2} is not a string: '{wkt_geometry_csv}'. Record will be created without geometry."
                                )
                            )
                        else:
                            parsed_geometry = GEOSGeometry(wkt_geometry_csv, srid=4326)

                            # CRUCIAL FIX: Wrap Polygon in MultiPolygon if needed
                            if isinstance(parsed_geometry, Polygon):
                                geometry_obj_for_model = MultiPolygon(
                                    parsed_geometry, srid=4326
                                )
                            elif isinstance(parsed_geometry, MultiPolygon):
                                geometry_obj_for_model = parsed_geometry
                            else:
                                # Handle cases where geometry is valid WKT but not Polygon or MultiPolygon (e.g. Point, LineString)
                                self.stderr.write(
                                    self.style.WARNING(
                                        f"Parsed geometry for region '{region_name_csv}' at CSV row {index+2} is a {type(parsed_geometry)}, not Polygon or MultiPolygon. Record will be created without geometry."
                                    )
                                )
                                # geometry_obj_for_model remains None

                    except GEOSException as e:
                        self.stderr.write(
                            self.style.ERROR(
                                f"GEOS Error parsing WKT geometry for record in region '{region_name_csv}' at CSV row {index+2}: {e}. WKT: '{str(wkt_geometry_csv)[:100]}...' Record will be created without geometry."
                            )
                        )
                    except (
                        ValueError,
                        TypeError,
                    ) as e:  # Catch errors if WKT is fundamentally malformed
                        self.stderr.write(
                            self.style.ERROR(
                                f"Invalid WKT string format for record in region '{region_name_csv}' at CSV row {index+2}: {e}. WKT: '{str(wkt_geometry_csv)[:100]}...' Record will be created without geometry."
                            )
                        )
                    except (
                        Exception
                    ) as e:  # Catch any other unexpected errors during geometry parsing
                        self.stderr.write(
                            self.style.ERROR(
                                f"Unexpected error creating geometry for record in region '{region_name_csv}' at CSV row {index+2}: {e}. WKT: '{str(wkt_geometry_csv)[:100]}...' Record will be created without geometry."
                            )
                        )
                else:
                    self.stderr.write(
                        self.style.WARNING(
                            f"Missing geometry for record in region '{region_name_csv}' at CSV row {index+2}. Record will be created without geometry."
                        )
                    )

                # Create the UXORecord object
                # The danger_score will be calculated by the pre_save signal
                UXORecord.objects.create(
                    region=region_name_csv,
                    geometry=geometry_obj_for_model,  # Assign the (potentially wrapped) GEOSGeometry object
                    environmental_conditions=(
                        str(row["environmental_conditions"])
                        if pd.notna(row["environmental_conditions"])
                        else ""
                    ),
                    ordnance_type=(
                        str(row["ordnance_type"])
                        if pd.notna(row["ordnance_type"])
                        else ""
                    ),
                    burial_depth_cm=(
                        str(row["burial_depth_cm"])
                        if pd.notna(row["burial_depth_cm"])
                        else ""
                    ),
                    ordnance_condition=(
                        str(row["ordnance_condition"])
                        if pd.notna(row["ordnance_condition"])
                        else ""
                    ),
                    ordnance_age=(
                        str(row["ordnance_age"])
                        if pd.notna(row["ordnance_age"])
                        else ""
                    ),
                    population_estimate=(
                        int(row["population_estimate"])
                        if pd.notna(row["population_estimate"])
                        else 0
                    ),
                    uxo_count=(
                        str(row["uxo_count"]) if pd.notna(row["uxo_count"]) else ""
                    ),
                )
                records_created_count += 1

            except (
                Exception
            ) as e:  # Catch any error during the creation of a single UXORecord
                records_failed_count += 1
                self.stderr.write(
                    self.style.ERROR(
                        f"FATAL error processing CSV row {index+2} for region '{row.get('region', 'N/A')}': {e}. Skipping this record."
                    )
                )

        self.stdout.write(self.style.SUCCESS(f"\nImport complete."))
        self.stdout.write(f"UXO Records successfully created: {records_created_count}")
        if records_failed_count > 0:
            self.stdout.write(
                self.style.ERROR(
                    f"UXO Records failed to create due to errors: {records_failed_count}"
                )
            )
        self.stdout.write(
            self.style.NOTICE(
                "Danger scores for records should have been calculated automatically by signals"
            )
        )
