import os
import argparse


class ShellCommand(object):
    help = ('''Runs a Python interactive interpreter. Tries to use
    IPython or bpython, if one of them is available.''')
    requires_system_checks = False
    shells = ['ipython', 'bpython', 'python']

    def parse_cargs(self, *params):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--no-startup', action='store_true',
            help=('''When using plain Python, ignore the PYTHONSTARTUP environment
            variable and ~/.pythonrc.py script.'''),
        )
        parser.add_argument(
            '-i', '--interface', choices=self.shells,
            help=('''Specify an interactive interpreter interface.
            Available options: "ipython", "bpython", and "python"'''),
        )
        parser.add_argument(
            '-c', '--command',
            help=('''Instead of opening an interactive shell,
            run a command as Django and exit.'''),
        )
        parsed_args = parser.parse_args(params)
        return parsed_args

    def _ipython_pre_011(self):
        """Start IPython pre-0.11"""
        from IPython.Shell import IPShell
        shell = IPShell(argv=[])
        shell.mainloop()

    def _ipython_pre_100(self):
        """Start IPython pre-1.0.0"""
        from IPython.frontend.terminal.ipapp import TerminalIPythonApp
        app = TerminalIPythonApp.instance()
        app.initialize(argv=[])
        app.start()

    def _ipython(self):
        """Start IPython >= 1.0"""
        from IPython import start_ipython
        start_ipython(argv=[])

    def ipython(self, options):
        """Start any version of IPython"""
        for ip in (
                self._ipython,
                self._ipython_pre_100,
                self._ipython_pre_011
        ):
            try:
                ip()
            except ImportError:
                pass
            else:
                return
        # no IPython, raise ImportError
        raise ImportError("No IPython")

    def bpython(self, options):
        import bpython
        bpython.embed()

    def python(self, options):
        import code
        # Set up a dictionary to serve as the environment for the shell, so
        # that tab completion works on objects that are imported at runtime.
        imported_objects = {}
        try:  # Try activating rlcompleter, because it's handy.
            import readline
        except ImportError:
            pass
        else:
            # We don't have to wrap the following import in a 'try', because
            # we already know 'readline' was imported successfully.
            import rlcompleter
            readline.set_completer(
                rlcompleter.Completer(imported_objects).complete
            )
            # Enable tab completion on systems using libedit (e.g. Mac OSX).
            # These lines are copied from Lib/site.py on Python 3.4.
            readline_doc = getattr(readline, '__doc__', '')
            if readline_doc is not None and 'libedit' in readline_doc:
                readline.parse_and_bind("bind ^I rl_complete")
            else:
                readline.parse_and_bind("tab:complete")

        # We want to honor both $PYTHONSTARTUP and .pythonrc.py,
        # so follow system
        # conventions and get $PYTHONSTARTUP first then .pythonrc.py.
        if not options.no_startup:
            for pythonrc in (
                    os.environ.get("PYTHONSTARTUP"),
                    '~/.pythonrc.py'
            ):
                if not pythonrc:
                    continue
                pythonrc = os.path.expanduser(pythonrc)
                if not os.path.isfile(pythonrc):
                    continue
                try:
                    with open(pythonrc) as handle:
                        exec(
                            compile(handle.read(), pythonrc, 'exec'),
                            imported_objects
                        )
                except NameError:
                    pass
        code.interact(local=imported_objects)

    def __call__(self, *params):
        params = self.parse_cargs(*params)

        available_shells = ([params.interface] if params.interface
                            else self.shells)

        for shell in available_shells:
            try:
                return getattr(self, shell)(params)
            except ImportError:
                pass
        raise ImportError("Couldn't load any of the specified interfaces.")
