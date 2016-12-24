#!/usr/bin/python

import sys
import socket
import string
from PyQt5 import QtWidgets, uic, QtCore

formClass = uic.loadUiType('main.ui')[0]

class MainWindow(QtWidgets.QMainWindow, formClass):
  
  HOST = 'irc.freenode.net'
  PORT = 6667
  NICK = 'julie_bot'
  IDENT = 'julie'
  REALNAME = 'Julie'
  readbuffer = ''
  
  def __init__(self):
    super(MainWindow, self).__init__()
    self.setupUi(self)
    self.actionConnect.triggered.connect(self.sayHi)
    self.actionExit_2.triggered.connect(self.close)
    
    s = socket.socket( )
    #s.connect((self.HOST, self.PORT))
    #s.send('NICK %s\r\n' % self.NICK.encode('utf-8'))
    #s.send("USER %s %s bla :%s\r\n" % (self.IDENT, self.HOST, self.REALNAME))
    
    self.mainStatus.setPlainText('teste')
    
  def sayHi(self):
    print('hi')
    
if __name__ == '__main__':
  app = QtWidgets.QApplication(sys.argv)
  window = MainWindow()
  window.show()
  sys.exit(app.exec_())
