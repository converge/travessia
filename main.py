#!/usr/bin/env python3.5

import sys
import asyncio
import yaml

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
        self.activeChats.insertItem(0, 'status')
        self.activeChats.insertItem(1, 'bug')

        self._server = None
        self._task = None
        self._serverRunning = None
        self.cfg = None

        # dict to retrieve Widgets and QTextEdits to be showed in main window
        self.chatWidgets = {}
        self.chatWindows = {}

    def dataReceived(self, command, params, nick):
        ''' receive data from user/server and take actions '''

        # channel name
        channelName = params[0]

        msg = ' '.join(params[1:])

        # join channel
        if command == 'JOIN' and \
                channelName.startswith('#') and \
                self.isChatCreated(channelName) is False:

            self.createChat(channelName)

        # part channel
        elif command == 'PART' and \
                channelName.startswith('#') and \
                self.isChatCreated(channelName) is True:

            self.removeChat(channelName)

        # join channel
        elif command == 'PRIVMSG' and \
                channelName.startswith('#') and \
                self.isChatCreated(channelName) is False:

            self.createChat(channelName, msg)

        # send msg to channel
        elif command == 'PRIVMSG' and \
                channelName.startswith('#') and \
                self.isChatCreated(channelName) is True:

            self.chatWindows[channelName].append('<'
                                                 + nick
                                                 + '> '
                                                 + msg)

        else:
            self.statusServerInfo.append(msg)

    # methods
    def createChat(self, chatName, msg=None):
        ''' create a new chat screen '''
        nextIndex = self.activeChats.count() + 1
        self.activeChats.insertItem(nextIndex, chatName)
        self.chatWidgets[chatName] = QWidget()
        self.chatWindows[chatName] = QTextEdit(self.chatWidgets[chatName])

        if msg is not None:
            self.chatWindows[chatName].append(msg)

        self.mainStackedWidget.addWidget(self.chatWindows[chatName])

    def removeChat(self, chatName):
        item = self.activeChats.findItems(chatName, Qt.MatchExactly)
        for i in item:
            self.activeChats.takeItem(self.activeChats.row(i))

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
        self.mainInput.setFocus()

    def send(self):

        # if not connected, clean input and exit
        if not self._serverRunning:
            self.mainInput.clear()
            return

        message = self.mainInput.text()

        command = None
        params = []

        if message.startswith('/'):
            message = message.lstrip('/')
            messageList = message.split()
            command = messageList[0]
            params = messageList[1:]
            self._server.send(command, params)
        else:
            command = 'PRIVMSG'
            chatName = self.activeChats.currentItem().text()
            params.append(chatName)
            params.append(self.mainInput.text())
            self._server.send(command, params)
            self.chatWindows[chatName].append('<'
                                              + self.cfg['userInfo']['nick']
                                              + '> '
                                              + str(params[1]))

        self.mainInput.clear()

    def close(self):
        self.disconnect()
        return super().close()

    def connect(self):

        with open('config.yml', 'r') as ymlfile:
            self.cfg = yaml.load(ymlfile)

        config = {
            'serverport': (self.cfg['serverInfo']['host'],
                           self.cfg['serverInfo']['port']),
            'ssl': self.cfg['serverInfo']['ssl'],
            'username': self.cfg['userInfo']['username'],
            'nick': self.cfg['userInfo']['nick'],
            'gecos': self.cfg['userInfo']['gecos'],
            'extensions': bot_recommended
        }

        def sigint(*protos):
            for proto in protos:
                try:
                    proto.send("QUIT", ["Terminating due to ctrl-c!"])
                    proto.close()
                except:
                    # Ugh! A race probably happened. Yay, signals.
                    pass

            quit()

        # IRC connect
        self._server = TravessiaProtocol(self, **config)
        self._task = asyncio.ensure_future(self._server.connect())
        self._serverRunning = True

        self.activeChats.item(0).setText(self.cfg['serverInfo']['host'])

    def disconnect(self):
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
