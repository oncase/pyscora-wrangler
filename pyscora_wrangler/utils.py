import os
import shutil


def overwrite_folder(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.makedirs(directory)


def make_folder(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


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
