import csv

from typing import Optional, Set

from hpt_converter.lib.schema.abstract.v1.general_data_elements import GeneralDataElements
from hpt_converter.lib.schema.csv import CsvType


def normalize_header(header: Set[str]) -> Set[str]:
    """Normalizes the header fields:
        1. convert to lowercase
        2. strip whitespace.
        3. replace ' | ' with '|'

    Args:
        header (Set[str]): Set of header fields from the CSV file.
    Returns:
        Set[str]: Normalized set of header fields.
    """
    return {x.lower().strip().replace(' | ', '|') for x in header}


def get_csv_type(header: set[str]) -> CsvType:
    """Determines the type of CSV file (tall or wide) based on its header.

    Args:
        header (set[str]): Set of header fields from the CSV file.
    Returns:
        CsvType: The type of the CSV file.
    Raises:
        ValueError: If the header is missing required fields.
    """
    header = normalize_header(header)
    if 'description' not in header or 'setting' not in header:
        raise ValueError(f"Invalid standard charge header line({header})")

    return CsvType.TALL if 'payer_name' in header else CsvType.WIDE



def infer_csv_type(csv_file_path) -> Optional[CsvType]:
    """Infers the type of CSV file (tall or wide) based on its header line.

    Args:
        csv_file_path (str): Path to the CSV file.
    Returns:
        CsvType: The inferred type of the CSV file.
    Raises:
        ValueError: If the CSV file is missing or has an invalid standard charge header line.
    """
    standard_charge_header = []
    with open(csv_file_path, mode='r', newline='', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        for _ in range(3):
            standard_charge_header = next(csv_reader, None)

    if not standard_charge_header:
        raise ValueError(f"CSV file({csv_file_path}) is missing standard charge header line.")

    return get_csv_type(standard_charge_header)

        
def read_general_data_elements(csv_file_path) -> GeneralDataElements:
    """Reads a CSV file and returns a GeneralDataElements instance.    
    Args:
        csv_file_path (str): Path to the CSV file.

    Returns:
        GeneralDataElements: An instance of GeneralDataElements populated with data from the CSV file."""
    with open(csv_file_path, mode='r', newline='', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        header = [x for x in next(csv_reader, []) if x != '']
        elements = [x for x in next(csv_reader, []) if x != '']
        dict_elements = dict(zip(header, elements))

        for key in list(dict_elements.keys()):
            # rename affimation_statement key.
            if key.lower().startswith('to the best of its knowledge and belief'):
                dict_elements['affirmation_statement'] = dict_elements[key]
                del dict_elements[key]
            # transform license_number|<state> keys into a tuple
            if key.lower().startswith('license_number|'):
                state = key.split('|')[1].strip()
                dict_elements['license_number'] = (dict_elements[key], state)
                del dict_elements[key]

        return GeneralDataElements(**dict_elements)
