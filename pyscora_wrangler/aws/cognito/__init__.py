from typing import Any, List, Dict, Tuple

from boto3.session import Session

from ..utils import setup_logger, get_boto3_session, get_user_secret_hash
from ..constants import COGNITO_SERVICE_NAME

logger = setup_logger('AWS Cognito')


def get_user(userpool_id: str, username: str, boto3_session: Session | None = None) -> Dict[str, Any]:
    """Gets the specified user by user name in a user pool as an administrator. Works on any user

    Calling this action requires developer credentials

    Args:
        userpool_id (str): The user pool ID for the user pool where you want to get information about the user.
        username (str): The user name of the user you want to retrieve.
        boto3_session (Session | None, optional): Custom boto3 session. Defaults to None.

    Returns:
        Dict[str, Any]: Represents the response from the server from the request to get the specified user as an administrator.
    """

    session = get_boto3_session(boto3_session)
    client = session.client(COGNITO_SERVICE_NAME)

    try:
        user = client.admin_get_user(UserPoolId=userpool_id, Username=username)

        return user
    except client.exceptions.UserNotFoundException:
        logger.warning(f'[get_user] User {username} not found. It is not registered.')
    except Exception as err:
        logger.error(f'[get_user] {err}')

    return None


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
        for user in users_by_page.get('Users', []):
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
        for user in users_by_page.get('Users', []):
            response_arr.append(user)

    return response_arr


def remove_user_from_userpool(userpool_id: str, username: str, boto3_session: Session | None = None) -> None:
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
        logger.info(f'[remove_user_from_userpool] User {username} deleted.')
    except client.exceptions.UserNotFoundException:
        logger.warning(f'[remove_user_from_userpool] User {username} does not exists. Skipping...')
    except Exception as err:
        logger.error(f'[remove_user_from_userpool] {err}')


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
        logger.error(f'[remove_user_from_group] {err}')


