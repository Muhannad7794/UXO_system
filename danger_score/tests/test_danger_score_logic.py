# danger_score/tests/test_danger_score_logic.py

import pytest
from pytest import approx

# Import the function we want to test
from ..calculators.danger_score_logic import calculate_danger_score

# Import the factory to create test data
from .factories import UXORecordFactory


# By using the @pytest.mark.django_db marker, pytest allows this test
# to access the database, which is needed to create model instances.
@pytest.mark.django_db
def test_danger_score_with_high_risk_parameters():
    """
    Unit test to verify that a record with high-risk parameters
    receives a correspondingly high danger score.
    """
    # 1. Arrange: Create a UXORecord instance with high-risk attributes
    #    using the factory and overriding specific fields.
    high_risk_record = UXORecordFactory(
        ordnance_type="IED",  # Highest threat type
        ordnance_condition="LEK",  # Highest threat condition
        is_loaded=True,  # Highest threat
        proximity_to_civilians="IMM",  # Highest vulnerability
        burial_status="EXP",  # Highest threat burial status
    )

    # 2. Act: Call the function we are testing.
    calculated_score = calculate_danger_score(high_risk_record)

    # 3. Assert: Check that the result is what we expect.
    #    A combination of the highest-risk parameters should result in a score > 0.9.
    assert calculated_score is not None
    assert calculated_score > 0.9


@pytest.mark.django_db
def test_danger_score_with_low_risk_parameters():
    """
    Unit test to verify that a record with low-risk parameters
    receives a correspondingly low danger score.
    """
    # 1. Arrange: Create a UXORecord with low-risk attributes.
    low_risk_record = UXORecordFactory(
        ordnance_type="OTH",  # Lowest threat type
        ordnance_condition="INT",  # Lowest threat condition
        is_loaded=False,  # Lowest threat
        proximity_to_civilians="REM",  # Lowest vulnerability
        burial_status="BUR",  # Lowest threat burial status
    )

    # 2. Act: Call the function.
    calculated_score = calculate_danger_score(low_risk_record)

    # 3. Assert: Check for a low score.
    #    A combination of the lowest-risk parameters should result in a score < 0.3.
    assert calculated_score is not None
    assert calculated_score < 0.3


@pytest.mark.django_db
def test_danger_score_with_specific_known_values():
    """
    Unit test to verify the exact calculation against a known set of inputs and expected output.
    This confirms the formula and weights are being applied correctly.
    """
    # 1. Arrange: Create a record with specific, known values.
    # Let's use: ART (0.7), INTACT (0.2), is_loaded=True (1.0),
    # BURIED (0.2), proximity=NEA (0.6)
    specific_record = UXORecordFactory(
        ordnance_type="ART",
        ordnance_condition="INT",
        is_loaded=True,
        proximity_to_civilians="NEA",
        burial_status="BUR",
    )

    # Manually calculate the expected score based on the formula in the report
    # ThreatScore = (0.7*0.4) + (0.2*0.3) + (1.0*0.2) + (0.2*0.1) = 0.28 + 0.06 + 0.2 + 0.02 = 0.56
    # VulnerabilityScore = 0.6
    # DangerScore = (0.56 * 0.6) + (0.6 * 0.4) = 0.336 + 0.24 = 0.576
    expected_score = 0.576

    # 2. Act: Call the function.
    calculated_score = calculate_danger_score(specific_record)

    # 3. Assert: Check that the calculated score is exactly what we expect.
    #    We use pytest.approx to handle potential floating-point inaccuracies.
    assert calculated_score == approx(expected_score)


@pytest.mark.django_db
def test_danger_score_with_missing_ordnance_type():
    """
    Unit test to verify that the calculator can still produce a valid score
    even when a threat parameter like 'ordnance_type' is missing,
    treating it as a low-risk value.
    """
    # 1. Arrange: Build a record in memory only, without a specific ordnance type.
    record_with_missing_data = UXORecordFactory.build(
        ordnance_type=None,
        # Use high-risk values for everything else to ensure the score isn't zero
        ordnance_condition="LEK",
        is_loaded=True,
        proximity_to_civilians="IMM",
        burial_status="EXP",
    )

    # 2. Act: Call the function with the incomplete in-memory object.
    calculated_score = calculate_danger_score(record_with_missing_data)

    # 3. Assert: Check that the score is a valid float between 0 and 1.
    #    This confirms the calculator handles the missing value gracefully
    #    without crashing and produces a reasonable output.
    assert isinstance(calculated_score, float)
    assert 0.0 <= calculated_score <= 1.0


def test_calculate_danger_score_with_invalid_input_type():
    """
    Unit test to ensure the function returns None if it's not passed a
    UXORecord instance. This covers the initial type check.
    """
    assert calculate_danger_score("this is not a valid record") is None
