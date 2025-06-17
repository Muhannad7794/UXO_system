# reports/utils.py

from django.db.models import Case, When, Value, FloatField, Func

from uxo_records.models import UXORecord

# --- NORMALIZATION MAPPING DICTIONARIES ---
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

# --- ANNOTATION MAP ---
# This dictionary maps the desired annotated field name to its source field
# and its corresponding numeric mapping dictionary.
ANNOTATION_MAP = {
    "ordnance_type_numeric": ("ordnance_type", ORDNANCE_TYPE_NUMERIC),
    "ordnance_condition_numeric": ("ordnance_condition", ORDNANCE_CONDITION_NUMERIC),
    "burial_status_numeric": ("burial_status", BURIAL_STATUS_NUMERIC),
    "proximity_to_civilians_numeric": ("proximity_to_civilians", PROXIMITY_NUMERIC),
    "is_loaded_numeric": ("is_loaded", IS_LOADED_NUMERIC),
}


def get_annotated_uxo_queryset():
    """
    Returns the base UXORecord queryset with added 'virtual' numeric fields
    for all major categorical attributes AND extracts latitude/longitude
    from the location PointField.
    """
    queryset = UXORecord.objects.all()
    annotations = {}

    # Using ANNOTATION_MAP for cleaner, more maintainable code
    for numeric_field, (source_field, mapping) in ANNOTATION_MAP.items():
        cases = [
            When(**{source_field: key}, then=Value(val)) for key, val in mapping.items()
        ]
        annotations[numeric_field] = Case(
            *cases, default=Value(0.0), output_field=FloatField()
        )

    # --- Use Func() for version-agnostic coordinate extraction ---
    # This directly calls the database's ST_X and ST_Y functions on the PointField.
    # It avoids version-specific import paths for the X and Y helper classes.
    annotations["longitude"] = Func(
        "location", function="ST_X", output_field=FloatField()
    )
    annotations["latitude"] = Func(
        "location", function="ST_Y", output_field=FloatField()
    )

    return queryset.annotate(**annotations)