def create_user(
    userpool_id: str,
    username: str,
    user_attributes: List[Dict[str, Any]] = [],
    force_alias_creation: bool = False,
    boto3_session: Session | None = None,
    *cognito_additional_args: Tuple,
    **cognito_additional_kwargs: Dict[str, Any],
) -> Dict[str, Any]:
    """Creates a new user in the specified user pool

    Calling this action requires developer credentials

    Args:
        userpool_id (str): The user pool ID for the user pool where the user will be created.
        username (str): The username for the user. Must be unique within the user pool. Must be a UTF-8 string between 1 and 128 characters. After the user is created, the username can't be changed.
        user_attributes (List[Dict[str, Any]], optional): An array of name-value pairs that contain user attributes and attribute values to be set for the user to be created. You can create a user without specifying any attributes other than `Username`. Defaults to [].
        force_alias_creation (bool, optional): This parameter is used only if the phone_number_verified or email_verified attribute is set to True. Otherwise, it is ignored. Defaults to False.
        boto3_session (Session | None, optional): Custom boto3 session. Defaults to None.

        Additional args can be found at https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cognito-idp/client/admin_create_user.html

    Returns:
        Dict[str, Any]: The newly created user.
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
        remove_user_from_userpool(userpool_id=userpool_id, username=username)

    except Exception as err:
        logger.error(f'[create_user] {err}')

    return None


def create_group(
    userpool_id: str, group_name: str, description: str = '', boto3_session: Session | None = None
) -> Dict[str, Any]:
    """Creates a new group in the specified user pool

    Calling this action requires developer credentials

    Args:
        userpool_id (str): The user pool ID for the user pool.
        group_name (str): The name of the group. Must be unique.
        description (str, optional): A string containing the description of the group. Defaults to ''.
        boto3_session (Session | None, optional): Custom boto3 session. Defaults to None.

    Returns:
        Dict[str, Any]: The group object for the group.
    """

    session = get_boto3_session(boto3_session)
    client = session.client(COGNITO_SERVICE_NAME)

    try:
        response = client.create_group(UserPoolId=userpool_id, GroupName=group_name, Description=description)
        logger.info(f'[create_group] Group {group_name} created.')

        return response
    except client.exceptions.GroupExistsException:
        logger.warning(f'[create_group] A group with the name {group_name} already exists. Skipping...')
    except Exception as err:
        logger.error(f'[create_group] {err}')

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
        logger.error(f'[add_user_to_group] {err}')


def resend_confirmation_code(client_id: str, username: str, boto3_session: Session | None = None) -> Dict[str, Any]:
    """Resends the confirmation (for confirmation of registration) to a specific user in the user pool

    Args:
        client_id (str): The ID of the client associated with the user pool.
        username (str): The username attribute of the user to whom you want to resend a confirmation code.
        boto3_session (Session | None, optional): Custom boto3 session. Defaults to None.

    Returns:
        Dict[str, Any]: The code delivery details returned by the server in response to the request to resend the confirmation code.
    """

    session = get_boto3_session(boto3_session)
    client = session.client(COGNITO_SERVICE_NAME)

    try:
        response = client.resend_confirmation_code(ClientId=client_id, Username=username)
        logger.info(f'[resend_confirmation_code] Confirmation code sent to user {username}')

        return response
    except client.exceptions.UserNotFoundException:
        logger.warning(f'[resend_confirmation_code] User {username} does not exists. Skipping...')
    except Exception as err:
        logger.error(f'[resend_confirmation_code] {err}')

    return None


def set_user_password(
    userpool_id: str, username: str, password: str, permanent: bool = True, boto3_session: Session | None = None
) -> None:
    """Sets the specified user's password in a user pool as an administrator. Works on any user

    The password can be temporary or permanent. If it is temporary, the user status enters the `FORCE_CHANGE_PASSWORD` state. When the user next tries to sign in, the InitiateAuth/AdminInitiateAuth response will contain the `NEW_PASSWORD_REQUIRED` challenge. If the user doesn't sign in before it expires, the user won't be able to sign in, and an administrator must reset their password.
    Once the user has set a new password, or the password is permanent, the user status is set to `Confirmed`.

    Args:
        userpool_id (str): The user pool ID for the user pool where you want to set the user's password.
        username (str): The user name of the user whose password you want to set.
        password (str): The password for the user.
        permanent (bool, optional): `True` if the password is permanent, `False` if it is temporary. Defaults to True.
        boto3_session (Session | None, optional): Custom boto3 session. Defaults to None.

    Returns:
        None
    """

    session = get_boto3_session(boto3_session)
    client = session.client(COGNITO_SERVICE_NAME)

    try:
        client.admin_set_user_password(
            UserPoolId=userpool_id, Username=username, Password=password, Permanent=permanent
        )
    except client.exceptions.UserNotFoundException:
        logger.warning(f'[set_user_password] User {username} does not exists. Skipping...')
    except Exception as err:
        logger.error(f'[set_user_password] {err}')


def authenticate_user(
    userpool_id: str,
    client_id: str,
    username: str,
    password: str,
    auth_flow: str = 'ADMIN_NO_SRP_AUTH',
    app_client_secret: str | None = None,
    boto3_session: Session | None = None,
) -> Dict[str, Any]:
    """Initiates the authentication flow, as an administrator

    Calling this action requires developer credentials

    Args:
        userpool_id (str): The ID of the Amazon Cognito user pool.
        client_id (str): The app client ID.
        username (str): The user name of the user you want to authenticate.
        password (str): The password for the user.
        auth_flow (str, optional): The authentication flow for this call to run. The API action will depend on this value. Defaults to 'ADMIN_NO_SRP_AUTH'.
        app_client_secret (str | None, optional): The app client secret, if configured. Defaults to None.
        boto3_session (Session | None, optional): Custom boto3 session. Defaults to None.

    Returns:
        Dict[str, Any]: Initiates the authentication response, as an administrator.

    More info at: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cognito-idp/client/admin_initiate_auth.html
    """

    session = get_boto3_session(boto3_session)
    client = session.client(COGNITO_SERVICE_NAME)

    try:
        auth_parameters = {'USERNAME': username, 'PASSWORD': password}

        user_secret_hash = get_user_secret_hash(
            client_id=client_id, app_client_secret=app_client_secret, username=username
        )
        if user_secret_hash:
            auth_parameters['SECRET_HASH'] = user_secret_hash

        client_metadata = {'username': username, 'password': password}

        response = client.admin_initiate_auth(
            UserPoolId=userpool_id,
            ClientId=client_id,
            AuthFlow=auth_flow,
            AuthParameters=auth_parameters,
            ClientMetadata=client_metadata,
        )
        logger.info(f'[authenticate_user] User {username} authenticated.')

        return response
    except client.exceptions.UserNotFoundException:
        logger.warning(f'[authenticate_user] User {username} does not exists.')
    except Exception as err:
        logger.error(f'[authenticate_user] {err}')

    return None
