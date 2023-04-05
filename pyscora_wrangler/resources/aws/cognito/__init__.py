from typing import Any, List, Dict, Tuple

from boto3.session import Session

from ..utils import get_boto3_session
from ....utils.misc import setup_logger
from ..constants import *

logger = setup_logger('AWS Cognito')


def get_all_users(
    userpool_id: str,
    attributes_to_get: List[str] = [],
    filter: str = '',
    boto3_session: Session | None = None,
) -> List[Dict[str, Any]]:
    """Lists the users in the Amazon Cognito user pool

    Args:
        userpool_id (str): The user pool ID for the user pool on which the search should be performed.
        attributes_to_get (List[str], optional): An array of strings, where each string is the name of a user attribute to be returned for each user in the search results. If the array is null, all attributes are returned. Defaults to [].
        filter (str, optional): A filter string of the form “AttributeName Filter-Type “AttributeValue””. Quotation marks within the filter string must be escaped using the backslash () character. Defaults to ''.
        boto3_session (Session | None, optional): Custom boto3 session. Defaults to None.

    Returns:
        List[Dict[str, Any]]: The users returned in the request to list users.
    """

    session = get_boto3_session(boto3_session)
    client = session.client(COGNITO_SERVICE_NAME)

    paginator = client.get_paginator('list_users')
    response_iterator = paginator.paginate(UserPoolId=userpool_id, AttributesToGet=attributes_to_get, Filter=filter)

    response_arr: List[Dict[str, Any]] = []

    for users_by_page in response_iterator:
        for user in users_by_page.get('Users'):
            response_arr.append(user)

    return response_arr


def get_users_from_group(
    userpool_id: str, group_name: str, boto3_session: Session | None = None
) -> List[Dict[str, Any]]:
    """Lists the users in the specified group

    Args:
        userpool_id (str): The user pool ID for the user pool on which the search should be performed.
        group_name (str): The name of the group.
        boto3_session (Session | None, optional): Custom boto3 session. Defaults to None.

    Returns:
        List[Dict[str, Any]]: The users returned in the request to list users.
    """

    session = get_boto3_session(boto3_session)
    client = session.client(COGNITO_SERVICE_NAME)

    paginator = client.get_paginator('list_users_in_group')
    response_iterator = paginator.paginate(UserPoolId=userpool_id, GroupName=group_name)

    response_arr: List[Dict[str, Any]] = []

    for users_by_page in response_iterator:
        for user in users_by_page.get('Users'):
            response_arr.append(user)

    return response_arr


def delete_user_from_userpool(userpool_id: str, username: str, boto3_session: Session | None = None) -> None:
    """Deletes a user as an administrator. Works on any user

    Calling this action requires developer credentials

    Args:
        userpool_id (str): The user pool ID for the user pool where you want to delete the user.
        username (str): The user name of the user you want to delete.
        boto3_session (Session | None, optional): Custom boto3 session. Defaults to None.

    Returns:
        None
    """

    session = get_boto3_session(boto3_session)
    client = session.client(COGNITO_SERVICE_NAME)

    try:
        client.admin_delete_user(UserPoolId=userpool_id, Username=username)
        logger.info(f'[delete_user_from_userpool] User {username} deleted.')
    except client.exceptions.UserNotFoundException:
        logger.warning(f'[delete_user_from_userpool] User {username} does not exists. Skipping...')
    except Exception as err:
        logger.error(err)


def remove_user_from_group(
    userpool_id: str, username: str, group_name: str, boto3_session: Session | None = None
) -> None:
    """Removes the specified user from the specified group

    Calling this action requires developer credentials

    Args:
        userpool_id (str): The user pool ID for the user pool.
        username (str): The username for the user.
        group_name (str): The group name.
        boto3_session (Session | None, optional): Custom boto3 session. Defaults to None.

    Returns:
        None
    """

    session = get_boto3_session(boto3_session)
    client = session.client(COGNITO_SERVICE_NAME)

    try:
        client.admin_remove_user_from_group(UserPoolId=userpool_id, Username=username, GroupName=group_name)
        logger.info(f'[remove_user_from_group] User {username} deleted.')
    except client.exceptions.UserNotFoundException:
        logger.warning(f'[remove_user_from_group] User {username} does not exists. Skipping...')
    except Exception as err:
        logger.error(err)


def create_user(
    userpool_id: str,
    username: str,
    user_attributes: List[Dict[str, Any]] = [],
    force_alias_creation: bool = False,
    boto3_session: Session | None = None,
    *cognito_additional_args: Tuple,
    **cognito_additional_kwargs: Dict[str, Any],
) -> Dict[str, Any] | None:
    """Creates a new user in the specified user pool

    Calling this action requires developer credentials

    Args:
        userpool_id (str): The user pool ID for the user pool where the user will be created.
        username (str): The username for the user. Must be unique within the user pool. Must be a UTF-8 string between 1 and 128 characters. After the user is created, the username can't be changed.
        user_attributes (List[Dict[str, Any]], optional): An array of name-value pairs that contain user attributes and attribute values to be set for the user to be created. You can create a user without specifying any attributes other than `Username`. Defaults to [].
        force_alias_creation (bool, optional): This parameter is used only if the phone_number_verified or email_verified attribute is set to True. Otherwise, it is ignored. Defaults to False.
        boto3_session (Session | None, optional): Custom boto3 session. Defaults to None.

        Addition args can be found at https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cognito-idp/client/admin_create_user.html

    Returns:
        Dict[str, Any] | None: The newly created user.
    """

    session = get_boto3_session(boto3_session)
    client = session.client(COGNITO_SERVICE_NAME)

    try:
        user_created = client.admin_create_user(
            UserPoolId=userpool_id,
            Username=username,
            UserAttributes=user_attributes,
            ForceAliasCreation=force_alias_creation,
            *cognito_additional_args,
            **cognito_additional_kwargs,
        )

        return user_created.get('User', {})

    except client.exceptions.UsernameExistsException:
        logger.warning(f'[create_user] Username {username} already exists. Skipping creation...')

    except client.exceptions.CodeDeliveryFailureException:
        logger.critical('[create_user] Code delivery failed!')
        delete_user_from_userpool(userpool_id=userpool_id, username=username)

    except Exception as err:
        logger.error(err)

    return None


def add_user_to_group(userpool_id: str, username: str, group_name: str, boto3_session: Session | None = None) -> None:
    """Adds the specified user to the specified group

    Calling this action requires developer credentials

    Args:
        userpool_id (str): The user pool ID for the user pool.
        username (str): The username for the user.
        group_name (str): The group name.
        boto3_session (Session | None, optional): Custom boto3 session. Defaults to None.

    Returns:
        None
    """

    session = get_boto3_session(boto3_session)
    client = session.client(COGNITO_SERVICE_NAME)

    try:
        client.admin_add_user_to_group(UserPoolId=userpool_id, Username=username, GroupName=group_name)
        logger.info(f'[add_user_to_group] User {username} added to group {group_name}')
    except client.exceptions.UserNotFoundException:
        logger.warning(f'[add_user_to_group] User {username} does not exists. Skipping...')
    except Exception as err:
        logger.error(err)
