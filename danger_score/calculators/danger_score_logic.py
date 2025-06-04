# danger_score/calculators/danger_score_logic.py
from typing import Optional, Union

# This value will be returned by normalization functions if their specific input is None or unparseable.
# It represents a neutral contribution from that factor.
NEUTRAL_NORMALIZED_SCORE_ON_NONE_INPUT = 0.0


def normalize_munition_type(munition_type: Optional[str]) -> float:
    if not isinstance(munition_type, str) or not munition_type.strip():
        return NEUTRAL_NORMALIZED_SCORE_ON_NONE_INPUT  # Or a specific score for "unknown type"
    mapping = {
        "Cluster Munition": 1.0,
        "Landmine": 0.9,
        "Artillery Shells": 0.8,
        "Mortars": 0.6,
        "Hand Grenades": 0.4,
        "Small Arms Ammunition": 0.2,
        "IEDs": 0.95,  # Added based on common high risk, adjust as needed
        # Add other types from your dataset if necessary
    }
    return mapping.get(
        munition_type.strip(), NEUTRAL_NORMALIZED_SCORE_ON_NONE_INPUT
    )  # Default for unknown types


def normalize_uxo_count(uxo_count: Optional[float]) -> float:
    if uxo_count is None:
        return NEUTRAL_NORMALIZED_SCORE_ON_NONE_INPUT
    # Ensure it's a float for comparison, though parse_value_to_numerical should provide this
    try:
        count = float(uxo_count)
    except (ValueError, TypeError):
        return NEUTRAL_NORMALIZED_SCORE_ON_NONE_INPUT

    if count > 100:
        return 1.0
    elif count > 50:
        return 0.7
    elif count > 10:
        return 0.5
    elif count >= 1:  # Includes 1
        return 0.2
    return 0.0  # For counts less than 1


def normalize_burial_depth_cm(depth_cm: Optional[float]) -> float:
    if depth_cm is None:
        return NEUTRAL_NORMALIZED_SCORE_ON_NONE_INPUT
    try:
        depth = float(depth_cm)
    except (ValueError, TypeError):
        return NEUTRAL_NORMALIZED_SCORE_ON_NONE_INPUT

    if depth <= 10:
        return 1.0
    elif depth <= 30:
        return 0.7
    elif depth <= 60:
        return 0.4
    return 0.2  # For depths > 60 cm


def normalize_ordnance_age(age_years: Optional[float]) -> float:
    if age_years is None:
        return NEUTRAL_NORMALIZED_SCORE_ON_NONE_INPUT
    try:
        age = float(age_years)
    except (ValueError, TypeError):
        return NEUTRAL_NORMALIZED_SCORE_ON_NONE_INPUT

    if age > 15:
        return 1.0
    elif age > 5:  # Covers 6-15 years
        return 0.6
    return 0.3  # For ages 0-5 years


def normalize_population_estimate(population: Optional[int]) -> float:
    if (
        population is None
    ):  # Should not happen if model field is PositiveIntegerField and not null
        return 0.1  # Default to lowest risk category if somehow None

    # Based on your initial methodology for population proxy
    if population > 1000000:  # Matching your example table
        return 1.0
    elif population > 500000:
        return 0.7
    elif population > 200000:
        return 0.5
    elif population > 100000:
        return 0.4
    elif population > 50000:
        return 0.3
    elif population > 10000:
        return 0.2
    return 0.1  # For populations <= 10000


def normalize_environment(env_condition: Optional[str]) -> float:
    if not isinstance(env_condition, str) or not env_condition.strip():
        return 0.5  # Default for unknown/empty environment

    # Ensure this map covers all unique values from your CSV or has a good default
    mapping = {
        "Sandy Soil": 0.8,
        "Clay Soil": 0.5,
        "Rocky Terrain": 0.3,
        "Wetlands": 0.7,
        "Humid Mediterranean coastal zone": 0.9,  # From your methodology doc
        "Flood-prone near Euphrates River": 0.8,  # From your methodology doc
        "Semi-arid agricultural land": 0.6,
        "Hilly agricultural": 0.7,
        "Coastal mountains": 0.4,
        "Desert plains": 0.2,
        "Mixed terrain": 0.5,
        "River valley and plains": 0.7,
        "Urban and surrounding plains": 0.8,
        "Agricultural plains": 0.6,
        "Southern plains": 0.6,
        "Riverine": 0.8,
        "Urban": 0.9,
        "Suburban/Agricultural": 0.7,
        "Rural Town": 0.6,
        "Golan Heights plateau": 0.3,
        "Volcanic plateau": 0.2,
        "Coastal plain": 0.7,
    }
    return mapping.get(env_condition.strip(), 0.5)  # Default for unmapped values


