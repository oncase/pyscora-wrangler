# AWS

This module contains a set of functions to interact with AWS services.

## Athena

See `./athena/__init__.py` for more details.

## Cognito

### `add_user_to_group`

#### Adds the specified user to the specified group

Calling this action requires developer credentials.

#### Parameters

|      Name       |          Type           |            Description             | Required | Default |
| :-------------: | :---------------------: | :--------------------------------: | :------: | :-----: |
|  `userpool_id`  |          `str`          | The user pool ID for the user pool |  `True`  |   `-`   |
|   `username`    |          `str`          |     The username for the user      |  `True`  |   `-`   |
|  `group_name`   |          `str`          |           The group name           |  `True`  |   `-`   |
| `boto3_session` | `boto3.session.Session` |        Custom boto3 session        | `False`  | `None`  |

#### Returns

`None`

### `authenticate_user`

#### Initiates the authentication flow, as an administrator

Calling this action requires developer credentials.

#### Parameters

|        Name         |          Type           |                                      Description                                       | Required |       Default       |
| :-----------------: | :---------------------: | :------------------------------------------------------------------------------------: | :------: | :-----------------: |
|    `userpool_id`    |          `str`          |                         The ID of the Amazon Cognito user pool                         |  `True`  |         `-`         |
|     `client_id`     |          `str`          |                                   The app client ID                                    |  `True`  |         `-`         |
|     `username`      |          `str`          |                   The user name of the user you want to authenticate                   |  `True`  |         `-`         |
|     `password`      |          `str`          |                               The password for the user                                |  `True`  |         `-`         |
|     `auth_flow`     |          `str`          | The authentication flow for this call to run. The API action will depend on this value | `False`  | `ADMIN_NO_SRP_AUTH` |
| `app_client_secret` |          `str`          |                          The app client secret, if configured                          | `False`  |       `None`        |
|   `boto3_session`   | `boto3.session.Session` |                                  Custom boto3 session                                  | `False`  |       `None`        |

#### Returns

`Dict[str, Any]`: Initiates the authentication response, as an administrator.

### `create_group`

#### Creates a new group in the specified user pool

Calling this action requires developer credentials.

#### Parameters

|      Name       |          Type           |                   Description                    | Required | Default |
| :-------------: | :---------------------: | :----------------------------------------------: | :------: | :-----: |
|  `userpool_id`  |          `str`          |        The user pool ID for the user pool        |  `True`  |   `-`   |
|   `username`    |          `str`          |      The name of the group. Must be unique       |  `True`  |   `-`   |
|  `description`  |          `str`          | A string containing the description of the group | `False`  |  `''`   |
| `boto3_session` | `boto3.session.Session` |               Custom boto3 session               | `False`  | `None`  |

### `create_user`

#### Creates a new user in the specified user pool

Calling this action requires developer credentials.

#### Parameters

|          Name          |          Type           |                                                                                            Description                                                                                             | Required | Default |
| :--------------------: | :---------------------: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: | :------: | :-----: |
|     `userpool_id`      |          `str`          |                                                                 The user pool ID for the user pool where the user will be created                                                                  |  `True`  |   `-`   |
|       `username`       |          `str`          |           The username for the user. Must be unique within the user pool. Must be a UTF-8 string between 1 and 128 characters. After the user is created, the username can't be changed            |  `True`  |   `-`   |
|   `user_attributes`    | `List[Dict[str, Any]]`  | An array of name-value pairs that contain user attributes and attribute values to be set for the user to be created. You can create a user without specifying any attributes other than `Username` | `False`  |  `[]`   |
| `force_alias_creation` |         `bool`          |                                   TThis parameter is used only if the phone_number_verified or email_verified attribute is set to True. Otherwise, it is ignored                                   | `False`  | `False` |
|    `boto3_session`     | `boto3.session.Session` |                                                                                        Custom boto3 session                                                                                        | `False`  | `None`  |

##### Addition args can be found at [boto3 `admin_create_user` docs](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cognito-idp/client/admin_create_user.html)

#### Returns

`Dict[str, Any]`: The newly created user.

### `get_all_users`

#### Lists the users in the Amazon Cognito user pool

#### Parameters

|        Name         |          Type           |                                                                                 Description                                                                                  | Required | Default |
| :-----------------: | :---------------------: | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------: | :------: | :-----: |
|    `userpool_id`    |          `str`          |                                                  The user pool ID for the user pool on which the search should be performed                                                  |  `True`  |   `-`   |
| `attributes_to_get` |       `List[str]`       | An array of strings, where each string is the name of a user attribute to be returned for each user in the search results. If the array is null, all attributes are returned | `False`  |  `[]`   |
|      `filter`       |          `str`          |     A filter string of the form “AttributeName Filter-Type “AttributeValue””. Quotation marks within the filter string must be escaped using the backslash () character      | `False`  |  `''`   |
|   `boto3_session`   | `boto3.session.Session` |                                                                             Custom boto3 session                                                                             | `False`  | `None`  |

#### Returns

`List[Dict[str, Any]]`: The users returned in the request to list users.

