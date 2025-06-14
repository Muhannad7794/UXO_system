# danger_score/tests/test_update_danger_scores_command.py

import io
import pytest
from django.core.management import call_command
from pytest import approx

# We need to import BOTH factories and the model now
from .factories import UXORecordFactory, RegionFactory
from ..calculators.danger_score_logic import calculate_danger_score
from uxo_records.models import UXORecord


@pytest.mark.django_db
def test_update_danger_scores_command_updates_records():
    """
    Integration test to verify that the command correctly recalculates
    and saves the danger_score for existing records.
    """
    # 1. Arrange: Create a batch of records in the test database.
    #    We give them an initial, incorrect danger_score of 0.0.
    records = UXORecordFactory.create_batch(5, danger_score=0.0)

    # 2. Act: Run the management command.
    call_command("update_danger_scores")

    # 3. Assert: Check that the scores have been updated correctly.
    for record in records:
        # Refresh the record from the database to get the updated value
        record.refresh_from_db()
        # Recalculate the expected score manually
        expected_score = calculate_danger_score(record)

        # Assert that the score is no longer the old value and matches the expected value
        assert record.danger_score != 0.0
        assert record.danger_score == approx(expected_score)


@pytest.mark.django_db
def test_update_danger_scores_command_handles_no_records():
    """
    Unit test to verify the command's output when there are no records
    in the database to process.
    """
    # 1. Arrange: Ensure the database is empty.
    #    (It already is, thanks to pytest-django's fresh test database).
    #    We also prepare a string buffer to capture the command's output.
    out = io.StringIO()

    # 2. Act: Run the command, redirecting its standard output to our buffer.
    call_command("update_danger_scores", stdout=out)

    # 3. Assert: Check that the captured output contains the expected notice.
    assert "No UXO records found to update." in out.getvalue()


@pytest.mark.django_db
def test_update_danger_scores_is_efficient(mocker):
    """
    Integration test to ensure the command uses the efficient `bulk_update`
    method instead of saving records one by one in a loop.
    """
    # 1. Arrange (Part 1): Create the single, saved Region instance first.
    #    This object now exists in the test database and has a valid ID.
    test_region = RegionFactory.create()

    # 2. Arrange (Part 2): Build 10 record objects in memory, explicitly
    #    assigning the pre-saved region to all of them.
    records_to_create = UXORecordFactory.build_batch(
        10, danger_score=0.0, region=test_region  # Link to the saved region
    )

    # 3. Arrange (Part 3): Now, bulk_create will work because the related
    #    'region' object has a valid primary key.
    UXORecord.objects.bulk_create(records_to_create)

    # 4. Spy: Use pytest-mock's `mocker.spy` to watch the bulk_update method.
    spy = mocker.spy(UXORecord.objects, "bulk_update")

    # 5. Act: Run the command.
    call_command("update_danger_scores")

    # 6. Assert: Check that our spy was called. The command should now find
    #    records with incorrect scores and call bulk_update exactly once.
    assert spy.call_count == 1
