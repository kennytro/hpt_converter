from hpt_converter.lib.csv.utils import CsvType

from hpt_converter.csv2parquet import Csv2Parquet, FileMetaData
from pathlib import Path
from tests.unit.common import create_standard_charge_instance
import pandas as pd
import shutil
import pytest
from dataclasses import asdict


def test_split_raw_standard_charge_tall():
    # Arrange
    file_id = "file123"
    instance = create_standard_charge_instance(CsvType.TALL)

    # Act
    result = Csv2Parquet.split_raw_standard_charge(instance, CsvType.TALL, file_id)

    # Assert
    assert len(result) == 1
    standard_charge, payer_plans = result[0]
    assert standard_charge.file_id == file_id
    assert standard_charge.plan_id == payer_plans.plan_id
    assert payer_plans.file_id == file_id
    assert payer_plans.payer_name == 'payer A'
    assert payer_plans.plan_name == 'plan A1'

def test_split_raw_standard_charge_wide():
    # Arrange
    file_id = "file456"
    instance = create_standard_charge_instance(CsvType.WIDE)
 
    # Act
    result = Csv2Parquet.split_raw_standard_charge(instance, CsvType.WIDE, file_id)

    # Assert
    assert len(result) == 1
    standard_charge, payer_plans = result[0]
    assert standard_charge.file_id == file_id
    assert standard_charge.plan_id == payer_plans.plan_id
    assert payer_plans.file_id == file_id
    assert payer_plans.payer_name == 'payer A'
    assert payer_plans.plan_name == 'plan A1'


@pytest.mark.parametrize("csv_type,file_name", [(CsvType.TALL, "tall_v2.csv"),
                                                (CsvType.WIDE, "wide_v2.csv")])
def test_convert(csv_type: CsvType, file_name: str, tmp_path: Path, data_root: Path):
    # Arrange
    converter = Csv2Parquet(
        csv_file_path=data_root.joinpath('csv', file_name),
        out_dir_path=tmp_path,
        csv_type=csv_type
    )

    # Act
    result = converter.convert()

    # Assert
    print(f"metadata: {asdict(result)}")
    if csv_type == CsvType.TALL:
        assert result == FileMetaData(input_row_count=31, standard_charge_count=31, plan_count=2)
    elif csv_type == CsvType.WIDE:
        assert result == FileMetaData(input_row_count=20, standard_charge_count=40, plan_count=2)


    snapshot_dir = Path(__file__).parent.joinpath('snapshots', 'csv2parquet', csv_type.value)
    for file in tmp_path.iterdir():
        print(f'checking the data in {file.name}')
        df = pd.read_parquet(file)
        print(df.head(n=10))
        snapshot_path = snapshot_dir.joinpath(file.name)
        if not snapshot_path.exists():
            print(f"snapshot {str(snapshot_path)} doesn't exist. Creating a new one")
            shutil.copy(file, str(snapshot_path))
        else:
            df2 = pd.read_parquet(snapshot_path)
            assert df.equals(df2)


