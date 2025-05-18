# danger_score/models.py
from django.db.models.signals import pre_save
from django.dispatch import receiver
from uxo_records.models import UXORecord
from danger_score.calculators.danger_score_logic import calculate_danger_score


@receiver(pre_save, sender=UXORecord)
def assign_danger_score(sender, instance, **kwargs):
    try:
        # Handle ordnance_age
        age_str = instance.ordnance_age
        age = float(age_str.split("–")[0]) if "–" in age_str else float(age_str)

        # Handle uxo_count
        uxo_str = instance.uxo_count
        try:
            uxo_count = (
                float(uxo_str.split("–")[0]) if "–" in uxo_str else float(uxo_str)
            )
        except ValueError:
            # Fallback mapping for descriptive text
            descriptive_map = {
                "High density cluster munition remnants": 100,
                "Medium density cluster munition remnants": 50,
                "Low density cluster munition remnants": 10,
            }
            uxo_count = descriptive_map.get(uxo_str.strip(), 0)

        instance.danger_score = calculate_danger_score(
            munition_type=instance.ordnance_type,
            uxo_count=uxo_count,
            burial_depth_cm=instance.burial_depth_cm,
            ordnance_age=age,
            population_estimate=instance.population_estimate,
            environment=instance.environmental_conditions,
            ordnance_condition=instance.ordnance_condition,
        )
    except Exception as e:
        print(f"Could not calculate danger score: {e}")
