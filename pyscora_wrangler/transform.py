import pandas as pd
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
# Utils
from pyscora_wrangler.utils import overwrite_folder
import os


def to_parquet(
    stream,
    output_parquet: str,
    multiple_files=False,
    print_every=None,
    mode='overwrite',
    chunksize=None
):
    """
    Write chunks of pandas.DataFrame into a single or multiple parquet files.

    Args:
        stream (Chunk generator or pd.DataFrame): Stream of data through chunks.
        If it is a single pd.DataFrame then splits into a chunk list using
        'chunksize' argument.
        outuput_parquet (str): filepath to write the single file, or path to the
            folder where to write multiple chunks file.
        multiple_files (bool, optional): if True, then the 'output_parquet' must
            be a folder path, otherwise, it must be a file path.
        print_every (int, optional): Print the chunk index every 'print every'.
            If None, then it does not print. Defaults to None.
        mode (str, optional): It can be either 'overwrite' or 'append'. If 
            'overwrite', deletes folder/file and rewrite it. If 'appends' and 
            'multiple_files' is True then it writes following the current chunk 
            division of "chunk_0.parquet", "chunk_1.parquet", etc. Defaults to 
            'overwrite'.
        chunksize (int, optional): Only used if 'stream' is pd.DataFrame. The 
        chunksize to split the pd.DataFrame. Defaults to None.

    Returns:
        None.
    """
    if mode == 'overwrite' and multiple_files:
        overwrite_folder(output_parquet)
    if mode == 'overwrite' and not multiple_files:
        os.remove(output_parquet)

    if isinstance(stream, pd.DataFrame):
        print('Breaking DataFrame into chunks...')
        chunksize = len(stream) // chunksize
        stream = np.array_split(stream, chunksize)

    if multiple_files:
        for i, chunk in enumerate(stream):
            if print_every and (i % print_every) == 0:
                print(f"Reading chunk {i}.")
            # Create a parquet table from your first chunk.
            if index == 0:
                table = pa.Table.from_pandas(chunk)
                schema = table.schema
            else:
                table = pa.Table.from_pandas(chunk, schema=schema)
            pa.parquet.write_table(table,
                                   where=f"{output_parquet}/" +
                                   f"chunk_{i}.parquet")

    if multiple_files == False:
        for i, chunk in enumerate(stream):
            if print_every and (i % print_every) == 0:
                print(f"Reading chunk {i}.")
            if i == 0:
                # Infer schema and open parquet file on first chunk
                parquet_schema = pa.Table.from_pandas(df=chunk).schema
                parquet_writer = pq.ParquetWriter(
                    output_parquet, parquet_schema, compression='snappy')

            table = pa.Table.from_pandas(chunk, schema=parquet_schema)
            parquet_writer.write_table(table)
        parquet_writer.close()
