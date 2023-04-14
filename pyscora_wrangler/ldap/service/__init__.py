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
        self.__ldap_connection: Connection | None = None
        self.__all_ldap_dns: List[str] | None = None
        self.__all_ldap_groups: List[str] | None = None
        self.__all_ldap_usernames: List[str] | None = None
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
                - bool: `True` if `ldap_config` is valid, `False` otherwise.
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
            bool: `True` if user is authenticated to ldap server, `False` otherwise.
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
            bool: `True` if user is authenticated to ldap server, `False` otherwise.
        """

        try:
            self.__ldap_username = username.strip()
            self.__ldap_password = password.strip()

            if not self.__ldap_username or not self.__ldap_password:
                logger_msg = 'Username argument cannot be null or empty.' if not self.__ldap_username else ''
                logger_msg += 'Password argument cannot be null or empty.' if not self.__ldap_password else ''
                logger.error(f'[auth] {logger_msg}')

                raise ValueError('Invalid credentials.')

            root_dn = self.ldap_config.get('root_dn')
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
                user=f'CN={self.__ldap_username},{root_dn}',
                password=self.__ldap_password,
                authentication='SIMPLE',
                raise_exceptions=False,
            )

            if self.__ldap_connection.bind():
                self.__user_is_authenticated = True
                logger.info('[auth] Successful bind to ldap server.')
            else:
                logger.error(f'[auth] Cannot bind to ldap server: {self.__ldap_connection.last_error}.')
            logger.debug(f'[auth] {self.__ldap_connection}')
        except Exception as err:
            logger.error(f'[auth] {err}')

        return self.is_user_authenticated()

    def __set_ldap_arrays(self, search_filter: str) -> List[str] | None:
        if not self.is_user_authenticated():
            logger.warning('[__set_ldap_arrays] User is not authenticated. Skipping...')
            return None

        root_dn = self.ldap_config.get('root_dn', '')

        self.__ldap_connection.search(
            search_base=root_dn, search_filter=search_filter, search_scope=SUBTREE, size_limit=0
        )

        arr = []
        for entry in self.__ldap_connection.entries:
            arr.append(entry.entry_dn)

        return arr

    def __set_all_ldap_dns(self) -> List[str] | None:
        """Set all the ldap DN's

        Returns:
            List[str] | None: Returns `None` if an error occurs in the process. Otherwise, returns the list of the ldap DN's.
        """

        search_filter = '(objectClass=*)'
        self.__all_ldap_dns = self.__set_ldap_arrays(search_filter=search_filter)

        return self.__all_ldap_dns

    def __set_all_ldap_usernames(self) -> List[str] | None:
        """Set all the ldap users

        Returns:
            List[str] | None: Returns `None` if an error occurs in the process. Otherwise, returns the list of the ldap users.
        """

        users_search_filter = '(objectClass=person)'
        users_dn = self.__set_ldap_arrays(search_filter=users_search_filter)

        if users_dn == None:
            return None

        self.__all_ldap_usernames = [user.split('=')[1].split(',')[0] for user in users_dn]

        return self.__all_ldap_usernames

    def __set_all_ldap_groups(self) -> List[str] | None:
        """Set all the ldap groups

        Returns:
            List[str] | None: Returns `None` if an error occurs in the process. Otherwise, returns the list of the ldap groups.
        """

        groups_search_filter = '(objectClass=groupOfNames)'
        groups_dn = self.__set_ldap_arrays(search_filter=groups_search_filter)

        if groups_dn == None:
            return None

        self.__all_ldap_groups = [group.split('=')[1].split(',')[0] for group in groups_dn]

        return self.__all_ldap_groups

    def get_all_ldap_dns(self, reset: bool = False) -> List[str] | None:
        """Get all the ldap DN's

        Args:
            reset (bool, optional): `True` if you want to reset the list (do all the process again, including the search), `False` if you want only its value. Defaults to False.

        Returns:
            List[str] | None: Returns `None` if an error occurs in the process. Otherwise, returns a list containing all the ldap DN's.
        """

        if reset or self.__all_ldap_dns == None:
            return self.__set_all_ldap_dns()

        return self.__all_ldap_dns

    def get_all_ldap_usernames(self, reset: bool = False) -> List[str] | None:
        """Get all the ldap usernames

        Args:
            reset (bool, optional): `True` if you want to reset the list (do all the process again, including the search), `False` if you want only its value. Defaults to False.

        Returns:
            List[str] | None: Returns `None` if an error occurs in the process. Otherwise, returns a list containing all the ldap usernames.
        """

        if reset or self.__all_ldap_usernames == None:
            return self.__set_all_ldap_usernames()

        return self.__all_ldap_usernames

    def get_all_ldap_groups(self, reset: bool = False) -> List[str] | None:
        """Get all the ldap groups

        Args:
            reset (bool, optional): `True` if you want to reset the list (do all the process again, including the search), `False` if you want only its value. Defaults to False.

        Returns:
            List[str] | None: Returns `None` if an error occurs in the process. Otherwise, returns a list containing all the ldap groups.
        """

        if reset or self.__all_ldap_groups == None:
            return self.__set_all_ldap_groups()

        return self.__all_ldap_groups

    def logout(self) -> None:
        """Unbind the connection to the ldap server"""

        if self.__ldap_connection:
            try:
                self.__ldap_connection.unbind()
                logger.info('[logout] Successful unbind to ldap server.')
            except Exception as err:
                logger.error(f'[logout] {err}')
