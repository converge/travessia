import asyncio
from random import choice

# PyIRC
from PyIRC.signal import event
from PyIRC.io.asyncio import IRCProtocol
from PyIRC.line import Line


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
        print('&&&')
        print(data)
        data = self.data + data

        lines = data.split(b'\r\n')
        # removes the byte assignment, ex. [b':whelm.freenode.net 482']
        self.data = lines.pop()

        for line in lines:
            line = Line.parse(line.decode('utf-8', 'ignore'))

            # send datas to window/qt control its behavior
            self.window.dataReceived(line.command,
                                     line.params,
                                     line.hostmask.nick)

            try:
                super().recv(line)
            except Exception:
                # We should never get here!
                self.send("QUIT", ["Exception received!"])
                self.transport.close()

                # This is fatal and needs to be reported so stop the event
                # loop.
                loop = asyncio.get_event_loop()
                loop.stop()

                raise

    @event("commands", "PRIVMSG")
    def respond(self, event, line):
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
            print(params)

        self.send('PRIVMSG', params)
        self.window.dataReceived('PRIVMSG', params, self.basic_rfc.nick)
