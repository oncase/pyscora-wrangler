from multiprocessing import Pool
from transform import to_parquet
import pandas as pd
import boto3
from botocore.exceptions import ClientError
import os
import time
import multiprocessing


def upload_file_s3(file_name, bucket, object_name=None):
    """Upload single file to a specific bucket.
    
    Args:
        file_name (str): File to upload.
        bucket (str): Bucket to upload to.
        object_name (str, optional): S3 object name. If not specified then
        file_name is used. Defaults to None.

    Returns:
        [bool]: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        print(e)
        return False
    return True

def upload_file_s3_async(kwargs):
    return upload_file_s3(kwargs['filename'],
                          kwargs['bucket'],
                          object_name=kwargs['object_name'])

if __name__ == '__main__':
    root_dir = 'test_data/output'
    files = os.listdir(root_dir)
    example_files = [os.path.join(root_dir, i) for i in files]
    
    # t0 = time.time()
    # for index, f in enumerate(example_files):
    #     print(f)
    #     print(f.split('/')[-1])
    #     upload_file_s3(f,
    #                    'oncase-test-data',
    #                    object_name=os.path.join('ENEM_2019/output',
    #                                             f.split('/')[-1]))
    #     if index == 5:
    #         break
    # t1 = time.time()
    # print(t1-t0)
    
    cpu_count = multiprocessing.cpu_count()
    print(cpu_count)
    
    t2 = time.time()
    with Pool(cpu_count) as p:
        kwargs = [{'filename': f, 'bucket': 'oncase-test-data',
                   'object_name': f.split('/')[-1]}  for f in example_files[10:15]]
        print(kwargs)
        print(p.map(upload_file_s3_async, kwargs))
    t3 = time.time()
    print(t3-t2)