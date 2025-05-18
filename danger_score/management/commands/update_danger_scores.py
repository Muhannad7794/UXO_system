# danger_score/management/commands/update_danger_scores.py
from danger_score.calculators.danger_score_logic import calculate_danger_score
from django.db.models.signals import pre_save
from django.dispatch import receiver
from uxo_records.models import UXORecord
from danger_score.utils.parsing import extract_numeric_start
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Update danger_score field for all existing UXO records"

    def handle(self, *args, **kwargs):
        updated = 0
        skipped = 0

        for record in UXORecord.objects.all():
            try:
                burial_depth = extract_numeric_start(record.burial_depth_cm)
                ordnance_age = extract_numeric_start(record.ordnance_age)
                uxo_count = extract_numeric_start(
                    record.uxo_count,
                    fallback_map={
                        "High density cluster munition remnants": 100,
                        "Widespread landmine contamination": 80,
                        "UXO hotspot (quantity not stated)": 60,
                        "Estimated contamination (Baghouz-level)": 90,
                    },
                )

                score = calculate_danger_score(
                    munition_type=record.ordnance_type,
                    uxo_count=uxo_count,
                    burial_depth_cm=burial_depth,
                    ordnance_age=ordnance_age,
                    population_estimate=record.population_estimate,
                    environment=record.environmental_conditions,
                    ordnance_condition=record.ordnance_condition,
                )

                record.danger_score = score
                record.save()
                updated += 1

            except Exception as e:
                skipped += 1
                print(f"Skipped record {record.id} - {e}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully updated danger_score for {updated} records. Skipped: {skipped}"
            )
        )


@receiver(pre_save, sender=UXORecord)
def assign_danger_score(sender, instance, **kwargs):
    try:
        fallback_map = {
            "High density cluster munition remnants": 100,
            "Medium density cluster munition remnants": 50,
            "Low density cluster munition remnants": 10,
            "UXO hotspot (quantity not stated)": 50,
            "Widespread landmine contamination": 75,
            "Estimated contamination (Baghouz-level)": 90,
        }

        age = extract_numeric_start(instance.ordnance_age)
        uxo_count = extract_numeric_start(instance.uxo_count, fallback_map)

        instance.danger_score = calculate_danger_score(
            munition_type=instance.ordnance_type,
            uxo_count=uxo_count,
            burial_depth_cm=extract_numeric_start(instance.burial_depth_cm),
            ordnance_age=age,
            population_estimate=instance.population_estimate,
            environment=instance.environmental_conditions,
            ordnance_condition=instance.ordnance_condition,
        )

    except Exception as e:
        print(f"Could not calculate danger score: {e}")
