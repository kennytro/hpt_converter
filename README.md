# CMS HPT(Hospital Price Transparecy) File Converter
This package contains modules to convert raw [HPT](https://github.com/CMSgov/hospital-price-transparency) file, in both CSV and JSON, to Parquet files after transforming data to schema that can be easily consumed.

## Installation
```bash
pip install hpt-converter
```

## Usage
For CSV format, both "tall" and "wide", use `Csv2Parquet` module.
```python
from hpt_converter import Csv2Parquet

result = Csv2Parquet(
    csv_file_path=<path to raw CSV file>,
    out_dir_path=<path to output folder>,
    csv_type=<If None, the CSV type is inferred by reading the input file>
).convert()

print(result)       # result is the metadata of conversion.
```

For JSON format, use `Json2Parquet` module.

## Output Schema
Refer to the [README](./src/hpt_converter/lib/schema/abtract/README.md) in the schema folder.