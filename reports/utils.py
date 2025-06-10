from django.db.models import Case, When, Value, FloatField
from uxo_records.models import UXORecord

# --- NORMALIZATION MAPPING DICTIONARIES (from your danger_score_logic) ---
# We define the numeric value for each category.

ORDNANCE_TYPE_NUMERIC = {
    UXORecord.OrdnanceType.IED: 1.0,
    UXORecord.OrdnanceType.SUBMUNITION: 0.9,
    UXORecord.OrdnanceType.LANDMINE: 0.9,
    UXORecord.OrdnanceType.AIRCRAFT_BOMB: 0.8,
    UXORecord.OrdnanceType.ROCKET: 0.7,
    UXORecord.OrdnanceType.ARTILLERY: 0.7,
    UXORecord.OrdnanceType.MORTAR: 0.6,
    UXORecord.OrdnanceType.OTHER: 0.3,
}

ORDNANCE_CONDITION_NUMERIC = {
    UXORecord.OrdnanceCondition.LEAKING: 1.0,
    UXORecord.OrdnanceCondition.DAMAGED: 0.8,
    UXORecord.OrdnanceCondition.CORRODED: 0.6,
    UXORecord.OrdnanceCondition.INTACT: 0.2,
}

BURIAL_STATUS_NUMERIC = {
    UXORecord.BurialStatus.EXPOSED: 1.0,
    UXORecord.BurialStatus.PARTIAL: 0.8,
    UXORecord.BurialStatus.CONCEALED: 0.5,
    UXORecord.BurialStatus.BURIED: 0.2,
}

PROXIMITY_NUMERIC = {
    UXORecord.ProximityStatus.IMMEDIATE: 1.0,
    UXORecord.ProximityStatus.NEAR: 0.6,
    UXORecord.ProximityStatus.REMOTE: 0.2,
}

IS_LOADED_NUMERIC = {True: 1.0, False: 0.2}


def get_annotated_uxo_queryset():
    """
    Returns the base UXORecord queryset with added 'virtual' numeric fields
    for all major categorical attributes, enabling advanced statistical analysis.
    """
    queryset = UXORecord.objects.all()

    # Create a list of 'When' conditions for each categorical field
    ordnance_type_cases = [
        When(ordnance_type=key, then=Value(val))
        for key, val in ORDNANCE_TYPE_NUMERIC.items()
    ]
    condition_cases = [
        When(ordnance_condition=key, then=Value(val))
        for key, val in ORDNANCE_CONDITION_NUMERIC.items()
    ]
    burial_cases = [
        When(burial_status=key, then=Value(val))
        for key, val in BURIAL_STATUS_NUMERIC.items()
    ]
    proximity_cases = [
        When(proximity_to_civilians=key, then=Value(val))
        for key, val in PROXIMITY_NUMERIC.items()
    ]
    is_loaded_cases = [
        When(is_loaded=key, then=Value(val)) for key, val in IS_LOADED_NUMERIC.items()
    ]

    # Annotate the queryset with the new numeric fields
    annotated_queryset = queryset.annotate(
        ordnance_type_numeric=Case(
            *ordnance_type_cases, default=Value(0.0), output_field=FloatField()
        ),
        ordnance_condition_numeric=Case(
            *condition_cases, default=Value(0.0), output_field=FloatField()
        ),
        burial_status_numeric=Case(
            *burial_cases, default=Value(0.0), output_field=FloatField()
        ),
        proximity_to_civilians_numeric=Case(
            *proximity_cases, default=Value(0.0), output_field=FloatField()
        ),
        is_loaded_numeric=Case(
            *is_loaded_cases, default=Value(0.0), output_field=FloatField()
        ),
    )

    return annotated_queryset
