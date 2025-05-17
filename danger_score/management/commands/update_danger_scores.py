from django.core.management.base import BaseCommand
from uxo_records.models import UXORecord
from danger_score.calculators.danger_score_logic import calculate_danger_score
import re


def average_from_range(value: str) -> float:
    """
    If value is like '40-70', return average as float.
    If not parsable, raise ValueError.
    """
    try:
        numbers = [int(num) for num in re.findall(r"\d+", value)]
        if len(numbers) == 2:
            return sum(numbers) / 2
        elif len(numbers) == 1:
            return float(numbers[0])
        else:
            raise ValueError(f"No numeric values found in '{value}'")
    except Exception as e:
        raise ValueError(f"Invalid value '{value}': {e}")


class Command(BaseCommand):
    help = "Batch update danger_score field for all UXO records"

    def handle(self, *args, **options):
        records = UXORecord.objects.all()
        updated_count = 0
        skipped = 0

        for record in records:
            try:
                burial_depth = average_from_range(record.burial_depth_cm)
                age = average_from_range(record.ordnance_age)

                score = calculate_danger_score(
                    munition_type=record.ordnance_type,
                    quantity=1,
                    burial_depth=burial_depth,
                    ordnance_age=age,
                    population_estimate=record.population_estimate,
                    environment=record.environmental_conditions,
                    ordnance_condition=record.ordnance_condition,
                )
                record.danger_score = score
                record.save()
                updated_count += 1

            except Exception as e:
                self.stderr.write(f"Skipped record {record.id} - {e}")
                skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully updated danger_score for {updated_count} records. Skipped: {skipped}"
            )
        )
