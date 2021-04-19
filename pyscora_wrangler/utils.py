import os
import shutil

def overwrite_folder(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.makedirs(directory)

def make_folder(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)