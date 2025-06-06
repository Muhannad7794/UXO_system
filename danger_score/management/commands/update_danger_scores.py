# danger_score/management/commands/update_danger_scores.py

from django.core.management.base import BaseCommand
from uxo_records.models import UXORecord
from danger_score.calculators.danger_score_logic import calculate_danger_score


class Command(BaseCommand):
    """
    Recalculates and updates the danger_score for all existing UXORecord objects.

    This command directly calls the danger score calculation logic for each record
    and uses 'bulk_update' for high efficiency, making it suitable for large datasets.
    It does NOT rely on triggering pre_save signals.
    """

    help = "Recalculate and update the danger_score field for all existing UXORecord objects efficiently."

    def add_arguments(self, parser):
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1000,
            help="Process records in batches of this size to manage memory.",
        )

    def handle(self, *args, **options):
        batch_size = options["batch_size"]
        total_records = UXORecord.objects.count()

        if total_records == 0:
            self.stdout.write(self.style.NOTICE("No UXO records found to update."))
            return

        self.stdout.write(
            f"Starting danger score update for {total_records} UXO records..."
        )

        updated_count = 0
        skipped_count = 0
        # Use .iterator() to process records in chunks, which is memory-efficient
        record_iterator = UXORecord.objects.all().iterator(chunk_size=batch_size)

        for batch_of_records in self.queryset_iterator(record_iterator, batch_size):
            records_to_update = []
            for record in batch_of_records:
                try:
                    # Directly call the calculation logic
                    new_score = calculate_danger_score(record)

                    # Update the score on the instance if it has changed
                    if record.danger_score != new_score:
                        record.danger_score = new_score
                        records_to_update.append(record)

                    updated_count += 1

                except Exception as e:
                    skipped_count += 1
                    self.stderr.write(
                        self.style.ERROR(
                            f"Error processing record {record.id}: {e}. Skipping."
                        )
                    )

            # Now, update the entire batch in a single database query
            if records_to_update:
                UXORecord.objects.bulk_update(records_to_update, ["danger_score"])

            self.stdout.write(f"Processed {updated_count}/{total_records} records...")

        self.stdout.write(self.style.SUCCESS("\nDanger score update complete."))
        self.stdout.write(
            self.style.SUCCESS(f"Successfully processed {updated_count} records.")
        )

        if skipped_count > 0:
            self.stdout.write(
                self.style.WARNING(f"Skipped {skipped_count} records due to errors.")
            )

    def queryset_iterator(self, iterator, batch_size):
        """
        A helper generator to yield batches of a specific size from an iterator.
        """
        batch = []
        for item in iterator:
            batch.append(item)
            if len(batch) == batch_size:
                yield batch
                batch = []
        if batch:
            yield batch
