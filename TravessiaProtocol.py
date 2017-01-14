import asyncio
from random import choice

# PyIRC
from PyIRC.signal import event
from PyIRC.io.asyncio import IRCProtocol
from PyIRC.line import Line

# ?
from logging import getLogger
_logger = getLogger(__name__)  # pylint: disable=invalid-name


class TravessiaProtocol(IRCProtocol):

    def __init__(self, mainWindow, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.window = mainWindow

    yifflines = (
        "right there~",
        "mmmm yes~",
    )

    flirtlines = (
        "not in here! message me",
        "I don't do it in channels, sorry...",
    )

    def data_received(self, data):

        data = self.data + data

        lines = data.split(b'\r\n')
        # removes the byte assignment, ex. [b':whelm.freenode.net 482']
        self.data = lines.pop()

        for line in lines:
            line = Line.parse(line.decode('utf-8', 'ignore'))
            print('command %s' % line.command)
            print('params %s' % line.params)
            print('linestr %s' % line.linestr)

            # send datas to window/qt control its behavior
            self.window.dataReceived(line.command, line.params, line.linestr)

            _logger.debug("IN: %s", str(line).rstrip())
            try:
                super().recv(line)
            except Exception:
                # We should never get here!
                _logger.exception("Exception received in recv loop")
                self.send("QUIT", ["Exception received!"])
                self.transport.close()

                # This is fatal and needs to be reported so stop the event
                # loop.
                loop = asyncio.get_event_loop()
                loop.stop()

                raise

    @event("commands", "PRIVMSG")
    def respond(self, event, line):
        print(dir(self.basic_rfc))
        params = line.params

        if len(params) < 2:
            return

        if self.casecmp(self.basic_rfc.nick, params[0]):
            params = [line.hostmask.nick, choice(self.yifflines)]
        else:
            # Ensure it starts with us
            check_self = params[-1][:len(self.basic_rfc.nick)]
            if not self.casecmp(self.basic_rfc.nick, check_self):
                return

            params = [params[0], choice(self.flirtlines)]

        self.send("PRIVMSG", params)
