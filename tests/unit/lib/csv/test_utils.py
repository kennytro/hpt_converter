from pathlib import Path

import pytest

import hpt_converter.lib.csv.utils as utils
from hpt_converter.lib.schema.csv.v2.standard_charge import \
    create_standard_charge_model


def test_normalize_header():
    # Arrange
    raw_header = {
        ' Description ',
        'SETTING',
        'Payer Name',
        'standard_charge | gross',
        ' standard_charge|discounted_cash '
    }

    # Act
    normalized_header = utils.normalize_header(raw_header)

    # Assert
    expected_header = {
        'description',
        'setting',
        'payer name',
        'standard_charge|gross',
        'standard_charge|discounted_cash'
    }
    assert normalized_header == expected_header


def test_get_csv_type():
    # Arrange
    tall_header = {
        'description',
        'setting',
        'payer_name',
        'plan_name',
        'standard_charge|gross'
    }
    wide_header = {
        'description',
        'setting',
        'standard_charge|gross',
        'standard_charge|discounted_cash'
    }
    invalid_header = {
        'description',
        'payer_name',
        'standard_charge|gross'
    }

    # Act & Assert
    assert utils.get_csv_type(tall_header) == utils.CsvType.TALL
    assert utils.get_csv_type(wide_header) == utils.CsvType.WIDE
    with pytest.raises(ValueError, match="Invalid standard charge header line."):
        utils.get_csv_type(invalid_header)


def test_infer_csv_type(data_root: Path):
    # Arrange
    test_root = Path(__file__).parent
    tall_csv = data_root.joinpath('csv', 'tall_v2.csv')
    wide_csv = data_root.joinpath('csv', 'wide_v2.csv')

    # Act & Assert
    assert utils.infer_csv_type(tall_csv) == utils.CsvType.TALL
    assert utils.infer_csv_type(wide_csv) == utils.CsvType.WIDE
    for bad_file in ['empty.csv', 'missing.csv']:
        with pytest.raises(ValueError, match="missing standard charge header line"):
            utils.infer_csv_type(test_root.joinpath('data', bad_file))


def test_read_general_data_elements(data_root: Path):
 
    # Act & Assert
    for file_name in ['tall_v2.csv', 'wide_v2.csv']:
        file_path = data_root.joinpath('csv', file_name)
        gde = utils.read_general_data_elements(file_path)
        assert gde.hospital_name == "West Mercy Hospital"
        assert gde.last_updated_on == "2024-07-01"
        assert gde.affirmation_statement is True
        assert gde.license_number == ("50056", "CA")


def test_create_standard_charge_model(data_root: Path):
    # Arrange
    tall_csv = data_root.joinpath('csv', 'tall_v2.csv')
    wide_csv = data_root.joinpath('csv', 'wide_v2.csv')

    # Act
    tall_model = create_standard_charge_model(tall_csv)
    wide_model = create_standard_charge_model(wide_csv)

    # Assert
    # Tall model should have tall-specific fields
    tall_model_fields = tall_model.model_fields
    assert 'payer_name' in tall_model_fields
    assert 'plan_name' in tall_model_fields
    assert 'standard_charge|negotiated_dollar' in tall_model_fields
    assert 'estimated_amount' in tall_model_fields

    # Wide model should not have tall-specific fields
    wide_model_fields = wide_model.model_fields
    assert 'payer_name' not in wide_model_fields
    assert 'plan_name' not in wide_model_fields
    assert 'standard_charge|negotiated_dollar' not in wide_model_fields
    assert 'estimated_amount' not in wide_model_fields
