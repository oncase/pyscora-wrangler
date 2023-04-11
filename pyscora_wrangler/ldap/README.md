# Ldap

Services and functions to simplify ldap management, including extracting ldap infos.

## LdapService

Class with utils ldap methods.

Requires only a config dictionary. An example with types can be seen below:

```python
{
  "root_dn": "DC=service,DC=local", # REQUIRED. Type = str.
  "server": "ldap://localhost:389", # REQUIRED. Type = str.
  "port": 636, # OPTIONAL. Type = int. Default is 389.
  "server_alias": ["service.com.br"] # OPTIONAL. Type = List[str]. Default is [].
}

```
