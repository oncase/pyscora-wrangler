from typing import Any, Optional, Literal, Dict, List
from boto3.session import Session
from awswrangler.secretsmanager import *
from ..utils import get_boto3_session

AVAILABLE_EXTENSIONS: List[str] = ['yaml']


def generate_env_from_secretsmanager(
    secrets: Optional[Dict[str, Any]] = None,
    secret_name: Optional[str] = None,
    filename: Optional[str] = '.env',
    extension: Optional[Literal['yaml']] = None,
    boto3_session: Optional[Session] = None,
) -> None:
    """Generate env file from secrets

    Args:
        secrets (Optional[Dict[str, Any]], optional): Secrets data as a dictionary. Defaults to None.
        secret_name (Optional[str], optional): AWS secretsmanager name. Defaults to None.
        filename (Optional[str], optional): Name of the file to be created. Defaults to '.env'.
        extension (Optional[Literal[&#39;yaml&#39;]], optional): File extension. Defaults to None.
        boto3_session (Optional[Session], optional): Custom boto3 session. Defaults to None.

    Raises:
        ValueError: If neither `secrets` nor `secret_name` is specified.
        ValueError: If `filename` is empty or null.
        ValueError: If you pass a non-available extension.
    """

    if not secrets and not secret_name:
        raise ValueError('You must specify a secrets dictionary or a secret_name to retrieve from AWS.')

    if not filename:
        raise ValueError('Filename argument cannot be empty or null.')

    if not extension:
        extension = ''
    elif extension not in AVAILABLE_EXTENSIONS:
        raise ValueError(f"Extension '{extension}' is not available")

    operator = '='

    if extension == 'yaml':
        operator = ': '
        extension = f'.{extension}'

    if not secrets:
        session = get_boto3_session(boto3_session)
        secrets = get_secret_json(name=secret_name, boto3_session=session)

    with open(f'{filename}{extension}', 'w') as envfile:
        for idx, key in enumerate(secrets):
            break_line = '\n'

            if len(secrets) == idx + 1:
                break_line = ''

            envfile.write(f"{key}{operator}'{secrets.get(key)}'{break_line}")
