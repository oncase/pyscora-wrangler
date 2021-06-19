import time
import os
import boto3
from pyscora_wrangler.upload import (
    mp_folder_s3_upload,
    upload_file_s3,
    mt_folder_s3_upload
)


mt_folder_s3_upload(folder_path='test_data/output',
                    s3_folder_path=('s3://oncase-test-data/ENEM_2019/output/' +
                                    'multi-threading'))
# # Testing upload_file_s3
# session = boto3.client('s3')
# upload_file_s3(file_name='test_data/input/MICRODADOS_ENEM_2019.csv',
#                s3_path='s3://oncase-test-data/input/MICRODADOS_ENEM_2019.csv',
#                boto3_client=123)


# # Testing mp_folder_s3_upload

# # # Single-Thread
# local_folder = 'test_data/output'
# s3_folder = 's3://oncase-test-data/ENEM_2019/output'
# files = os.listdir(local_folder)
# files = [os.path.join(local_folder, i) for i in files]

# t0 = time.time()
# for f in files:
#     tail_of_filename = os.path.split(f)[1]
#     s3_filepath = s3_folder + '/' + tail_of_filename
#     upload_file_s3(f,
#                    s3_filepath)
# t1 = time.time()
# print('Single Thread')
# print(t1-t0)


# # Our function using Multiprocessing
# t0 = time.time()
# mp_folder_s3_upload(folder_path='test_data/output',
#                     s3_folder_path='s3://oncase-test-data/ENEM_2019/output')
# t1 = time.time()
# print('Multiprocessing')
# print(t1 - t0)
