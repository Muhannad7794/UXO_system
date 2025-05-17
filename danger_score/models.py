# danger_score/models.py
from django.db.models.signals import pre_save
from django.dispatch import receiver
from uxo_records.models import UXORecord
from danger_score.calculators.danger_score_logic import calculate_danger_score


@receiver(pre_save, sender=UXORecord)
def assign_danger_score(sender, instance, **kwargs):
    try:
        # Convert burial depth and age from string to float, stripping ranges like "11–13"
        burial_depth = float(instance.burial_depth_cm.split("–")[0])
        age = float(instance.ordnance_age.split("–")[0])
        quantity = 1  # Optional: Add quantity support later

        instance.danger_score = calculate_danger_score(
            munition_type=instance.ordnance_type,
            quantity=quantity,
            burial_depth=burial_depth,
            ordnance_age=age,
            population_estimate=instance.population_estimate,
            environment=instance.environmental_conditions,
            ordnance_condition=instance.ordnance_condition,
        )
    except Exception as e:
        print(f"Could not calculate danger score: {e}")
