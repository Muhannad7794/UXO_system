# uxo_records/signals.py
from django.db.models.signals import pre_save
from django.dispatch import receiver
from uxo_records.models import UXORecord
from danger_score.calculators.danger_score_logic import calculate_danger_score


def parse_range_string(value):
    """Convert a 'min-max' string to float average."""
    if isinstance(value, str) and "-" in value:
        try:
            parts = value.split("-")
            parts = [float(p.strip()) for p in parts]
            return sum(parts) / len(parts)
        except Exception:
            return None
    try:
        return float(value)
    except Exception:
        return None


@receiver(pre_save, sender=UXORecord)
def compute_danger_score(sender, instance, **kwargs):
    try:
        burial_depth = parse_range_string(instance.burial_depth_cm)
        ordnance_age = parse_range_string(instance.ordnance_age)

        instance.danger_score = calculate_danger_score(
            munition_type=instance.ordnance_type,
            quantity=1,  # default or placeholder if quantity isn't modeled
            burial_depth=burial_depth or 0,
            ordnance_age=ordnance_age or 0,
            population_estimate=instance.population_estimate or 0,
            environment=instance.environmental_conditions,
            ordnance_condition=instance.ordnance_condition,
        )
    except Exception as e:
        print(f"[Signal] Failed to compute danger_score: {e}")
        instance.danger_score = None
