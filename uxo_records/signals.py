# uxo_records/signals.py

from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import UXORecord
from danger_score.calculators import danger_score_logic


@receiver(pre_save, sender=UXORecord)
def assign_danger_score_to_uxo_record(sender, instance, **kwargs):
    """
    A pre-save signal that automatically calculates the danger_score
    for a UXORecord instance before it is saved to the database.
    """
    try:
        # Pass the instance directly to the new, updated danger score calculator
        calculated_score = danger_score_logic.calculate_danger_score(instance)
        instance.danger_score = calculated_score
    except Exception as e:
        # If calculation fails for any reason, set the score to None
        # and print an error to the console for debugging.
        print(
            f"Error calculating danger score for UXORecord (ID: {instance.id or 'New'}): {e}"
        )
        instance.danger_score = None
