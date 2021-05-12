import pandas as pd
from pyscora_wrangler.transform import to_parquet

stream = pd.read_csv('test_data/input/MICRODADOS_ENEM_2019.csv',
                     chunksize=100000)
to_parquet(stream,
           output_parquet='test_data/output',
           multiple_files=True)
