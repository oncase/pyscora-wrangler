from boto3.session import Session


def get_boto3_session(boto3_session: Session | None = None) -> Session:
    return boto3_session if boto3_session != None else Session()
