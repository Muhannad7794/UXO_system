# danger_score/calculators/danger_score_logic.py
from typing import Optional


def normalize_munition_type(munition_type: str) -> float:
    mapping = {
        "Cluster Munition": 1.0,
        "Landmine": 0.9,
        "Artillery Shells": 0.8,
        "Mortars": 0.6,
        "Hand Grenades": 0.4,
        "Small Arms Ammunition": 0.2,
    }
    return mapping.get(munition_type, 0.0)


def normalize_uxo_count(uxo_count: float) -> float:
    if uxo_count > 100:
        return 1.0
    elif uxo_count > 50:
        return 0.7
    elif uxo_count > 10:
        return 0.5
    elif uxo_count >= 1:
        return 0.2
    return 0.0


def normalize_burial_depth_cm(depth_cm: float) -> float:
    if depth_cm <= 10:
        return 1.0
    elif depth_cm <= 30:
        return 0.7
    elif depth_cm <= 60:
        return 0.4
    return 0.2


def normalize_ordnance_age(age_years: float) -> float:
    if age_years > 15:
        return 1.0
    elif age_years > 5:
        return 0.6
    return 0.3


def normalize_population_estimate(population: int) -> float:
    if population > 100000:
        return 1.0
    elif population > 50000:
        return 0.7
    elif population > 10000:
        return 0.4
    return 0.1


def normalize_environment(env_condition: str) -> float:
    mapping = {
        "Sandy Soil": 0.8,
        "Clay Soil": 0.5,
        "Rocky Terrain": 0.3,
        "Wetlands": 0.7,
        "Humid Mediterranean coastal zone": 0.9,
        "Flood-prone near Euphrates River": 0.8,
    }
    return mapping.get(env_condition, 0.5)


def normalize_ordnance_condition(condition: str) -> float:
    mapping = {
        "Pristine": 0.3,
        "Corroded": 0.6,
        "Damaged": 0.9,
        "Leaking": 1.0,
    }
    return mapping.get(condition, 0.5)


def calculate_danger_score(
    munition_type: str,
    burial_depth_cm: float,
    ordnance_age: float,
    population_estimate: int,
    environment: str,
    ordnance_condition: str,
    uxo_count: float,
) -> float:
    weights = {
        "munition_type": 0.25,
        "uxo_count": 0.20,
        "burial_depth_cm": 0.10,
        "ordnance_age": 0.10,
        "population_estimate": 0.15,  # proxy for proximity
        "environment": 0.10,
        "ordnance_condition": 0.10,
    }

    score = (
        normalize_munition_type(munition_type) * weights["munition_type"]
        + normalize_uxo_count(uxo_count) * weights["uxo_count"]
        + normalize_burial_depth_cm(burial_depth_cm) * weights["burial_depth_cm"]
        + normalize_ordnance_age(ordnance_age) * weights["ordnance_age"]
        + normalize_population_estimate(population_estimate)
        * weights["population_estimate"]
        + normalize_environment(environment) * weights["environment"]
        + normalize_ordnance_condition(ordnance_condition)
        * weights["ordnance_condition"]
    )

    return round(score, 3)  # rounded for readability
