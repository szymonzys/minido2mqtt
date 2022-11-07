# **- encoding: utf-8 -**
"""
    Minido-Unleashed is a set of programs to control a home automation
    system based on minido from AnB S.A.

    Please check http://kenai.com/projects/minido-unleashed/
    and also http://code.google.com/p/minido-unleashed/

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


    This program connects to a STOMP server, and allow dual way communication
    with the minido bus, checking the validity of the packet before sending.
"""

from twisted.internet.protocol import Protocol
from twisted.internet import task
import datetime
import time

from minidopackage import checksum, MINIDOSTART, Pdu, CommandPdu, CMD, MINIDO, MiniPduFactory


class MinidoProtocol(Protocol):
    """
    Bus protocol (low level), also used for Minido, D2000 and C2000
    This class only assemble and validate the packet, but does not decode is.
    This class can also check the checksum of incoming packets, 
    or add the missing checksum before sending packets.
    The decoding is left to the MinidoProtocolDecoder class when receiving
    new packet.
    """
    chardata = list()
    def __init__(self, factory, kalive=0.0, d2000 = False):
        Protocol.__init__(self)
        self.factory = factory
        print('MinidoProtocol initialized')
        self.factory.connections = list()
        self.kalive = kalive

        #used for delayed send message strategy
        self.lastmsgtime = ( datetime.datetime.now() 
            - datetime.timedelta(microseconds=10000))

        #used for D2000 send message strategy
        self.d2000Strategy = d2000
        self.queue = []
        self.pduFactory = MiniPduFactory()

    def connectionMade(self):
        print(str(datetime.datetime.now()) + " :" +
            "New connection :" + self.factory.id)
        self.factory.connections.append(self)
        if self.kalive > 0.0:
            print('Starting the keepalive loop every ' + str(self.kalive) + ' seconds.')
            self.loopingcall = task.LoopingCall(self.keepalive)
            self.loopingcall.start(self.kalive)
        else:
            print('Keepalive disabled for this connection')

    def connectionLost(self, reason):
        self.factory.connections.remove(self)
        print("Lost connection : " + self.factory.id + " Reason : " + str(reason))
        if self.kalive > 0.0:
            self.loopingcall.stop()

    def newpacket(self, data):
        """ Called when a new packet is validated """
        self.factory.recv_message(data)
        self.lastmsgtime = datetime.datetime.now()
        self.send_data_from_queue_after_packet(data)

    def send_data(self, data):
        if data[len(data) - 1] == checksum(data[4:(len(data) - 1)]):
            self.send_data_strategy(data)
        else:
            # First check if the packet is complete,
            # and build the missing checksum.
            if len(data) == data[3] + 3:
                print(str(datetime.datetime.now()) + " :",
                      "Adding the missing checksum")
                data.append(checksum(data[4:(len(data))]))
                self.send_data_strategy(data)

            else:
                print(str(datetime.datetime.now()) + " : " +
                      'Bad checksum for packet : ' + str(' '.join(
                    ['%0.2x' % c for c in data])))

    def send_data_strategy(self, data):
        if self.d2000Strategy:
            self.queue.append(data)
        else:
            self. send_data_delayed(data)

    def send_data_from_queue_after_packet(self, prvedata):
        packet = self.pduFactory.createPdu(prvedata)

        #When detected D2000 changed strategy for sending data to avoid collision
        if packet.src == MINIDO.D2000:
            self.d2000Strategy = True

        if self.d2000Strategy:
            if  isinstance(packet, CommandPdu) and packet.command == CMD.BUS_TOKEN_GRANT and packet.dst == MINIDO.PC:
                self.send_data_from_queue()

    def send_data_from_queue(self):
        if len(self.queue) > 0:
            data = self.queue.pop()
            self.send_data_now(data)

    def send_data_now(self, data):
        # TODO: This can be improved for collision detection,
        #  eg. low level queue and retransmitted if collision detected
        self.transport.write(bytes(data))

    def send_data_delayed(self, data):
        timed = datetime.datetime.now() - self.lastmsgtime
        if timed < datetime.timedelta(microseconds=10000):
            print('Delayed send_data by 0.01s')
            time.sleep(0.01)
        self.lastmsgtime = datetime.datetime.now()
        self.send_data_now(data)

    def dataReceived(self, chardata):
        """ This method is called by Twisted  """
        self.chardata.extend(chardata)
        # The smallest packets are 6 bytes long. So even if the data length is
        # in 4th position, we need at least 6 bytes with the checksum.
        while len(self.chardata) >= 6:
            if self.chardata[0] != MINIDOSTART:
                startidx = 0
                try:
                    startidx = self.chardata.index(MINIDOSTART)
                except(LookupError, ValueError):
                    # We did not find 0x23
                    # We are not interested in data not starting by 0x23.
                    self.factory.printBytesHex(self.chardata, " Error: none is 0x23. Dropping everything: ")
                    self.chardata = list()
                    continue

                if startidx != 0:
                    #self.factory.printBytesHex(self.chardata[0:startidx], " Warning: Deleting first characters : StartIDX = " + str(startidx))
                    self.chardata = self.chardata[startidx:]
                    continue
            else:
                """ We have a valid begining """
                datalength = self.chardata[3]
                if len(self.chardata) >= datalength + 4:
                    """ We have at least a complete packet"""
                    if checksum(
                        [x for x in self.chardata[4:datalength + 3]]
                        ) != (self.chardata[datalength + 3]):
                        self.factory.printBytesHex(self.chardata, " Warning: Invalid checksum for packet: ")

                        validpacket = self.chardata[0:datalength + 4]
                        self.chardata = self.chardata[datalength + 4:]
                        continue
                    else:
                        validpacket = self.chardata[0:datalength + 4]
                        self.chardata = self.chardata[datalength + 4:]
                    # OK, I have now a nice, beautiful, valid packet
                    data = [x for x in validpacket]
                    self.newpacket(data)
                else:
                    #print("Debug packet : " + str(map(lambda x: ord(x), self.chardata)))
                    #print("Debug ord(self.chardata[3]) : " + str(datalength))
                    break

    def keepalive(self):
         self.send_data([0x31, 0x00, 0x00, 0x01, 0x00])
 