### `get_user`

#### Gets the specified user by user name in a user pool as an administrator. Works on any user

Calling this action requires developer credentials.

#### Parameters

|      Name       |          Type           |                                     Description                                     | Required | Default |
| :-------------: | :---------------------: | :---------------------------------------------------------------------------------: | :------: | :-----: |
|  `userpool_id`  |          `str`          | The user pool ID for the user pool where you want to get information about the user |  `True`  |   `-`   |
|   `username`    |          `str`          |                   The user name of the user you want to retrieve                    |  `True`  |   `-`   |
| `boto3_session` | `boto3.session.Session` |                                Custom boto3 session                                 | `False`  | `None`  |

#### Returns

`Dict[str, Any]`: Represents the response from the server from the request to get the specified user as an administrator.

### `get_users_from_group`

#### Lists the users in the specified group

#### Parameters

|      Name       |          Type           |                                 Description                                 | Required | Default |
| :-------------: | :---------------------: | :-------------------------------------------------------------------------: | :------: | :-----: |
|  `userpool_id`  |          `str`          | The user pool ID for the user pool on which the search should be performed. |  `True`  |   `-`   |
|  `group_name`   |          `str`          |                            The name of the group                            |  `True`  |   `-`   |
| `boto3_session` | `boto3.session.Session` |                            Custom boto3 session                             | `False`  | `None`  |

#### Returns

`List[Dict[str, Any]]`: The users returned in the request to list users.

### `remove_user_from_group`

#### Removes the specified user from the specified group

Calling this action requires developer credentials.

#### Parameters

|      Name       |          Type           |            Description             | Required | Default |
| :-------------: | :---------------------: | :--------------------------------: | :------: | :-----: |
|  `userpool_id`  |          `str`          | The user pool ID for the user pool |  `True`  |   `-`   |
|   `username`    |          `str`          |     The username for the user      |  `True`  |   `-`   |
|  `group_name`   |          `str`          |           The group name           |  `True`  |   `-`   |
| `boto3_session` | `boto3.session.Session` |        Custom boto3 session        | `False`  | `None`  |

#### Returns

`None`

### `remove_user_from_userpool`

#### Deletes a user as an administrator. Works on any user

Calling this action requires developer credentials.

#### Parameters

|      Name       |          Type           |                             Description                              | Required | Default |
| :-------------: | :---------------------: | :------------------------------------------------------------------: | :------: | :-----: |
|  `userpool_id`  |          `str`          | The user pool ID for the user pool where you want to delete the user |  `True`  |   `-`   |
|   `username`    |          `str`          |             The user name of the user you want to delete             |  `True`  |   `-`   |
| `boto3_session` | `boto3.session.Session` |                         Custom boto3 session                         | `False`  | `None`  |

#### Returns

`None`

### `resend_confirmation_code`

#### Resends the confirmation (for confirmation of registration) to a specific user in the user pool

#### Parameters

|      Name       |          Type           |                                    Description                                    | Required | Default |
| :-------------: | :---------------------: | :-------------------------------------------------------------------------------: | :------: | :-----: |
|   `client_id`   |          `str`          |                The ID of the client associated with the user pool                 |  `True`  |   `-`   |
|   `username`    |          `str`          | The username attribute of the user to whom you want to resend a confirmation code |  `True`  |   `-`   |
| `boto3_session` | `boto3.session.Session` |                               Custom boto3 session                                | `False`  | `None`  |

#### Returns

`Dict[str, Any]`: The code delivery details returned by the server in response to the request to resend the confirmation code.

### `set_user_password`

#### Sets the specified user's password in a user pool as an administrator. Works on any user

##### The password can be temporary or permanent. If it is temporary, the user status enters the `FORCE_CHANGE_PASSWORD` state. When the user next tries to sign in, the InitiateAuth/AdminInitiateAuth response will contain the `NEW_PASSWORD_REQUIRED` challenge. If the user doesn't sign in before it expires, the user won't be able to sign in, and an administrator must reset their password.

##### Once the user has set a new password, or the password is permanent, the user status is set to `Confirmed`.

Calling this action requires developer credentials.

#### Parameters

|      Name       |          Type           |                                 Description                                  | Required | Default |
| :-------------: | :---------------------: | :--------------------------------------------------------------------------: | :------: | :-----: |
|  `userpool_id`  |          `str`          | The user pool ID for the user pool where you want to set the user's password |  `True`  |   `-`   |
|   `username`    |          `str`          |           The user name of the user whose password you want to set           |  `True`  |   `-`   |
|   `password`    |          `str`          |                          The password for the user                           |  `True`  |   `-`   |
|   `permanent`   |         `bool`          |       `True` if the password is permanent, `False` if it is temporary        |  `True`  | `True`  |
| `boto3_session` | `boto3.session.Session` |                             Custom boto3 session                             | `False`  | `None`  |

#### Returns

`None`

## DynamoDB

See `./dynamodb/__init__.py` for more details.

## Other Services

Check out [boto3 docs](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) and [awswrangler docs](https://pypi.org/project/awswrangler/) for more information.
