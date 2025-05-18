# uxo_records/signals.py
from django.db.models.signals import pre_save
from django.dispatch import receiver
from uxo_records.models import UXORecord
from danger_score.calculators.danger_score_logic import calculate_danger_score
from danger_score.utils.parsing import extract_numeric_start


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
def assign_danger_score(sender, instance, **kwargs):
    try:
        burial_depth = extract_numeric_start(instance.burial_depth_cm)
        ordnance_age = extract_numeric_start(instance.ordnance_age)
        uxo_count = extract_numeric_start(
            instance.uxo_count,
            fallback_map={
                "High density cluster munition remnants": 100,
                "Widespread landmine contamination": 80,
                "UXO hotspot (quantity not stated)": 60,
                "Estimated contamination (Baghouz-level)": 90,
            },
        )

        instance.danger_score = calculate_danger_score(
            munition_type=instance.ordnance_type,
            uxo_count=uxo_count,
            burial_depth_cm=burial_depth,
            ordnance_age=ordnance_age,
            population_estimate=instance.population_estimate,
            environment=instance.environmental_conditions,
            ordnance_condition=instance.ordnance_condition,
        )
    except Exception as e:
        print(f"Could not calculate danger score: {e}")
