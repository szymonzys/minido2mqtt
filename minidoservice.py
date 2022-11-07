#!/usr/bin/env python

import sys
import datetime

from twisted.internet import reactor
from twisted.internet.serialport import SerialPort

from twisted.python import usage
from twisted.application import service
from twisted.internet.defer import Deferred
from twisted.internet.protocol import ReconnectingClientFactory, ClientFactory

from mqttminidoservice import BridgeHandler
from minidopackage import strHex, CMD
from minidoprotocol import MinidoProtocol




class TCPClientOptions(usage.Options):
    optParameters = [
        ["server", "s", "192.168.1.249", "Remote TCP Server address"],
        ["port", "p", 1024, "Remote TCP Server port", int]
    ]


class SerialOptions(usage.Options):
    optParameters = [
        ["tty", "t", "/dev/ttyUSB0", "Serial port"]
    ]

class MinidoOptions(usage.Options):
    optFlags = [
        ["filter", "f", "Filter out most common commands from D2000"],
        ["verbose", "v", "Verbose mode prints all the messages"]
    ]

class MinidoServiceOptions(MinidoOptions):
    subCommands = [
        ["tcpclient", None, TCPClientOptions, "Connect to TCP Server for minido"],
        ["serial", None, SerialOptions, "Serial connection to minido over RS485"]
    ]



class MinidoFactory(ReconnectingClientFactory):
    def __init__(self, handler, filtering=False):
        self.done = Deferred()
        self.id = None
        self.handler = handler
        self.filtering = filtering


    def buildProtocol(self, addr):
        if not self.protocol:
            self.protocol = MinidoProtocol(self)
        return self.protocol

    def recv_message(self, chardata):
        if (not self.filtering) or (not CMD.ignoreCMD(chardata[4])):
            self.handler.receievedMessage(chardata)

    def printMessageText(self, message):
        print(str(datetime.datetime.now()) + ': ' + message)

    def printMessageHex(self, chardata):
        self.printBytesHex(chardata)

    def printBytesHex(self, chardata, extra = ""):
        print(str(datetime.datetime.now()) + extra + ': %s' % strHex(chardata))

class MinidoService(service.Service, BridgeHandler):
    def __init__(self, config):
        service.Service.__init__(self)
        BridgeHandler.__init__(self, config['verbose'])
        self.mode = config.subCommand
        self.filtering = config['filter']
        self.verbose = config['verbose']
        self.factory = MinidoFactory(self, self.filtering)
        self.filteredCommands = [0x3F, 0x21, 0x02, 0x03]

        if self.mode == 'tcpclient':
            self.factory.id = config.subOptions['server'] + ':' + str(config.subOptions['port'])
            self.port = config.subOptions['port']
            self.server = config.subOptions['server']
        elif self.mode == 'serial':
            self.factory.id = config.subOptions['tty']
            self.tty = config.subOptions['tty']

    def startService(self):
        if self.mode == 'tcpclient':
            reactor.connectTCP(self.server, self.port, self.factory)
        elif self.mode == 'serial':
            SerialPort(self.factory.buildProtocol(None), self.tty, reactor, baudrate='19200')

    def sendMessage(self, message):
        b = bytearray()
        b.extend(message)
        self.factory.protocol.send_data(b)


    def printMessage(self, message):
        self.factory.printMessageHex(message)

    def clientConnectionLost(self, connector, reason):
        print('Lost connection.  Reason:', reason)
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)


if __name__ == "__main__":
    config = MinidoServiceOptions()

    try:
        config.parseOptions()  # When given no argument, parses sys.argv[1:]
    except usage.UsageError as errortext:
        print('{}: {}'.format(sys.argv[0], errortext))
        print('{}: Try --help for usage details.'.format(sys.argv[0]))
        sys.exit(1)

    serv = MinidoService(config)
    serv.startService()
    reactor.run()
