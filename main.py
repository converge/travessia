#!/usr/bin/env python3.5

from TravessiaProtocol import TravessiaProtocol

import sys
import asyncio
from logging import basicConfig

# PyQt5
from PyQt5 import uic
from PyQt5.QtWidgets import (QMainWindow, QMessageBox, QWidget, QTextEdit,
                             QApplication)

# from PyQt5 import QtCore, QtGui, QtWidgets, uic

# quamash
from quamash import QEventLoop

# PyIRc
from PyIRC.extensions import bot_recommended

formClass = uic.loadUiType('main.ui')[0]


class MainWindow(QMainWindow, formClass):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setGeometry(400, 250, 661, 51)
        self.setupUi(self)

        # QT signals
        self.actionConnect.triggered.connect(self.connect)
        self.actionDisconnect.triggered.connect(self.disconnect)
        self.actionExit.triggered.connect(self.close)
        self.actionAbout.triggered.connect(self.about)
        self.mainInput.returnPressed.connect(self.send)
        self.activeChats.currentRowChanged.connect(self.display)

        self.activeChats.insertItem(0, 'irc.freenode.net')
        self.activeChats.insertItem(1, '#python')

        self._server = None
        self._task = None
        self._server_running = None

    # QT slots
    def createChat(self, chatName):
        nextIndex = self.activeChats.count() + 1
        self.activeChats.insertItem(nextIndex, chatName)
        self.teste = QWidget()
        self.telaChat = QTextEdit(self.teste)
        self.telaChat.append('teste ' + str(nextIndex))
        self.mainStackedWidget.addWidget(self.telaChat)

        # self.activeChats.insertItem(2, chatName)
        self.mainStackedWidget.setCurrentIndex(2)

    def about(self):
        QMessageBox.about(self, 'About',
                                '<center>Travessia IRC Client (0.1)<br><br>'
                                'João Vanzuita (converge)<p> <a '
                                'href="https://github.com/converge/travessia">'
                                'https://github.com/converge/travessia</a></p>'
                                '</center>')

    def display(self, i):
        self.mainStackedWidget.setCurrentIndex(i)

    def send(self):
        message = self.mainInput.text()

        # removes the slash before command
        message = message.lstrip('/')

        messageList = message.split()
        command = None
        params = []

        if len(messageList) >= 1:
            command = messageList[0]
            messageList.pop(0)
            params = messageList
            self._server.send(command, params)

    def close(self):
        self.disconnect()
        return super().close()

    def connect(self):

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
                except:
                    # Ugh! A race probably happened. Yay, signals.
                    pass

            print()
            print("Terminating due to ctrl-c!")

            quit()

        # IRC connect
        self._server = TravessiaProtocol(self, **args)
        self._task = asyncio.ensure_future(self._server.connect())
        self._server_running = True

    def disconnect(self):
        print('quit')
        if self._server_running:
            try:
                self._server.send("QUIT", ["Bye!"])
                self._server.close()
                self._task.cancel()
            except Exception as e:
                print(e)
            finally:
                self._server_running = False
                self._server = None
                self._Task = None


app = QApplication(sys.argv)
loop = QEventLoop(app)
asyncio.set_event_loop(loop)

if __name__ == '__main__':
    # initialize window
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

    # asyncio loop
    try:
        loop.run_forever()
    finally:
        loop.close()