def normalize_ordnance_condition(condition: Optional[str]) -> float:
    if not isinstance(condition, str) or not condition.strip():
        return 0.5  # Default for unknown/empty condition
    mapping = {
        "Pristine": 0.3,
        "Corroded": 0.6,
        "Damaged": 0.9,
        "Leaking": 1.0,
    }
    return mapping.get(condition.strip(), 0.5)  # Default for unmapped values


def calculate_danger_score(
    munition_type: Optional[str],
    burial_depth_cm: Optional[float],  # Expecting float or None from parsing
    ordnance_age: Optional[float],  # Expecting float or None from parsing
    population_estimate: Optional[
        int
    ],  # Expecting int or None (though model field is PositiveInt)
    environment: Optional[str],
    ordnance_condition: Optional[str],
    uxo_count: Optional[float],  # Expecting float or None from parsing
) -> Optional[float]:  # Can return None if score cannot be reliably calculated

    # Define which parameters are absolutely critical. If these are None,
    # we might decide the score is indeterminable and return None.
    # For this example, let's assume munition_type is critical.
    # uxo_count, burial_depth, and ordnance_age will use NEUTRAL_NORMALIZED_SCORE_ON_NONE_INPUT
    # if they are None, allowing a score to still be computed.

    if munition_type is None or not str(munition_type).strip():
        # If munition type is unknown, we cannot reliably score.
        # You could also assign a high penalty if preferred.
        print(
            f"Warning: Munition type is None or empty. Cannot calculate danger score."
        )
        return None

    weights = {
        "munition_type": 0.20,
        "uxo_count": 0.14,
        "burial_depth_cm": 0.10,
        "ordnance_age": 0.02,
        "population_estimate": 0.30,
        "environment": 0.04,
        "ordnance_condition": 0.20,
    }

    try:
        norm_munition = normalize_munition_type(munition_type)
        norm_uxo_count = normalize_uxo_count(uxo_count)
        norm_burial_depth = normalize_burial_depth_cm(burial_depth_cm)
        norm_ordnance_age = normalize_ordnance_age(ordnance_age)
        norm_population = normalize_population_estimate(population_estimate)
        norm_environment = normalize_environment(environment)
        norm_ordnance_condition = normalize_ordnance_condition(ordnance_condition)

        # Check if any critical normalization failed in a way that should invalidate the score
        # For instance, if normalize_munition_type returned the neutral score because the type was unknown,
        # you might decide the overall score is invalid.
        # For now, we proceed with the sum.

        score_components = [
            norm_munition * weights["munition_type"],
            norm_uxo_count * weights["uxo_count"],
            norm_burial_depth * weights["burial_depth_cm"],
            norm_ordnance_age * weights["ordnance_age"],
            norm_population * weights["population_estimate"],
            norm_environment * weights["environment"],
            norm_ordnance_condition * weights["ordnance_condition"],
        ]

        # Ensure all components are numbers before summing
        if any(
            comp is None for comp in score_components
        ):  # Should not happen if normalizers return floats
            print(
                f"Warning: A normalized component is None. Cannot calculate danger score."
            )
            return None

        total_score = sum(score_components)
        return round(total_score, 3)

    except TypeError as e:
        # This is a fallback, but the individual normalizers should prevent TypeErrors now.
        print(
            f"TypeError during final danger score calculation: {e}. Inputs: munition_type='{munition_type}', uxo_count={uxo_count}, burial_depth={burial_depth_cm}, age={ordnance_age}"
        )
        return None
    except Exception as e:
        print(f"Unexpected error during final danger score calculation: {e}")
        return None
