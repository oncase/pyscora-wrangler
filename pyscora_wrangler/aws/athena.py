import logging
import traceback
import os
import awswrangler as wr
from pyathena import connect


def get_sql_ctas_athena(
    athena_metadata,
    parquet_path,
    table_name
) -> str: 
    """
    Create a SQL CTAS query for a given metadata, table name and parquet path.
    There is no specification for database in the query.
    Args:
        athena_metadata (dict): dictionary containing column name and data type.
        Normally, this is the result of awswrangler.s3.read_parquet_metadata()[0].
        parquet_path (str): parquet path in S3 fs. 
        table_name (str): Name of the table to create.
    Returns:
        [str]: SQL CTAS query.
    """
    columns = []
    sql = f"CREATE EXTERNAL TABLE {table_name} "

    for field in athena_metadata:
        value = athena_metadata.get(field)
        columns.append(f"{field} {value}")

    sql += f"({','.join(columns)}) STORED AS PARQUET LOCATION '{parquet_path}'"

    return sql


def create_athena_table_from_parquet(
    parquet_path,
    database,
    s3_staging_dir,
    table_name=None,
    athena_work_group=None,
    verbose=True
) -> bool:
    """
    Create a table in AWS Athena from a source of parquet data.
    Args:
        parquet_path (str): a parquet folder path in S3 fs.
        table_name (str): Name of the table to be created. Defaults to None.
        When None, it will default to the name of the parquet folder or parquet file.
        database (str): Athena database where the table will be created.
        Must previously exist.
        athena_work_group (str): Athena workgroup to be specified. Defaults to None.
        s3_staging_dir (str): S3 path to store the results of the Athena table creation.
    Returns:
        bool: True if the process had no errors, False, otherwise.
    """
    if table_name is None:
        table_name = os.path.split(parquet_path)[1]
    
    athena_metadata = wr.s3.read_parquet_metadata(path=parquet_path)[0]
    try:
        if len(athena_metadata) > 0:
            wr.catalog.delete_table_if_exists(database=database, table=table_name)
            logging.info(f'Deleted {table_name}.')
            
            
            ctas_sql = get_sql_ctas_athena(athena_metadata, parquet_path, table_name)
            conn = connect(
                s3_staging_dir=s3_staging_dir,
                schema_name=database,
                work_group=athena_work_group
            )
            cursor = conn.cursor()
            cursor.execute(ctas_sql)
            logging.info(f'Created {table_name}.')
            logging.info(f'SQL CTAS query:\n{ctas_sql}') if verbose else None
        else:
            logging.info(f'There is no metadata for the parquet_path. Skipping table {table_name} creation.')
    except Exception:
        logging.error(f"Error on CTAS of {table_name} on Athena.")
        print(traceback.print_exc())
        return False
    return True
