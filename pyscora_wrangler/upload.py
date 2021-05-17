# File Management
import os

from multiprocessing import Pool

# AWS S3
from pyscora_wrangler.utils import get_bucket_uri_parts
import boto3
from botocore.exceptions import ClientError


def upload_file_s3(
    file_name,
    s3_path,
    boto3_client=None
) -> bool:
    """Upload single file to a specific bucket.

    Args:
        file_name (str): File to upload.
        s3_path (str): s3 path.
        file_name is used. Defaults to None.
        boto3_client (botocore.client.s3, optional): boto3 s3 client for
        connecting to AWS. If None it will create a client.

    Returns:
        [bool]: True if file was uploaded, else False.
    """
    print(file_name)
    print(s3_path)
    s3_client = boto3.client('s3') if boto3_client is None else boto3_client
    # Checking if boto3 client is valid.
    try:
        s3_client.upload_file
    except AttributeError as error:
        error = ValueError("Please, use a valid s3 client, like " +
                           "boto3.client('s3')")
        raise error

    try:
        s3_path_parsed = get_bucket_uri_parts(s3_path)
        s3_client.upload_file(file_name,
                              s3_path_parsed['bucket'],
                              s3_path_parsed['object_path'])
    except ClientError as e:
        print(e)
        return False
    return True


def _upload_file_s3_single_argument(kwargs):
    return upload_file_s3(**kwargs)


def mp_folder_s3_upload(
    folder_path,
    s3_folder_path,
    n_processes=None
):
    """Upload all the files of the folder to s3 using multiprocessing.

    Args:
        folder_path (str): path of the local folder.
        s3_folder_path (str): S3 folder path.
        n_processes (int, optional): Number of the processes to use.
        Defaults to None, which means to use the results of os.cpu_count().

    Returns:
        [bool]: Returns True if all of the processes have uploaded
        successfully. Returns False otherwise.
    """
    files = os.listdir(folder_path)
    files = [os.path.join(folder_path, i) for i in files]

    with Pool(n_processes) as p:
        kwargs = []
        for f in files:
            tail_of_filename = os.path.split(f)[1]
            arg_dict = {
                'file_name': f,
                's3_path': s3_folder_path + '/' + tail_of_filename
            }
            kwargs.append(arg_dict)

        result_vector = p.map(_upload_file_s3_single_argument, kwargs)

        return all(result_vector)
