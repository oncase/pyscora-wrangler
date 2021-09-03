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


def get_bucket_uri_parts(uri_path):
    """Given a URI path get the important parts.

    Args:
        uri_path (str): URI path of a valid bucket system such as AWS or GCS.

    Raises:
        ValueError: If the path is invalid.

    Returns:
        [dict]: Dictionary containing the 'bucket' and 'object_path'.
    """
    if not uri_path.split(':')[0] in ['s3', 'gs']:
        raise ValueError('Must be a valid URI path.')
    split = uri_path.split('/')
    results_dict = {
        'bucket': split[2],
        'object_path': '/'.join(split[3:])
    }
    return results_dict
