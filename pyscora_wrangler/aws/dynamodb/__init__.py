from typing import Any, Dict, List, Literal, Tuple
from awswrangler.dynamodb import *
from boto3.session import Session
from boto3.dynamodb.conditions import Key
from ..utils import setup_logger, get_boto3_session, get_data_encoded, get_data_decoded
from ..constants import DYNAMODB_SERVICE_NAME

logger = setup_logger('AWS DynamoDB')


def create_tables(tables: List[Dict[str, Any]], boto3_session: Session | None = None) -> List[Dict[str, Any]]:
    """Adds new tables to your account

    Args:
        tables (List[Dict[str, Any]]): Tables to be created. Attributes can be found at https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/create_table.html
        boto3_session (Session | None, optional): Custom boto3 session. Defaults to None.

    Returns:
        List[Dict[str, Any]]: Tables descriptions and responses outputs.
    """

    session = get_boto3_session(boto3_session)
    client = session.client(DYNAMODB_SERVICE_NAME)

    response_arr: List[Dict[str, Any]] = []

    try:
        for table_config in tables:
            response = client.create_table(**table_config)
            logger.info('[create_tables] Table created')
            response_arr.append(response)
    except Exception as err:
        logger.error(f'[create_tables] {err}')

    return response_arr


def get_all_data_in_table(
    table_name: str,
    select: Literal['ALL_ATTRIBUTES']
    | Literal['ALL_PROJECTED_ATTRIBUTES']
    | Literal['SPECIFIC_ATTRIBUTES']
    | Literal['COUNT'] = 'ALL_ATTRIBUTES',
    boto3_session: Session | None = None,
    *dynamodb_additional_args: Tuple,
    **dynamodb_additional_kwargs: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Get all data in table

    Args:
        table_name (str): The name of the table containing the requested items.
        select ('ALL_ATTRIBUTES' | 'ALL_PROJECTED_ATTRIBUTES' | 'SPECIFIC_ATTRIBUTES' | 'COUNT', optional): The attributes to be returned in the result. Defaults to 'ALL_ATTRIBUTES'.
        boto3_session (Session | None, optional): Custom boto3 session. Defaults to None.

        Additional args can be found at https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/scan.html

    Returns:
        List[Dict[str, Any]]: An array of item attributes that match the scan criteria. Each element in this array consists of an attribute name and the value for that attribute.
    """

    session = get_boto3_session(boto3_session)
    client = session.client(DYNAMODB_SERVICE_NAME)

    paginator = client.get_paginator('scan')
    response_iterator = paginator.paginate(
        TableName=table_name, Select=select, *dynamodb_additional_args, **dynamodb_additional_kwargs
    )

    response_arr: List[Dict[str, Any]] = []

    for items_per_page in response_iterator:
        items = items_per_page.get('Items', [])
        response_arr.extend(items)

    return response_arr


def get_data_by_key(
    table_name: str,
    key: str,
    value: Any,
    fields: List[str] | None = None,
    decode_data: bool = True,
    boto3_session: Session | None = None,
) -> Dict[str, Any] | None:
    """Get data by key property

    Args:
        table_name (str): The name of the table containing the requested items.
        key (str): Key name.
        value (Any): Key value.
        fields (List[str] | None, optional): Returns the specified fields. If None, all fields will be returned. Defaults to None.
        decode_data (bool, optional): Decode data before `Query` operation. Defaults to True.
        boto3_session (Session | None, optional): Custom boto3 session. Defaults to None.

    Returns:
        Dict[str, Any] | None: A dict of item attributes that match the query criteria. Returns None if no data was found.
    """

    session = get_boto3_session(boto3_session)
    resource = session.resource(DYNAMODB_SERVICE_NAME)

    data = None

    dynamo_table = resource.Table(table_name)
    response = dynamo_table.query(KeyConditionExpression=Key(key).eq(value))
    response = response.get('Items', [])

    if len(response) > 0:
        data = get_data_decoded(response[0]) if decode_data else response[0]

    if fields != None and data:
        data = {field: data.get(field) for field in fields}

    return data


def get_all_tables_names(
    boto3_session: Session | None = None, *dynamodb_additional_args: Tuple, **dynamodb_additional_kwargs: Dict[str, Any]
) -> List[str]:
    """Returns an array of table names associated with the current account and endpoint

    Args:
        boto3_session (Session | None, optional): Custom boto3 session. Defaults to None.

        Additional args can be found at https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/list_tables.html

    Returns:
        List[str]: The names of the tables.
    """

    session = get_boto3_session(boto3_session)
    client = session.client(DYNAMODB_SERVICE_NAME)

    paginator = client.get_paginator('list_tables')
    response_iterator = paginator.paginate(*dynamodb_additional_args, **dynamodb_additional_kwargs)

    response_arr: List[str] = []

    for items_per_page in response_iterator:
        items = items_per_page.get('TableNames', [])
        response_arr.extend(items)

    return response_arr


def put_item(
    table_name: str,
    data: Dict[str, Any],
    encode_data: bool = True,
    boto3_session: Session | None = None,
    *dynamodb_additional_args: Tuple,
    **dynamodb_additional_kwargs: Dict[str, Any],
) -> Dict[str, Any]:
    """Creates a new item, or replaces an old item with a new item at the specified table.

    Args:
        table_name (str): The name of the table to contain the item.
        data (Dict[str, Any]): A map of attribute name/value pairs, one for each attribute. Only the primary key attributes are required; you can optionally provide other attribute name-value pairs for the item.
        encode_data (bool, optional): Encode data before `PutItem` operation. Defaults to True.
        boto3_session (Session | None, optional): Custom boto3 session. Defaults to None.

        Additional args can be found at https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/put_item.html

    Returns:
        Dict[str, Any]: Return the attributes and other outputs of the `PutItem` operation.
    """

    session = get_boto3_session(boto3_session)
    resource = session.resource(DYNAMODB_SERVICE_NAME)

    table = resource.Table(table_name)
    encoded_data = get_data_encoded(data) if encode_data else data
    item = table.put_item(Item=encoded_data, *dynamodb_additional_args, **dynamodb_additional_kwargs)

    return item
