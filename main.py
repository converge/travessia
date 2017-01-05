#!/usr/bin/env python3.5

import sys
import asyncio
import ssl
import signal

# PyQt5
from PyQt5 import QtWidgets, uic

from random import choice
from logging import basicConfig

# IRC
import asyncio
import ssl
import signal

from PyIRC.signal import event
from PyIRC.io.asyncio import IRCProtocol
from PyIRC.extensions import bot_recommended

formClass = uic.loadUiType('main.ui')[0]

class MainWindow(QtWidgets.QMainWindow, formClass):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.actionConnect.triggered.connect(self.connect_irc)
        self.actionDisconnect.triggered.connect(self.disconnect_irc)
        self.actionExit_2.triggered.connect(self.close)
        self.mainStatus.setPlainText('teste')

    def disconnect_irc(self):
        print('disconnect')

    async def connect_irc(self):

        basicConfig(level="DEBUG")

        # @todo: place it in a file / preference window
        args = {
            'serverport': ('irc.freenode.net', 6667),
            'ssl': False,
            'username': 'jpbot',
            'nick': 'jpbot',
            'gecos': 'hello everybody',
            'extensions': bot_recommended,
            'join': ['#bot7'],
        }

        def sigint(*protos):
            for proto in protos:
                try:
                    proto.send("QUIT", ["Terminating due to ctrl-c!"])
                    proto.close()
                except Exception as e:
                    # Ugh! A race probably happened. Yay, signals.
                    pass

            print()
            print("Terminating due to ctrl-c!")

            quit()

        # IRC connect
        inst = TestProtocol(**args)
        coro = await inst.connect()

class EchoClientProtocol(asyncio.Protocol):
    def __init__(self, message, loop):
        self.message = message
        self.loop = loop

    def connection_made(self, transport):
        transport.write(self.message.encode())
        print('Data sent: {!r}'.format(self.message))

    def data_received(self, data):
        print('Data received: {!r}'.format(data.decode()))

    def connection_lost(self, exc):
        print('The server closed the connection')
        print('Stop the event loop')
        self.loop.stop()

class TestProtocol(IRCProtocol):

    yifflines = (
        "right there~",
        "mmmm yes~",
    )

    flirtlines = (
        "not in here! message me",
        "I don't do it in channels, sorry...",
    )

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

    # overrided
    def connect(self):
        print('hi')
        # (PyIRC connect)
        #return loop.create_connection(lambda: self, self.server, self.port, ssl=self.ssl)
        # testing at local server
        return loop.create_connection(lambda: EchoClientProtocol(message, loop), '127.0.0.1', 8888)


async def runPyQt():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(runPyQt())
    loop.run_forever()
