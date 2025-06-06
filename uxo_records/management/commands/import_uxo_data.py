# uxo_records/management/commands/import_uxo_data.py
import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import Point
from django.db import transaction
from uxo_records.models import Region, UXORecord

# --- DATA MAPPING DICTIONARIES ---
# These maps translate human-readable strings from the CSV into the
# internal database representations used by the UXORecord model's `choices`.

ORDNANCE_TYPE_MAP = {
    "Artillery Projectile": UXORecord.OrdnanceType.ARTILLERY,
    "Mortar Bomb": UXORecord.OrdnanceType.MORTAR,
    "Rocket": UXORecord.OrdnanceType.ROCKET,
    "Aircraft Bomb": UXORecord.OrdnanceType.AIRCRAFT_BOMB,
    "Landmine": UXORecord.OrdnanceType.LANDMINE,
    "Submunition": UXORecord.OrdnanceType.SUBMUNITION,
    "Improvised Explosive Device": UXORecord.OrdnanceType.IED,
    "Other": UXORecord.OrdnanceType.OTHER,
}

ORDNANCE_CONDITION_MAP = {
    "Intact": UXORecord.OrdnanceCondition.INTACT,
    "Corroded": UXORecord.OrdnanceCondition.CORRODED,
    "Damaged/Deformed": UXORecord.OrdnanceCondition.DAMAGED,
    "Leaking/Exuding": UXORecord.OrdnanceCondition.LEAKING,
}

PROXIMITY_STATUS_MAP = {
    "Immediate (0-100m to civilians/infrastructure)": UXORecord.ProximityStatus.IMMEDIATE,
    "Near (101-500m)": UXORecord.ProximityStatus.NEAR,
    "Remote (>500m)": UXORecord.ProximityStatus.REMOTE,
}

BURIAL_STATUS_MAP = {
    "Exposed": UXORecord.BurialStatus.EXPOSED,
    "Partially Exposed": UXORecord.BurialStatus.PARTIAL,
    "Concealed (by vegetation/debris)": UXORecord.BurialStatus.CONCEALED,
    "Buried": UXORecord.BurialStatus.BURIED,
}


class Command(BaseCommand):
    help = (
        "Imports UXO incident data from a CSV file. Each row should represent a single "
        "UXO record with latitude and longitude. This command performs a spatial join "
        "to link each record to its administrative Region."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file_path", type=str, help="The path to the CSV file to import."
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing UXORecord data before importing. Does not affect Region data.",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1000,
            help="Process and insert records in batches of this size.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        csv_file_path = options["csv_file_path"]
        clear_data = options["clear"]
        batch_size = options["batch_size"]

        if clear_data:
            self.stdout.write(self.style.WARNING("Clearing existing UXORecord data..."))
            UXORecord.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Existing UXORecord data cleared."))

        if not Region.objects.exists():
            raise CommandError(
                "No Region data found. Please import region boundaries before importing UXO records."
            )

        try:
            df = pd.read_csv(csv_file_path).fillna("")
        except FileNotFoundError:
            raise CommandError(f'Error: CSV file not found at "{csv_file_path}"')
        except Exception as e:
            raise CommandError(f"Error reading CSV file: {e}")

        self.stdout.write(f"Validating columns in {csv_file_path}...")
        expected_columns = [
            "latitude",
            "longitude",
            "ordnance_type",
            "ordnance_condition",
            "is_loaded",
            "proximity_to_civilians",
            "burial_status",
        ]
        for col in expected_columns:
            if col not in df.columns:
                raise CommandError(
                    f"Error: Missing expected column '{col}' in CSV file."
                )

        self.stdout.write("Starting import of UXO records...")
        records_to_create = []
        failed_rows = []

        for index, row in df.iterrows():
            try:
                # 1. Create GIS Point Location
                lat = float(row["latitude"])
                lon = float(row["longitude"])
                location_point = Point(lon, lat, srid=4326)

                # 2. Perform Spatial Join to find the Region
                region = Region.objects.filter(
                    geometry__contains=location_point
                ).first()
                if not region:
                    raise ValueError(
                        "Could not find a corresponding Region for the given coordinates."
                    )

                # 3. Map CSV data to model choices
                ordnance_type = ORDNANCE_TYPE_MAP[row["ordnance_type"]]
                ordnance_condition = ORDNANCE_CONDITION_MAP[row["ordnance_condition"]]
                proximity_to_civilians = PROXIMITY_STATUS_MAP[
                    row["proximity_to_civilians"]
                ]
                burial_status = BURIAL_STATUS_MAP[row["burial_status"]]
                is_loaded = str(row["is_loaded"]).strip().lower() in [
                    "true",
                    "1",
                    "yes",
                ]

                # 4. Append a new UXORecord object to the batch list
                records_to_create.append(
                    UXORecord(
                        location=location_point,
                        region=region,
                        ordnance_type=ordnance_type,
                        ordnance_condition=ordnance_condition,
                        is_loaded=is_loaded,
                        proximity_to_civilians=proximity_to_civilians,
                        burial_status=burial_status,
                    )
                )

                # 5. If batch is full, create the records
                if len(records_to_create) == batch_size:
                    UXORecord.objects.bulk_create(records_to_create)
                    self.stdout.write(
                        f"Imported batch of {len(records_to_create)} records."
                    )
                    records_to_create = []

            except (ValueError, KeyError, TypeError) as e:
                failed_rows.append((index + 2, str(e)))  # CSV row number and error
            except Exception as e:
                failed_rows.append((index + 2, f"An unexpected error occurred: {e}"))

        # Create any remaining records in the last batch
        if records_to_create:
            UXORecord.objects.bulk_create(records_to_create)
            self.stdout.write(
                f"Imported final batch of {len(records_to_create)} records."
            )

        # --- FINAL REPORT ---
        self.stdout.write(self.style.SUCCESS("\nImport process complete."))
        total_created = (
            UXORecord.objects.count()
            if not clear_data
            else df.shape[0] - len(failed_rows)
        )
        self.stdout.write(f"Total UXO Records in database: {UXORecord.objects.count()}")

        if failed_rows:
            self.stdout.write(
                self.style.WARNING(
                    f"\nSkipped {len(failed_rows)} records due to errors:"
                )
            )
            for row_num, error in failed_rows[
                :10
            ]:  # Print details for the first 10 failures
                self.stderr.write(f"  - Row {row_num}: {error}")
            if len(failed_rows) > 10:
                self.stderr.write("  ...")

        self.stdout.write(
            self.style.NOTICE(
                "\nIMPORTANT: Danger scores have NOT been calculated automatically."
            )
        )
        self.stdout.write(
            self.style.NOTICE(
                "Run 'python manage.py update_danger_scores' to calculate scores for the imported records."
            )
        )
