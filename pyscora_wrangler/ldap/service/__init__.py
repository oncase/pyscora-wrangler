import json
from typing import Any, List, Dict, Tuple, Type
from typeguard import check_type
from ldap3 import Server, Connection, ALL, SUBTREE
from ..utils import setup_logger

logger = setup_logger('LDAP Service')


class LdapService:
    LDAP_CONFIG_SCHEMA: Dict[str, Type] = {
        'root_dn': str,
        'server': str,
        'port': int,  # Optional. Default is 389.
        'server_alias': List[str],  # Optional. Default is [],
    }

    def __init__(self, ldap_config: Dict[str, Any]) -> None:
        """Class initialization

        Args:
            ldap_config (Dict[str, Any]): Dict with ldap server configurations. Dict keys types can be seen below:

            {
                'root_dn': str,
                'server': str,
                'port': int,  # Optional. Default is 389.
                'server_alias': List[str],  # Optional. Default is [],
            }

        Raises:
            ValueError: If `ldap_config` is not configured correctly.

        Returns:
            None
        """

        ldap_config_default_values = {'port': 389, 'server_alias': []}
        ldap_config_default_values.update(**ldap_config)

        # Public
        self.ldap_config: Dict[str, Any] = ldap_config_default_values

        # Private
        self.__ldap_username: str | None = None
        self.__ldap_password: str | None = None
        self.__ldap_connection: Connection = None
        self.__ldap_groups: List[str] = []
        self.__ldap_users: List[str] = []
        self.__user_is_authenticated: bool = False

        ldap_config_is_valid, err_msgs = self.__is_ldap_config_valid()
        if not ldap_config_is_valid:
            for err_msg in err_msgs:
                logger.critical(f'[__init__] {err_msg}')

            raise ValueError('Invalid ldap config object.')

    def __is_ldap_config_valid(self) -> Tuple[bool, List[str]]:
        """Check if configuration variable is valid

        Returns:
            Tuple[bool, List[str]]:
                - bool: True if `ldap_config` is valid, False otherwise.
                - List[str]: Error messages
        """

        ldap_config_is_valid = True
        err_msgs = []

        for key, value in self.ldap_config.items():
            if key not in self.LDAP_CONFIG_SCHEMA:
                logger.warning(f'Unused ldap_config key: {key}.')
                continue

            try:
                check_type(value, self.LDAP_CONFIG_SCHEMA.get(key))
            except TypeError:
                ldap_config_is_valid = False
                err_msgs.append(
                    f'Invalid value type for key {key}. Expected {self.LDAP_CONFIG_SCHEMA[key]}, got {type(value)}.'
                )

        for key, value in self.LDAP_CONFIG_SCHEMA.items():
            if key not in self.ldap_config:
                ldap_config_is_valid = False
                err_msgs.append(f'Missing key: {key}.')

        return ldap_config_is_valid, err_msgs

    def is_user_authenticated(self) -> bool:
        """Check if user is authenticated to ldap server

        Returns:
            bool: True if user is authenticated to ldap server, False otherwise.
        """

        return self.__user_is_authenticated

    def auth(self, username: str, password: str) -> bool:
        """Authenticate user to ldap server in SIMPLE mode

        Args:
            username (str): The user `username`.
            password (str): The user `password`.

        Raises:
            ValueError: If `username` or `password` is null or is empty string.

        Returns:
            bool: True if user is authenticated to ldap server, False otherwise.
        """

        try:
            self.__ldap_username = username.strip()
            self.__ldap_password = password.strip()

            if not self.__ldap_username or not self.__ldap_password:
                logger_msg = 'Username argument cannot be null or empty.' if not self.__ldap_username else ''
                logger_msg += 'Password argument cannot be null or empty.' if not self.__ldap_password else ''
                logger.error(f'[auth] {logger_msg}')

                raise ValueError('Invalid credentials.')

            port = int(self.ldap_config.get('port', 389))
            server_alias = self.ldap_config.get('server_alias', [])

            server = Server(
                self.ldap_config.get('server', ''),
                get_info=ALL,
                port=port,
                allowed_referral_hosts=[(sa, True) for sa in server_alias]
                if server_alias and len(server_alias)
                else None,
            )

            self.__ldap_connection = Connection(
                server,
                user=self.__ldap_username,
                password=self.__ldap_password,
                authentication='SIMPLE',
                raise_exceptions=False,
            )

            if self.__ldap_connection.bind():
                self.__user_is_authenticated = True
                logger.info("[auth] Successful bind to ldap server.")
            else:
                logger.error(f"[auth] Cannot bind to ldap server: {self.__ldap_connection.last_error}.")
        except Exception as err:
            logger.error(f'[auth] {err}')

        return self.is_user_authenticated()

    def logout(self) -> None:
        """Unbind the connect to the ldap server"""

        if self.__ldap_connection:
            try:
                self.__ldap_connection.unbind()
            except Exception as err:
                logger.error(f'[logout] {err}')

    def get_ldap_groups(self) -> List[str]:
        """Returns A list containing the ldap groups."""

        return self.__ldap_groups

    def get_ldap_users(self) -> List[str]:
        """Returns A list containing the ldap users."""

        return self.__ldap_users

    def set_ldap_users_and_groups(self) -> Tuple[List[str], List[str]] | None:
        """Set the ldap groups and users.

        Returns:
            Tuple[List[str], List[str]] | None: Returns None if an error occurs in the process. Otherwise, returns a Tuple the lists of the ldap groups and the ldap users.
        """

        if not self.is_user_authenticated():
            logger.warning('[set_ldap_users_and_groups] User is not authenticated. Skipping...')
            return None

        groups = []
        root_dn = self.ldap_config.get('root_dn', '')

        try:
            self.__ldap_connection.search(
                search_base=root_dn,
                search_filter="(objectclass=*)",
                search_scope=SUBTREE,
                attributes=["member"],
                size_limit=0,
            )

            response = json.loads(self.__ldap_connection.response_to_json())

            if type(response.get("entries")) == list and len(response.get("entries")) > 0:
                for entry in response.get("entries"):
                    for member in entry.member.values:
                        self.__ldap_connection.search(
                            search_base=root_dn,
                            search_filter=f"(distinguishedName={member})",
                            attributes=["sAMAccountName"],
                        )

                        user = self.__ldap_connection.entries[0].sAMAccountName.values

                        self.__ldap_users.append(user)

                cn_groups = response.get("entries")[0].get("attributes").get("member")

                for cn_group in cn_groups:
                    groups.append(cn_group.split(",")[0].replace("CN=", ""))

                self.__ldap_groups = groups
        except Exception as err:
            logger.error(f'[set_ldap_users_and_groups] {err}')
            return None

        return self.get_ldap_users(), self.get_ldap_groups()
