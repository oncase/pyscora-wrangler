from boto3.session import Session
from ..utils import get_boto3_session


def get_users(boto3_session: Session | None = None) -> None:
    session = get_boto3_session(boto3_session)
    print(session)
