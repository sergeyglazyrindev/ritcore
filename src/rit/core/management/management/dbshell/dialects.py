import shlex
import subprocess


class Postgres(object):

    def __init__(self, uri):
        self.uri = uri

    def _build_shell_string(self):
        cmd_buffer = []
        if self.uri.password:
            cmd_buffer.extend(['export PGPASSWORD={};'.format(shlex.quote(self.uri.password))])
        cmd_buffer.append('psql')
        if self.uri.username:
            cmd_buffer.extend(['-U', shlex.quote(self.uri.username)])
        if self.uri.host:
            cmd_buffer.extend(['-h', self.uri.host])
        if self.uri.port:
            cmd_buffer.extend(['-p', self.uri.port])
        if self.uri.database:
            cmd_buffer.extend(['-d', shlex.quote(self.uri.database)])
        return cmd_buffer

    def open_shell(self):
        subprocess.call(' '.join(self._build_shell_string()), shell=True)

d_type_to_object = {
    'postgresql': Postgres
}


def get_dialect_by_type(d_type):
    return d_type_to_object[d_type]
