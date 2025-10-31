import argparse
import sys
from pathlib import Path
from typing import Any, get_args, get_origin

from hpt_converter.lib.schema.abstract.v1 import *

TEMPLATE = """
# Abstract Schema[^1]
Data in HPT file is split into 3 files:
* General data element
* Payer plan
* Standard charge

[^1]: Auto generated document. DO NOT manually edit this file.

"""


def get_type_name(field_name: str, annotation: Any) -> str:
    type_map = {'str': 'String',
                'bool': 'Boolean'}
    # TODO: emit Enum type as a hyperlink to its definition. 
    if annotation.__name__ in type_map:
        return type_map[annotation.__name__]
    if annotation.__name__ == 'Optional':
        type_name = get_args(annotation)[0].__name__
        return type_name if type_name not in type_map else type_map[type_name]
    if get_origin(annotation) == list:
        return f"List[{get_args(annotation)[0].__name__}]"
    if get_origin(annotation) == tuple:
        args = get_args(annotation)
        return f"Tuple[{', '.join([type_map.get(x.__name__) or  x.__name__ for x in args])}]"
    # [NOTE] uncomment the line below after supporting enum type.
    # raise AssertionError(f"Unsupported type({annotation}) of field({field_name})")
    return annotation.__name__

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update README.md in 'lib/schema/abstract/' with abstract schema definition.")

    parser.add_argument("--version", default="v1", type=str, help="Absctract schema version.")
    parser.add_argument("--path", default='hpt_converter/lib/schema/abstract/', type=str, help="Path to the README.md excluding version folder.")
    parser.add_argument("--exclusive", action='store_true', help="Do not write if README.md exists.")

    args = parser.parse_args()
    file_path = Path(__file__).parent.parent.joinpath(args.path, args.version, 'README.md')
    if file_path.exists() and args.exclusive:
        print(f'{file_path} already exist. Exiting...')
        sys.exit(-1)
    
    with open(file_path, mode='w') as file:
        file.write(TEMPLATE)
        for model in [GeneralDataElements, PayerPlan, StandardCharge]:
            file.write(f'\n## {model.__name__}\n\n')
            file.write("|Name|Type|Description|\n")
            file.write("|---|:---:|---|\n")
            for field_name, field_info in model.model_fields.items():
                file.write(f"|{field_name}|{get_type_name(field_name, field_info.annotation)}|{field_info.description}|\n")
        # [TODO] add a section for enum definitions.
    print("Done")
    sys.exit(0)