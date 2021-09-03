import pandas as pd
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq


def to_parquet(
    stream,
    output_path: str,
    multiple_files: bool = False,
    print_every=None,
    chunksize: int = None
):
    """
    Overwrite chunks of pandas.DataFrame into a single or multiple parquet
    files.

    Args:
        stream (pd.io.parsers.TextFileReader or pd.core.frame.DataFrame):
        Stream of data through chunks. If it is a single pd.DataFrame then
        splits into a chunk list using 'chunksize' argument.
        outuput_parquet (str): filepath to write the single file, or path to
        the folder where to write multiple chunks file.
        multiple_files (bool, optional): if True, then the 'output_path'
        must be a folder path, otherwise, it must be a file path.
        print_every (int, optional): Print the chunk index every 'print every'.
        If None, then it does not print. Defaults to None.
        chunksize (int, optional): Only used if 'stream' is pd.DataFrame. The
        chunksize to split the pd.DataFrame. Defaults to None.

    Returns:
        None.
    """
    if (not isinstance(stream, pd.core.frame.DataFrame) and
            not isinstance(stream, pd.io.parsers.TextFileReader)):
        # Raise Exception and print the stream type to help clarify.
        your_stream_type = f'Your stream type: {str(type(stream))}'
        raise ValueError(your_stream_type +
                         " 'stream' argument must be either pd.DataFrame " +
                         "or pd.io.parsers.TextFileReader")

    if isinstance(stream, pd.DataFrame):
        if not chunksize:
            raise Exception("If using stream as a pd.Dataframe, must also " +
                            "pass the value of chunksize.")

        print('Breaking DataFrame into chunks...')
        chunksize = len(stream) // chunksize
        stream = np.array_split(stream, chunksize)

    if multiple_files:
        for i, chunk in enumerate(stream):
            if print_every and (i % print_every) == 0:
                print(f"Reading chunk {i}.")
            # Create a parquet table from your first chunk.
            if i == 0:
                table = pa.Table.from_pandas(chunk)
                schema = table.schema
            else:
                table = pa.Table.from_pandas(chunk, schema=schema)
            pa.parquet.write_table(table,
                                   where=f"{output_path}/" +
                                   f"chunk_{i}.parquet")

    if multiple_files is False:
        for i, chunk in enumerate(stream):
            if print_every and (i % print_every) == 0:
                print(f"Reading chunk {i}.")
            if i == 0:
                # Infer schema and open parquet file on first chunk
                parquet_schema = pa.Table.from_pandas(df=chunk).schema
                parquet_writer = pq.ParquetWriter(
                    output_path, parquet_schema, compression='snappy')

            table = pa.Table.from_pandas(chunk, schema=parquet_schema)
            parquet_writer.write_table(table)
        parquet_writer.close()
