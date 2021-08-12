import os
import shutil
from smart_open import open


def overwrite_folder(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.makedirs(directory)


def make_folder(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def decoder_of_files(
    input_path: str,
    output_path: str,
    dcd_output: str = 'latin',
) -> None:
    """It will overwrite the output file.

    Args:
        input_path (str)
        output_path (str)
        dcd_input (str, optional)
        dcd_output (str, optional)
    """
    if input_path == output_path:
        raise Exception('input_path and output_path must be different.')
    with open(output_path, 'w') as new_file:
        with open(input_path, 'rb') as input_file:
            for line in input_file:
                line = line.decode(dcd_output)
                new_file.write(line)
