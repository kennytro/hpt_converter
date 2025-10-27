import csv
import os
import argparse
import tempfile
from dataclasses import dataclass, asdict
from logging import getLogger
from typing import List, Tuple
import sys
import pyarrow as pa
import pyarrow.dataset as ds
import pyarrow.parquet as pq

from hpt_converter.lib.csv.utils import (infer_csv_type,
                                         read_general_data_elements)
from hpt_converter.lib.schema.abstract.v1 import *
from hpt_converter.lib.schema.csv import CsvType
from hpt_converter.lib.schema.csv.v2.standard_charge import \
    create_standard_charge_model


@dataclass
class FileMetaData:
    input_row_count: int = 0
    standard_charge_count: int = 0
    plan_count: int = 0


class Csv2Parquet:
    def __init__(self, csv_file_path, out_dir_path,
                 csv_type: CsvType = None):
        self.csv_file_path = csv_file_path
        self.out_dir_path = out_dir_path
        self.csv_type = csv_type or infer_csv_type(csv_file_path)
        self.meta_data: FileMetaData = FileMetaData()
        self.logger = getLogger(__name__)

    @staticmethod
    def split_raw_standard_charge(raw_standard_charge, csv_type: CsvType, file_id: str) -> List[Tuple[StandardCharge, PayerPlan]]:
        """Splits raw standard charge instance into abstract standard charge instances and payer plan instances.
        The CSV type determines the outcome dimition - Tall type produces a single pair while wide type produces multiple pairs.

        Args:
            raw_standard_charge (BaseModel): raw data instance found in file.
            csv_type (CsvType): The type of the CSV file (tall or wide).
            file_id (str): unique id of input file.
        
        Returns:
            list: List of tuple(standard charge, payer plan)
        """
        if csv_type == CsvType.TALL:
            # tall format has only one payer plan per row
            payer_plan = PayerPlan(file_id=file_id, payer_name=getattr(raw_standard_charge, 'payer_name'),
                                   plan_name=getattr(raw_standard_charge, 'plan_name'))
            standard_charge = StandardCharge(file_id=file_id, plan_id=payer_plan.plan_id, **raw_standard_charge.model_dump())
            return [(standard_charge, payer_plan)]

        # wide format may have multiple payer plans per row. We identify them by the presence of "standard_charge|...|negotiated_dollar" fields.
        payer_plans = {}
        for field_name in raw_standard_charge.__class__.model_fields:
            if field_name.startswith('standard_charge|') and field_name.endswith('|negotiated_dollar'):
                tokens = field_name.split('|')
                assert len(tokens) == 4, f"Unexpected field name format: {field_name}"
                payer_plans[tokens[1] + '|' + tokens[2]] = PayerPlan(
                    file_id=file_id,
                    payer_name=tokens[1],
                    plan_name=tokens[2])

        return_list = []
        standard_charge_template = (StandardCharge(file_id=file_id, **raw_standard_charge.model_dump())
                                    .model_dump(exclude=['plan_id', 'negotiated_dollar', 'negotiated_percentage',
                                                         'negotiated_algorithm', 'estimated_amount', 'methodology',
                                                         'additional_payer_notes']))
        for payer_plan_key, payer_plan in payer_plans.items():
            standard_charge = StandardCharge(
                plan_id=payer_plan.plan_id,
                negotiated_dollar=getattr(raw_standard_charge, f'standard_charge|{payer_plan_key}|negotiated_dollar', None),
                negotiated_percentage=getattr(raw_standard_charge, f'standard_charge|{payer_plan_key}|negotiated_percentage', None),           
                negotiated_algorithm=getattr(raw_standard_charge, f'standard_charge|{payer_plan_key}|negotiated_algorithm', None),
                estimated_amount=getattr(raw_standard_charge, f'estimated_amount|{payer_plan_key}', None),
                methodology=getattr(raw_standard_charge, f'standard_charge|{payer_plan_key}|methodology', None),
                additional_payer_notes=getattr(raw_standard_charge, f'additional_payer_notes|{payer_plan_key}', None),
                **standard_charge_template)
            return_list.append((standard_charge, payer_plan))

        return return_list

    def convert(self) -> FileMetaData:

        general_data_elements = read_general_data_elements(self.csv_file_path)
        self.logger.info(f"General Data Elements: {general_data_elements.model_dump()}")

        sc_model = create_standard_charge_model(self.csv_file_path)
        with tempfile.TemporaryDirectory() as tmp_dir:
            sc_temp_path = os.path.join(tmp_dir, 'standard_charges')
            os.makedirs(sc_temp_path)
            payer_plans_map = {}
            standard_charges = []
            sc_file_count = 1
            with open(self.csv_file_path, mode='r', newline='', encoding='utf-8') as csv_file:
                # skip first 2 lines
                next(csv_file)
                next(csv_file)
                csv_reader = csv.DictReader(csv_file)
                for row_num, row in enumerate(csv_reader, start=1):
                    try:
                        raw_standard_charge = sc_model(**row)
                        ## standard_charge = sc_model.model_validate(row)
                        self.meta_data.input_row_count += 1
                        sc_pp_pair_list = self.split_raw_standard_charge(raw_standard_charge, self.csv_type, general_data_elements.file_id)
                        for standard_charge, payer_plan in sc_pp_pair_list:
                            standard_charges.append(standard_charge)
                            self.meta_data.standard_charge_count += 1
                            if payer_plan.plan_id not in payer_plans_map:
                                payer_plans_map[payer_plan.plan_id] = payer_plan
                                self.meta_data.plan_count += 1

                        if len(standard_charges) >= 10000000:
                            # Write to temp parquet file
                            sc_file_path = os.path.join(sc_temp_path, f'standard_charges_{sc_file_count}.parquet')
                            pq.write_table(
                                pa.Table.from_pylist([sc.model_dump() for sc in standard_charges]),
                                sc_file_path,
                                compression='SNAPPY'
                            )
                            standard_charges = []
                            sc_file_count += 1

                    except Exception as e:
                        self.logger.error(f"Error processing line {row_num}: {e}")
                        raise

            # Write remaining standard charges
            if standard_charges:
                sc_file_path = os.path.join(sc_temp_path, f'standard_charges_{sc_file_count}.parquet')
                pq.write_table(
                    pa.Table.from_pylist([sc.model_dump() for sc in standard_charges]),
                    sc_file_path,
                    compression='SNAPPY'
                )
            # Merge temp parquet files into final output
            dataset = ds.dataset(sc_temp_path, format='parquet')
            pq.write_table(
                dataset.to_table(),
                os.path.join(self.out_dir_path, 'standard_charges.parquet'),
                compression='SNAPPY'
            )
            # write other files
            pq.write_table(
                pa.Table.from_pylist([general_data_elements.model_dump()]),
                os.path.join(self.out_dir_path, 'general_data_elements.parquet'),
                compression='SNAPPY')
            pq.write_table(
                pa.Table.from_pylist([pp.model_dump() for pp in payer_plans_map.values()]),
                os.path.join(self.out_dir_path, 'payer_plans.parquet'),
                compression='SNAPPY'
            )
        self.logger.info(f"Conversion completed. Output written to {self.out_dir_path}")
        self.logger.info(f"File MetaData: {self.meta_data}")
        return self.meta_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert HPT CSV to abstract schema in Parquet.")

    parser.add_argument("input", type=str, help="Path to input CSV file.")
    parser.add_argument("--output-folder", type=str, help="Path to output folder. Default is the folder where the input file is.")
    parser.add_argument("--csv-type", choices=[m.value for m in CsvType], help="Type of input CSV file(\"wide\" or \"tall\")")
    parser.add_argument("--infer-type", action='store_true', help="Infer input CSV file type without conversion.")
    args = parser.parse_args()

    if args.infer_type:
        csv_type = infer_csv_type(args.input)
        print(f"File({args.input}) type: {csv_type.value}")
        sys.exit(0)
    if not args.output_folder:
        args.output_folder = os.path.dirname(args.input)
        print(f"Set 'output-folder' to {args.output_folder}")
    try:
        result = Csv2Parquet(csv_file_path=args.input,
                             out_dir_path=args.output_folder,
                             csv_type=CsvType(args.csv_type) if args.csv_type else None).convert()
        print(f"Result: {asdict(result)}")
        sys.exit(0)
    except Exception as e:
        print(f"Failed: {str(e)}")
        sys.exit(-1)
