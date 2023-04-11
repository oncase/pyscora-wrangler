import os
import asyncio
import awswrangler as wr
from typing import Any, List, Dict, Type
from pyathena import connect
from concurrent.futures import ThreadPoolExecutor
from boto3.session import Session
from ..utils import setup_logger, get_boto3_session, get_copy_metadata, measure_time

from awswrangler.athena import *

logger = setup_logger('AWS Athena')


def get_sql_ctas_athena(athena_metadata: Dict[str, Any], parquet_path: str, table_name: str) -> str:
    """Create a SQL CTAS query for a given metadata, table name and parquet path

    There is no specification for database in the query

    Args:
        athena_metadata (Dict[str, Any]): dictionary containing column name and data type. Normally, this is the result of awswrangler.s3.read_parquet_metadata()[0].
        parquet_path (str): parquet path in S3 fs.
        table_name (str): Name of the table to create.

    Returns:
        str: SQL CTAS query.
    """

    columns = []
    sql = f'CREATE EXTERNAL TABLE {table_name} '

    for field in athena_metadata:
        value = athena_metadata.get(field)
        columns.append(f'{field} {value}')

    sql += f"({','.join(columns)}) STORED AS PARQUET LOCATION '{parquet_path}'"

    return sql


def create_athena_table_from_parquet(
    parquet_path: str,
    database: str,
    s3_staging_dir: str,
    table_name: str | None = None,
    athena_work_group: str | None = None,
    verbose: bool = True,
    boto3_session: Session | None = None,
) -> bool:
    """Create a table in AWS Athena from a source of parquet data

    Args:
        parquet_path (str): a parquet folder path in S3 fs.
        database (str): Athena database where the table will be created. Must previously exist.
        s3_staging_dir (str): S3 path to store the results of the Athena table creation.
        table_name (str | None, optional): Name of the table to be created. Defaults to None.  When None, it will default to the name of the parquet folder or parquet file.
        athena_work_group (str | None, optional): Athena workgroup to be specified. Defaults to None.
        verbose (bool, optional): More logs. Defaults to True.
        boto3_session (Session | None, optional): Custom boto3 session. Defaults to None.


    Returns:
        bool: True if the process had no errors, False, otherwise.
    """

    session = get_boto3_session(boto3_session)

    if table_name is None:
        table_name = os.path.split(parquet_path)[1]

    athena_metadata = wr.s3.read_parquet_metadata(path=parquet_path, boto3_session=session)[0]
    try:
        if len(athena_metadata) > 0:
            wr.catalog.delete_table_if_exists(database=database, table=table_name, boto3_session=session)
            logger.info(f'[create_athena_table_from_parquet] Deleted {table_name}.')

            ctas_sql = get_sql_ctas_athena(athena_metadata, parquet_path, table_name)

            conn = connect(
                s3_staging_dir=s3_staging_dir, schema_name=database, work_group=athena_work_group, session=session
            )
            cursor = conn.cursor()
            cursor.execute(ctas_sql)

            logger.info(f'[create_athena_table_from_parquet] Created {table_name}.')
            logger.info(f'[create_athena_table_from_parquet] SQL CTAS query:\n{ctas_sql}') if verbose else None
        else:
            logger.warning(
                f'[create_athena_table_from_parquet] There is no metadata for the parquet_path. Skipping table {table_name} creation...'
            )
    except Exception as err:
        logger.error(f'[create_athena_table_from_parquet] Error on CTAS of {table_name} on Athena. {err}')

        return False

    return True


@measure_time
def athena_refresh(
    database: str,
    tables_metadatas: List[Dict[str, Any]] | None = None,
    yaml_metadatas_file_path: str | None = None,
    boto3_session: Session | None = None,
) -> None:
    """Refreshes athena tables

    Args:
        database (str): AWS Athena database name. If the database does not exist, create a new one.

        YOU MUST SPECIFY ONE OF THOSE:
            tables_metadatas (List[Dict[str, Any]] | None, optional): List of dictionaries with athena tables metadatas. Defaults to None.
            yaml_metadatas_file_path (str | None, optional): Yaml file with athena tables metadatas. Defaults to None.

            YOU MUST SPECIFY (FOR EACH TABLE):

                - `name`;

                - `schema`;

                - `s3_path`;

                - `athena_work_group`;


        boto3_session (Session | None, optional): Custom boto3 session. Defaults to None.

    Returns:
        None
    """

    if not database:
        logger.warning('[athena_refresh] No database was given.')
        return

    if not tables_metadatas and not yaml_metadatas_file_path:
        logger.warning(
            '[athena_refresh] Please, specify on of those parameters: `TABLES_METADAS_FROM_YAML` or `YAML_METADATAS_FILE_PATH`.'
        )
        return

    session = get_boto3_session(boto3_session)

    if database not in wr.catalog.databases(boto3_session=session).values:
        logger.warning(f'[athena_refresh] Database {database} does not exist. Creating a new one...')
        try:
            wr.catalog.create_database(database, boto3_session=session)
            logger.info(f'[athena_refresh] Database {database} created.')
        except Exception as err:
            logger.error(f'[athena_refresh] {err}')
            return

    tables = get_copy_metadata(yaml_metadatas_file_path) if yaml_metadatas_file_path else tables_metadatas

    if not tables:
        logger.error('[athena_refresh] No table metadata was found.')
        return

    def _process(table_meta: Dict[str, Any]) -> Dict[str, str]:
        nonlocal database, session

        def _key_gen(meta: Type[table_meta]) -> str:
            return f"{database}_{meta.get('schema')}_{meta.get('name')}"

        base_path = table_meta.get('s3_path')
        table = _key_gen(table_meta)
        path = f'{base_path}/transac/parquet/{table}'

        create_athena_table_from_parquet(
            parquet_path=path,
            table_name=table,
            database=database,
            s3_staging_dir=f'{base_path}/athena-results',
            athena_work_group=table_meta.get('athena_work_group'),
            verbose=True,
            boto3_session=session,
        )

        return {'table': table}

    async def _process_async(tables: Type[tables]):
        logger.info('[athena_refresh_process_async] {0:<30} {1:>20}'.format('File', 'Completed at'))
        with ThreadPoolExecutor(max_workers=15) as executor:
            loop = asyncio.get_event_loop()
            tasks = [loop.run_in_executor(executor, _process, *table_meta) for table_meta in tables]

            for finished_task in await asyncio.gather(*tasks):
                logger.info(
                    f"[athena_refresh_process_async] Table {finished_task.get('table')} refreshed with success."
                )

    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(_process_async(tables))
    loop.run_until_complete(future)
