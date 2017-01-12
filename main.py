#!/usr/bin/env python3.5

import sys
import asyncio

# travessia
from TravessiaProtocol import TravessiaProtocol

# PyQt5
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QMessageBox, QWidget, QTextEdit,
                             QApplication)

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

        # @todo: create it dynamically
        # BUG: if I have only one activeChat window, when I create a new
        # window(channel), it wont show up self.dataReceived content
        self.activeChats.insertItem(0, 'irc.freenode.net')
        self.activeChats.insertItem(1, '#python')

        self._server = None
        self._task = None
        self._serverRunning = None

        # dict to retrieve Widgets and QTextEdits to be showed in main window
        self.chatWidgets = {}
        self.chatWindows = {}

    def dataReceived(self, command, params):
        ''' receive data from user/server and take actions '''
        # channel name
        firstParam = params[0]
        msg = params[1]

        if command == 'JOIN' and firstParam[0] == '#':
            self.createChat(firstParam)

        if command != 'PRIVMSG' and firstParam[0] != '#':
            self.statusServerInfo.append(''.join(command) + ''.join(params))

        # join channel
        if command == 'PRIVMSG' and \
           firstParam[0] == '#' and \
           self.isChatCreated(firstParam) is False:

                self.createChat(firstParam, msg)

        # send msg to channel
        elif command == 'PRIVMSG' and \
            firstParam[0] == '#' and \
                self.isChatCreated(firstParam) is True:

            self.chatWindows[firstParam].append(msg)

        else:
            self.statusServerInfo.append(msg)

    # methods
    def createChat(self, chatName, msg=None):
        ''' create a new chat screen '''
        print(self.activeChats.count())
        nextIndex = self.activeChats.count() + 1
        print(nextIndex)
        self.activeChats.insertItem(nextIndex, chatName)
        self.chatWidgets[chatName] = QWidget()
        self.chatWindows[chatName] = QTextEdit(self.chatWidgets[chatName])

        if msg is not None:
            self.chatWindows[chatName].append(msg)

        self.mainStackedWidget.addWidget(self.chatWindows[chatName])

    def isChatCreated(self, chatName):
        ''' verify if chat has been created '''
        chat = self.activeChats.findItems(chatName, Qt.MatchExactly)
        if len(chat) == 0:
            return False
        return True

    # QT slots
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

        # if not connected, clean input and exit
        if not self._serverRunning:
            self.mainInput.clear()
            return

        message = self.mainInput.text()

        # removes the slash before command
        message = message.lstrip('/')

        messageList = message.split()
        command = None
        params = []

        # it's still bad, I'm working here atm
        if len(messageList) > 1:
            command = messageList[0]
            messageList.pop(0)
            params = messageList
            self._server.send(command, params)
        else:
            chatName = self.activeChats.currentItem().text()
            params.insert(0, chatName)
            params.append(self.mainInput.text())
            print(params)
            self._server.send('PRIVMSG', params)
            self.chatWindows[chatName].append(str(params))

        self.mainInput.clear()

    def close(self):
        self.disconnect()
        return super().close()

    def connect(self):

        # @todo: place it in a file / preference window
        args = {
            'serverport': ('127.0.0.1', 6667),
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
        self._serverRunning = True

    def disconnect(self):
        print('quit')
        if self._serverRunning:
            try:
                self._server.send("QUIT", ["Bye!"])
                self._server.close()
                self._task.cancel()
            except Exception as e:
                print(e)
            finally:
                self._serverRunning = False
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
