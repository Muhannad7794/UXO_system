# uxo_records/tests/test_import_commands.py

import pytest
from django.core.management import call_command, CommandError
from django.contrib.gis.geos import MultiPolygon

from ..models import Region, UXORecord


@pytest.mark.django_db
class TestImportRegionsCommand:
    """
    Test suite for the import_regions management command.
    """

    def test_import_regions_successfully(self, tmp_path):
        """
        Verify that the command correctly imports regions from a valid CSV file.
        """
        csv_file = tmp_path / "regions.csv"
        csv_content = (
            "name,geometry\n"
            'Test Region A,"POLYGON ((0 0, 0 1, 1 1, 1 0, 0 0))"\n'
            'Test Region B,"POLYGON ((10 10, 10 20, 20 20, 20 10, 10 10))"\n'
        )
        csv_file.write_text(csv_content)

        call_command("import_regions", str(csv_file))

        assert Region.objects.count() == 2
        assert Region.objects.filter(name="Test Region A").exists()
        region_a = Region.objects.get(name="Test Region A")
        assert isinstance(region_a.geometry, MultiPolygon)

    def test_import_regions_with_clear_flag(self, tmp_path):
        """
        Verify that the --clear flag correctly deletes existing data before importing.
        """
        Region.objects.create(
            name="Old Region", geometry="MULTIPOLYGON (((0 0, 0 1, 1 1, 1 0, 0 0)))"
        )
        assert Region.objects.count() == 1

        csv_file = tmp_path / "new_regions.csv"
        csv_content = (
            'name,geometry\nNew Region,"POLYGON ((5 5, 5 6, 6 6, 6 5, 5 5))"\n'
        )
        csv_file.write_text(csv_content)

        call_command("import_regions", str(csv_file), "--clear")

        assert Region.objects.count() == 1
        assert not Region.objects.filter(name="Old Region").exists()
        assert Region.objects.filter(name="New Region").exists()

    def test_import_regions_file_not_found(self):
        """
        Verify that the command raises a CommandError if the CSV file does not exist.
        """
        non_existent_file = "/path/to/non_existent_file.csv"

        with pytest.raises(CommandError, match="Error: CSV file not found"):
            call_command("import_regions", non_existent_file)


@pytest.mark.django_db
class TestImportUXODataCommand:
    """
    Test suite for the import_uxo_data management command.
    """

    @pytest.fixture(autouse=True)
    def setup_regions(self):
        """
        A pytest fixture to ensure at least one Region exists for the spatial join.
        'autouse=True' means this will run automatically before each test in this class.
        """
        from .factories import RegionFactory

        RegionFactory.create(
            name="Test Area 1", geometry="MULTIPOLYGON (((0 0, 0 1, 1 1, 1 0, 0 0)))"
        )

    def test_import_uxo_data_successfully(self, tmp_path):
        """
        Verify that the command correctly imports UXO records from a valid CSV,
        performing data mapping and a spatial join.
        """
        csv_file = tmp_path / "uxo_data.csv"
        csv_content = (
            "latitude,longitude,ordnance_type,ordnance_condition,is_loaded,proximity_to_civilians,burial_status\n"
            "0.5,0.5,Artillery Projectile,Intact,True,Near (101-500m),Buried\n"
            "0.7,0.7,Landmine,Corroded,False,Remote (>500m),Exposed\n"
        )
        csv_file.write_text(csv_content)

        call_command("import_uxo_data", str(csv_file))

        assert UXORecord.objects.count() == 2
        # CORRECTED: Retrieve the record using a supported field lookup.
        record_1 = UXORecord.objects.get(ordnance_type=UXORecord.OrdnanceType.ARTILLERY)
        assert record_1.region.name == "Test Area 1"

    def test_import_uxo_data_with_clear_flag(self, tmp_path):
        """
        Verify that the --clear flag correctly deletes existing UXO records.
        """
        from .factories import UXORecordFactory

        UXORecordFactory.create(ordnance_type="IED")
        assert UXORecord.objects.count() == 1

        csv_file = tmp_path / "new_uxo.csv"
        csv_content = "latitude,longitude,ordnance_type,ordnance_condition,is_loaded,proximity_to_civilians,burial_status\n0.2,0.2,Mortar Bomb,Intact,True,Immediate (0-100m to civilians/infrastructure),Concealed (by vegetation/debris)\n"
        csv_file.write_text(csv_content)

        call_command("import_uxo_data", str(csv_file), "--clear")

        assert UXORecord.objects.count() == 1
        assert not UXORecord.objects.filter(ordnance_type="IED").exists()
        assert UXORecord.objects.filter(ordnance_type="MOR").exists()

    def test_import_uxo_data_handles_missing_column(self, tmp_path):
        """
        Verify that the command fails gracefully if a required column is missing.
        """
        csv_file = tmp_path / "bad_uxo.csv"
        csv_content = "latitude,longitude,ordnance_condition\n0.1,0.1,Intact\n"
        csv_file.write_text(csv_content)

        with pytest.raises(
            CommandError, match="Missing expected column 'ordnance_type'"
        ):
            call_command("import_uxo_data", str(csv_file))
