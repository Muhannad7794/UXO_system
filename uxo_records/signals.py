# uxo_records/signals.py
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import UXORecord  # UXORecord now has 'danger_score' and 'geometry'
from danger_score.calculators.danger_score_logic import calculate_danger_score
from danger_score.utils.parsing import extract_numeric_start


# This utility function was in your original signals.py.
# If extract_numeric_start or calculate_danger_score handles range parsing,
# this might be redundant or could be moved to a shared utils module.
# For now, keeping it as per your provided structure.
def parse_range_string(value):
    """Convert a 'min-max' string to float average if applicable, else try float."""
    if isinstance(value, str) and "-" in value:
        try:
            parts = value.split("-")
            parts = [float(p.strip()) for p in parts]
            if len(parts) > 0:
                return sum(parts) / len(parts)
            return None  # Or handle as error
        except ValueError:  # Catch if parts are not convertible to float
            return None
        except Exception:  # Catch other potential errors
            return None
    try:
        return float(value)
    except (ValueError, TypeError):  # Catch if direct conversion to float fails
        return None
    except Exception:
        return None


@receiver(pre_save, sender=UXORecord)
def assign_danger_score_to_uxo_record(sender, instance, **kwargs):
    """
    Calculates and assigns the danger_score to the UXORecord instance
    before it is saved.
    """
    try:
        # Ensure all necessary fields are present on the instance
        # The extract_numeric_start function is expected to handle various string inputs
        # and return a numeric type or None.
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

        # Check if all required numeric inputs for calculation are valid
        # calculate_danger_score should be robust enough to handle None for some inputs if designed so.
        # If not, you might need more checks here.

        calculated_score = calculate_danger_score(
            munition_type=instance.ordnance_type,
            uxo_count=uxo_count,  # Should be numeric
            burial_depth_cm=burial_depth,  # Should be numeric
            ordnance_age=ordnance_age,  # Should be numeric
            population_estimate=instance.population_estimate,  # Already PositiveIntegerField
            environment=instance.environmental_conditions,
            ordnance_condition=instance.ordnance_condition,
        )
        instance.danger_score = calculated_score

    except Exception as e:
        # Log the error and potentially set a default or null danger_score
        print(
            f"Error calculating danger score for UXORecord (ID: {instance.id if instance.id else 'New'}): {e}"
        )
        # Depending on requirements, you might want to set instance.danger_score to None or a default error value
        instance.danger_score = None  # Example: set to None if calculation fails
