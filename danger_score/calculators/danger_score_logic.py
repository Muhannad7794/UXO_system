# danger_score/calculators/danger_score_logic.py

from typing import Optional
from uxo_records.models import UXORecord

# --- NORMALIZATION MAPPING TABLES ---
# These tables map the categorical choices from the UXORecord model to a normalized
# numeric score between 0.0 and 1.0.

# Threat Parameter: Ordnance Type Scores
ORDNANCE_TYPE_SCORES = {
    UXORecord.OrdnanceType.IED: 1.0,  # Improvised devices are highly unpredictable and dangerous.
    UXORecord.OrdnanceType.SUBMUNITION: 0.9,  # Often unstable and designed for anti-personnel/area denial.
    UXORecord.OrdnanceType.LANDMINE: 0.9,  # Designed to be victim-activated.
    UXORecord.OrdnanceType.AIRCRAFT_BOMB: 0.8,  # High explosive yield.
    UXORecord.OrdnanceType.ROCKET: 0.7,  # High explosive/fragmentation potential.
    UXORecord.OrdnanceType.ARTILLERY: 0.7,  # High explosive/fragmentation potential.
    UXORecord.OrdnanceType.MORTAR: 0.6,  # Common, but generally lower yield than artillery.
    UXORecord.OrdnanceType.OTHER: 0.3,  # Default for other, less common types.
}

# Threat Parameter: Ordnance Condition Scores
ORDNANCE_CONDITION_SCORES = {
    UXORecord.OrdnanceCondition.LEAKING: 1.0,  # Indicates unstable and potentially volatile filler.
    UXORecord.OrdnanceCondition.DAMAGED: 0.8,  # Damaged fuzing or casing increases unpredictability.
    UXORecord.OrdnanceCondition.CORRODED: 0.6,  # Corrosion can make the item more sensitive.
    UXORecord.OrdnanceCondition.INTACT: 0.2,  # Item is in a relatively stable state.
}

# Threat Parameter: Burial Status Scores
BURIAL_STATUS_SCORES = {
    UXORecord.BurialStatus.EXPOSED: 1.0,  # Highest trip/detonation hazard and accessibility.
    UXORecord.BurialStatus.PARTIAL: 0.8,  # Partially exposed.
    UXORecord.BurialStatus.CONCEALED: 0.5,  # Concealed by vegetation/debris.
    UXORecord.BurialStatus.BURIED: 0.2,  # Lowest immediate hazard from direct interaction.
}

# Vulnerability Parameter: Proximity Scores
PROXIMITY_SCORES = {
    UXORecord.ProximityStatus.IMMEDIATE: 1.0,  # Immediate danger to human life/infrastructure.
    UXORecord.ProximityStatus.NEAR: 0.6,  # Near populated areas.
    UXORecord.ProximityStatus.REMOTE: 0.2,  # Remote from civilians.
}


def calculate_danger_score(record: UXORecord) -> Optional[float]:
    """
    Calculates the danger score for a given UXORecord instance based on the
    new methodology: Risk = f(Threat, Vulnerability).
    """
    # This check is the primary safety mechanism.
    if not isinstance(record, UXORecord):
        return None

    # --- 1. NORMALIZE PARAMETERS ---
    # Safely get the numeric score for each parameter using .get() with a default value.
    ordnance_type_score = ORDNANCE_TYPE_SCORES.get(record.ordnance_type, 0.0)
    condition_score = ORDNANCE_CONDITION_SCORES.get(record.ordnance_condition, 0.0)
    burial_status_score = BURIAL_STATUS_SCORES.get(record.burial_status, 0.0)
    proximity_score = PROXIMITY_SCORES.get(record.proximity_to_civilians, 0.0)
    is_loaded_score = 1.0 if record.is_loaded else 0.2

    # --- 2. CALCULATE SUB-SCORES (THREAT & VULNERABILITY) ---
    threat_weights = {
        "ordnance_type": 0.4,
        "condition": 0.3,
        "is_loaded": 0.2,
        "burial_status": 0.1,
    }
    threat_score = (
        (ordnance_type_score * threat_weights["ordnance_type"])
        + (condition_score * threat_weights["condition"])
        + (is_loaded_score * threat_weights["is_loaded"])
        + (burial_status_score * threat_weights["burial_status"])
    )
    vulnerability_score = proximity_score

    # --- 3. CALCULATE THE FINAL DANGER SCORE ---
    final_weights = {"threat": 0.6, "vulnerability": 0.4}
    danger_score = (threat_score * final_weights["threat"]) + (
        vulnerability_score * final_weights["vulnerability"]
    )

    return round(danger_score, 4)
