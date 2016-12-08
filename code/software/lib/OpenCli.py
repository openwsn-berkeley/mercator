#!/usr/bin/python

import threading
import logging
import time
from   datetime import timedelta


class NullLogHandler(logging.Handler):
    def emit(self, record):
        pass


class OpenCli(threading.Thread):
    """
    \brief Thread which handles CLI commands entered by the user.
    """

    CMD_LEVEL_USER   = "user"
    CMD_LEVEL_SYSTEM = "system"

    def __init__(self, app_name, quit_cb):

        # slot params
        self.appName         = app_name
        self.quit_cb         = quit_cb

        # local variables
        self.commandLock     = threading.Lock()
        self.commands        = []
        self.goOn            = True
        self.startTime       = 0

        # logging
        self.log             = logging.getLogger('OpenCli')
        self.log.setLevel(logging.DEBUG)
        self.log.addHandler(NullLogHandler())

        # initialize parent class
        threading.Thread.__init__(self)

        # give this thread a name
        self.name            = 'OpenCli'

        # register system commands (user commands registers by child object)
        self._register_command_internal(
                self.CMD_LEVEL_SYSTEM,
                'help',
                'h',
                'print this menu',
                [],
                self._handle_help)
        self._register_command_internal(
                self.CMD_LEVEL_SYSTEM,
                'info',
                'i',
                'information about this application',
                [],
                self._handle_info)
        self._register_command_internal(
                self.CMD_LEVEL_SYSTEM,
                'quit',
                'q',
                'quit this application',
                [],
                self._handle_quit)
        self._register_command_internal(
                self.CMD_LEVEL_SYSTEM,
                'uptime',
                'ut',
                'how long this application has been running',
                [],
                self._handle_uptime)

    def run(self):
        banner  = []
        banner += [""]
        banner += [" ___                 _ _ _  ___  _ _ "]
        banner += ["| . | ___  ___ ._ _ | | | |/ __>| \ |"]
        banner += ["| | || . \/ ._>| ' || | | |\__ \|   |"]
        banner += ["`___'|  _/\___.|_|_||__/_/ <___/|_\_|"]
        banner += ["     |_|                  openwsn.org"]
        banner += [""]
        banner  = '\n'.join(banner)
        print banner

        print '{0}\n'.format(self.appName)

        self.startTime = time.time()

        while self.goOn:

            # CLI stops here each time a user needs to call a command
            params = raw_input('> ')

            # log
            self.log.debug('Following command entered:'+params)

            params = params.split()
            if len(params) < 1:
                continue

            if len(params) == 2 and params[1] == '?':
                if not self._print_usage_from_name(params[0]):
                    if not self._print_usage_from_alias(params[0]):
                        print ' unknown command or alias \''+params[0]+'\''
                continue

            # find this command
            found = False
            self.commandLock.acquire()
            for command in self.commands:
                if command['name'] == params[0] or command['alias'] == params[0]:
                    found = True
                    cmd_params     = command['params']
                    cmd_callback   = command['callback']
                    break
            self.commandLock.release()

            # call its callback or print error message
            if found:
                if len(params[1:]) == len(cmd_params):
                    cmd_callback(params[1:])
                else:
                    if not self._print_usage_from_name(params[0]):
                        self._print_usage_from_alias(params[0])
            else:
                print ' unknown command or alias \''+params[0]+'\''

    #======================== public ==========================================

    def register_command(self, name, alias, description, params, callback):

        self._register_command_internal(self.CMD_LEVEL_USER,
                                        name,
                                        alias,
                                        description,
                                        params,
                                        callback)

    #======================== private =========================================

    def _register_command_internal(self, cmd_level, name, alias, description, params, callback):

        if self._does_command_exist(name):
            raise SystemError("command {0} already exists".format(name))

        self.commandLock.acquire()
        self.commands.append({
                                'cmd_level':      cmd_level,
                                'name':          name,
                                'alias':         alias,
                                'description':   description,
                                'params':        params,
                                'callback':      callback,
                             })
        self.commandLock.release()

    def _print_usage_from_name(self, commandname):
        return self._print_usage(commandname, 'name')

    def _print_usage_from_alias(self, commandalias):
        return self._print_usage(commandalias, 'alias')

    def _print_usage(self, name, param_type):

        usage_string = None

        self.commandLock.acquire()
        for command in self.commands:
            if command[param_type] == name:
                usage_string  = []
                usage_string += ['usage: {0}'.format(name)]
                usage_string += [" <{0}>".format(p) for p in command['params']]
                usage_string  = ''.join(usage_string)
        self.commandLock.release()

        if usage_string:
            print usage_string
            return True
        else:
            return False

    def _does_command_exist(self, cmd_name):

        return_val = False

        self.commandLock.acquire()
        for cmd in self.commands:
            if cmd['name'] == cmd_name:
                return_val = True
        self.commandLock.release()

        return return_val

    #=== command handlers (system commands only, a child object creates more)

    def _handle_help(self):
        output  = []
        output += ['Available commands:']

        self.commandLock.acquire()
        for command in self.commands:
            output += [' - {0} ({1}): {2}'.format(command['name'],
                                                  command['alias'],
                                                  command['description'])]
        self.commandLock.release()

        print '\n'.join(output)

    def _handle_info(self):
        output  = []
        output += ['General status of the application']
        output += ['']
        output += ['current time: {0}'.format(time.ctime())]
        output += ['']
        output += ['{0} threads running:'.format(threading.activeCount())]
        for t in threading.enumerate():
            output += ['- {0}'.format(t.getName())]
        output += ['']
        output += ['This is thread {0}.'.format(threading.currentThread().getName())]

        print '\n'.join(output)

    def _handle_quit(self):

        # call the quit callback
        self.quit_cb()

        # kill this thread
        self.goOn = False

    def _handle_uptime(self):

        up_time = timedelta(seconds=time.time()-self.startTime)

        print 'Running since {0} ({1} ago)'.format(
                time.strftime("%m/%d/%Y %H:%M:%S", time.localtime(self.startTime)),
                up_time)


###############################################################################

if __name__ == '__main__':

    def quit_callback():
        print "quitting!"

    def echo_callback(params):
        print "echo {0}!".format(params)

    cli = OpenCli("Standalone Sample App", quit_callback)
    cli.register_command('echo',
                        'e',
                        'echoes the first param',
                         ['string to echo'],
                         echo_callback)
    cli.start()
