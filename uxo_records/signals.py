# uxo_records/signals.py
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import UXORecord
from danger_score.calculators.danger_score_logic import calculate_danger_score
# Use the (potentially renamed) improved parsing function
from danger_score.utils.parsing import extract_numeric_value as parse_value_to_numerical

@receiver(pre_save, sender=UXORecord)
def assign_danger_score_to_uxo_record(sender, instance, **kwargs):
    """
    Calculates and assigns the danger_score to the UXORecord instance
    before it is saved.
    """
    try:
        # Use the improved parsing function
        burial_depth = parse_value_to_numerical(instance.burial_depth_cm)
        ordnance_age = parse_value_to_numerical(instance.ordnance_age)
        uxo_count = parse_value_to_numerical(
            instance.uxo_count,
            fallback_map={
                "High density cluster munition remnants": 100.0, # Use floats for consistency
                "Widespread landmine contamination": 80.0,
                "UXO hotspot (quantity not stated)": 60.0,
                "Estimated contamination (Baghouz-level)": 90.0,
                # Add other text descriptions from your CSV if they map to uxo_count
            }
        )

        # If any critical numeric input could not be parsed,
        # it might be best to not calculate a score or ensure calculate_danger_score handles None.
        # For now, we'll let calculate_danger_score handle None if it can,
        # or it will raise an error which the except block will catch.
        # A more robust approach might be:
        # if burial_depth is None or ordnance_age is None or uxo_count is None:
        #     instance.danger_score = None # Or a default "unable to calculate" score
        #     print(f"Cannot calculate danger score for UXORecord {instance.id if instance.id else 'New'} due to unparseable inputs.")
        #     return # Exit the signal handler

        calculated_score = calculate_danger_score(
            munition_type=instance.ordnance_type,
            uxo_count=uxo_count,
            burial_depth_cm=burial_depth,
            ordnance_age=ordnance_age,
            population_estimate=instance.population_estimate, # This is already PositiveIntegerField
            environment=instance.environmental_conditions,
            ordnance_condition=instance.ordnance_condition,
        )
        instance.danger_score = calculated_score

    except Exception as e:
        print(f"Error in assign_danger_score_to_uxo_record (ID: {instance.id if instance.id else 'New'}): {e}")
        instance.danger_score = None # Ensure score is None if any error occurs
