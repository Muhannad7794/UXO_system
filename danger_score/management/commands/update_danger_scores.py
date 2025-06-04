# danger_score/management/commands/update_danger_scores.py

from django.core.management.base import BaseCommand
from uxo_records.models import UXORecord
from django.db import transaction

# Removed imports for:
# - calculate_danger_score (will be called by the signal)
# - pre_save, receiver (signal is defined in uxo_records.signals)
# - extract_numeric_start (parsing is handled by the signal)


class Command(BaseCommand):
    help = "Recalculate and update the danger_score field for all existing UXORecord objects by re-saving them, which triggers the pre_save signal."

    def add_arguments(self, parser):
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1000,
            help="Process records in batches of this size to manage memory.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        batch_size = options["batch_size"]
        updated_count = 0
        skipped_count = 0
        total_records = UXORecord.objects.count()

        if total_records == 0:
            self.stdout.write(self.style.NOTICE("No UXO records found to update."))
            return

        self.stdout.write(
            f"Starting update of danger_score for {total_records} UXO records..."
        )

        # Iterate over records in batches to manage memory for large datasets
        queryset = UXORecord.objects.all()
        for i in range(0, total_records, batch_size):
            batch = queryset[i : i + batch_size]
            for record in batch:
                try:
                    # Simply saving the record will trigger the pre_save signal
                    # in uxo_records/signals.py, which contains the logic
                    # to parse necessary fields and call calculate_danger_score.
                    # The signal will then update instance.danger_score before actual save.
                    record.save()  # This triggers the signal in uxo_records.signals
                    updated_count += 1
                    if updated_count % 100 == 0:  # Print progress every 100 records
                        self.stdout.write(
                            f"Processed {updated_count}/{total_records} records..."
                        )
                except Exception as e:
                    skipped_count += 1
                    self.stderr.write(
                        self.style.ERROR(
                            f"Error updating record {record.id}: {e}. Skipping."
                        )
                    )
            self.stdout.write(f"Batch {i//batch_size + 1} processed.")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSuccessfully triggered score update for {updated_count} records."
            )
        )
        if skipped_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"Skipped {skipped_count} records due to errors during save."
                )
            )


# The duplicate @receiver(pre_save, sender=UXORecord) signal handler
# that was previously here has been REMOVED.
# The authoritative signal for calculating UXORecord.danger_score
# should be in uxo_records/signals.py.
