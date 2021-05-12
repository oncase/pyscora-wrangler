import os
import shutil


def overwrite_folder(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.makedirs(directory)


def make_folder(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def parse_s3_path(s3_path):
    if s3_path[0:5] != 's3://':
        raise ValueError("There must be s3:// in 's3_path'.")
    
    split = s3_path.split('/')
    results_dict = {
        'bucket': split[2],
        'object_name': '/'.join(split[3:])
    }
    return results_dict

if __name__ == '__main__':
    print(parse_s3_path('s3://oncase-test-data/ENEM_2019/output/'))
    