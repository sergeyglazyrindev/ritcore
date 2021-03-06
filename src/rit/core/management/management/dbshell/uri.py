import re
from urllib.parse import unquote, parse_qsl


class URL(object):
    """
    Represent the components of a URL used to connect to a database.
    This object is suitable to be passed directly to a
    :func:`~sqlalchemy.create_engine` call.  The fields of the URL are parsed
    from a string by the :func:`.make_url` function.  the string
    format of the URL is an RFC-1738-style string.
    All initialization parameters are available as public attributes.
    :param drivername: the name of the database backend.
      This name will correspond to a module in sqlalchemy/databases
      or a third party plug-in.
    :param username: The user name.
    :param password: database password.
    :param host: The name of the host.
    :param port: The port number.
    :param database: The database name.
    :param query: A dictionary of options to be passed to the
      dialect and/or the DBAPI upon connect.
    """

    def __init__(self, drivername, username=None, password=None,
                 host=None, port=None, database=None, query=None):
        self.drivername = drivername
        self.username = username
        self.password = password
        self.host = host
        if port is not None:
            self.port = int(port)
        else:
            self.port = None
        self.database = database
        self.query = query or {}

    def __to_string__(self, hide_password=True):
        s = self.drivername + "://"
        if self.username is not None:
            s += _rfc_1738_quote(self.username)
            if self.password is not None:
                s += ':' + ('***' if hide_password
                            else _rfc_1738_quote(self.password))
            s += "@"
        if self.host is not None:
            if ':' in self.host:
                s += "[%s]" % self.host
            else:
                s += self.host
        if self.port is not None:
            s += ':' + str(self.port)
        if self.database is not None:
            s += '/' + self.database
        if self.query:
            keys = list(self.query)
            keys.sort()
            s += '?' + "&".join("%s=%s" % (k, self.query[k]) for k in keys)
        return s

    def __str__(self):
        return self.__to_string__(hide_password=False)

    def __repr__(self):
        return self.__to_string__()

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return \
            isinstance(other, URL) and \
            self.drivername == other.drivername and \
            self.username == other.username and \
            self.password == other.password and \
            self.host == other.host and \
            self.database == other.database and \
            self.query == other.query

    def get_backend_name(self):
        if '+' not in self.drivername:
            return self.drivername
        else:
            return self.drivername.split('+')[0]

    def get_driver_name(self):
        if '+' not in self.drivername:
            return self.get_dialect().driver
        else:
            return self.drivername.split('+')[1]

    def translate_connect_args(self, names=[], **kw):
        """Translate url attributes into a dictionary of connection arguments.
        Returns attributes of this url (`host`, `database`, `username`,
        `password`, `port`) as a plain dictionary.  The attribute names are
        used as the keys by default.  Unset or false attributes are omitted
        from the final dictionary.
        :param \**kw: Optional, alternate key names for url attributes.
        :param names: Deprecated.  Same purpose as the keyword-based alternate
            names, but correlates the name to the original positionally.
        """

        translated = {}
        attribute_names = ['host', 'database', 'username', 'password', 'port']
        for sname in attribute_names:
            if names:
                name = names.pop(0)
            elif sname in kw:
                name = kw[sname]
            else:
                name = sname
            if name is not None and getattr(self, sname, False):
                translated[name] = getattr(self, sname)
        return translated


def make_url(name_or_url):
    """Given a string or unicode instance, produce a new URL instance.
    The given string is parsed according to the RFC 1738 spec.  If an
    existing URL object is passed, just returns the object.
    """

    if isinstance(name_or_url, str):
        return _parse_rfc1738_args(name_or_url)
    else:
        return name_or_url


def _parse_rfc1738_args(name):
    pattern = re.compile(r'''
        (?P<name>[\w\+]+)://
        (?:
            (?P<username>[^:/]*)
            (?::(?P<password>.*))?
        @)?
        (?:
            (?:
                \[(?P<ipv6host>[^/]+)\] |
                (?P<ipv4host>[^/:]+)
            )?
            (?::(?P<port>[^/]*))?
        )?
        (?:/(?P<database>.*))?
    ''', re.X)

    m = pattern.match(name)
    if not m:
        raise ValueError('Couldn\'t parse rfc1738 URL')
    components = m.groupdict()
    if components['database'] is not None:
        tokens = components['database'].split('?', 2)
        components['database'] = tokens[0]
        query = (
            len(tokens) > 1 and dict(parse_qsl(tokens[1]))
        ) or None
    else:
        query = None
    components['query'] = query

    if components['username'] is not None:
        components['username'] = unquote(components['username'])

    if components['password'] is not None:
        components['password'] = unquote(components['password'])

    ipv4host = components.pop('ipv4host')
    ipv6host = components.pop('ipv6host')
    components['host'] = ipv4host or ipv6host
    name = components.pop('name')
    return URL(name, **components)


def _rfc_1738_quote(text):
    return re.sub(r'[:@/]', lambda m: "%%%X" % ord(m.group(0)), text)
