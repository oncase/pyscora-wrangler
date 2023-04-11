import hmac
import base64
import hashlib
from boto3.session import Session
from ..utils import *


def get_boto3_session(boto3_session: Session | None = None) -> Session:
    return boto3_session if boto3_session != None else Session()


def get_user_secret_hash(client_id: str, app_client_secret: str, username: str) -> str | None:
    msg = username + client_id

    if not client_id or not app_client_secret or not username:
        return None

    try:
        dig = hmac.new(app_client_secret.encode('utf-8'), msg=msg.encode('utf-8'), digestmod=hashlib.sha256).digest()
        d2 = base64.b64encode(dig).decode()

        return d2
    except:
        return None
