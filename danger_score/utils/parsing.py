# danger_score/utils/parsing.py

import re


def extract_numeric_start(value: str, fallback_map: dict = None) -> float:
    try:
        if not value:
            return 0.0

        # Normalize dashes
        clean_value = value.replace("â€“", "-").replace("–", "-").replace("—", "-")

        # If it's a numeric range, take the lower bound
        if "-" in clean_value:
            first_part = clean_value.split("-")[0].strip()
            return float(first_part)

        # If it's a clean number
        return float(clean_value.strip())

    except ValueError:
        # Try to fallback to mapping
        if fallback_map and value.strip() in fallback_map:
            return fallback_map[value.strip()]

        raise ValueError(f"No numeric values found in '{value}'")
