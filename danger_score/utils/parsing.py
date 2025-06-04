# danger_score/utils/parsing.py
import re


def extract_numeric_value(
    value_str: str, fallback_map: dict = None, default_if_unparseable: float = None
) -> float | None:
    """
    Extracts a numeric value from a string.
    Handles ranges by averaging, specific text via fallback_map, and tries to clean common issues.
    Returns a float, or `default_if_unparseable` (which is None by default) if unparseable.
    """
    if not isinstance(value_str, str) or not value_str.strip():
        # If it's not a string or is an empty/whitespace string, try fallback or return default
        if (
            fallback_map
            and isinstance(value_str, str)
            and value_str.strip() in fallback_map
        ):
            return float(fallback_map[value_str.strip()])
        if fallback_map and value_str in fallback_map:  # For non-string keys if any
            return float(fallback_map[value_str])
        return default_if_unparseable

    original_value_for_fallback = value_str.strip()  # For fallback map lookup

    # 1. Normalize various dash characters to a standard hyphen
    # Using a more robust regex for dash normalization might be even better if many variants exist.
    normalized_str = value_str.replace("â€“", "-").replace("–", "-").replace("—", "-")
    normalized_str = normalized_str.replace("−", "-")  # Minus sign

    # 2. Handle ranges (e.g., "10-20", "5 - 7")
    if "-" in normalized_str:
        parts = normalized_str.split("-")
        numeric_parts = []
        for part in parts:
            part = part.strip()
            # Try to extract number even if it has non-numeric trailing chars like '+'
            match = re.match(r"^\s*([+-]?\d*\.?\d+)\s*[a-zA-Z_+]*\s*$", part)
            if match:
                try:
                    numeric_parts.append(float(match.group(1)))
                except ValueError:
                    pass  # Could not convert matched part

        if len(numeric_parts) > 0:
            return sum(numeric_parts) / len(
                numeric_parts
            )  # Average of valid numeric parts

    # 3. Handle single values, possibly with trailing characters (e.g., "15+", "75.0")
    # Try to extract number even if it has non-numeric trailing chars like '+'
    # This regex handles integers, floats, and optional leading sign.
    match = re.match(r"^\s*([+-]?\d*\.?\d+)\s*[a-zA-Z_+]*\s*$", normalized_str)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            pass  # Fall through to fallback or default

    # 4. Try fallback map if direct parsing failed
    if fallback_map and original_value_for_fallback in fallback_map:
        return float(fallback_map[original_value_for_fallback])

    # 5. If all else fails
    # print(f"Warning: Could not parse '{value_str}' to a numeric value.") # Optional warning
    return default_if_unparseable


# Renaming the function to be more descriptive of its improved capability
parse_value_to_numerical = extract_numeric_value

# Keep the old name for compatibility if it's imported elsewhere directly,
# but encourage use of the new name.
extract_numeric_start = extract_numeric_value
