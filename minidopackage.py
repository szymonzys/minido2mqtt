# **- encoding: utf-8 -**
from aenum import Enum, Constant

MINIDOSTART = 0x23

def checksum(datalist):
    """ Calculate an XOR checksum """
    checksum_ = 0
    for item in datalist:
        checksum_ ^= item
    return checksum_

def strHex(chardata):
    return ' '.join(map(lambda i: '{0:02X}'.format(i), chardata))

def strValue(value):
    if STATUS.isValueIn(value):
        return STATUS(value).name
    return str(value)

EXOOFFSET = 0x3B
EXIOFFSET = 0x13

# Packet fields
class PacketOffset(Constant):
    DST = 1
    SRC = 2
    LEN = 3
    COM = 4
    PAR = 5


class MINIDO(Enum):
    PC = 0x00
    D2000 = 0x01
    CONSOLE = 0x0B
    EXI01 = 0x14
    EXI02 = 0x15
    EXI03 = 0x16
    EXI04 = 0x17
    EXI05 = 0x18
    EXI06 = 0x19
    EXI07 = 0x1A
    EXI08 = 0x1B
    EXI09 = 0x1C
    EXI10 = 0x1D
    EXI11 = 0x1E
    EXI12 = 0x1F
    EXI13 = 0x20
    EXI14 = 0x21
    EXI15 = 0x22
    EXI16 = 0x23
    EX_UNKN_25 = 0x25      # Responds in my D2000
    EXO01 = 0x3C
    EXO02 = 0x3D
    EXO03 = 0x3E
    EXO04 = 0x3F
    EXO05 = 0x40
    EXO06 = 0x41
    EXO07 = 0x42
    EXO08 = 0x43
    EXO09 = 0x44
    EXO10 = 0x45
    EXO11 = 0x46
    EXO12 = 0x47
    EXO13 = 0x48
    EXO14 = 0x49
    EXO15 = 0x4A
    EXO16 = 0x4B

    def isExo(self):
        return self.value >= MINIDO.EXO01.value and self.value <= MINIDO.EXO16.value

    def isExi(self):
        return self.value >= MINIDO.EXI01.value and self.value <= MINIDO.EXI16.value

class EndPoint:
    SEPARATOR = "-"

    def __init__(self, minido, number = 0):
        self.minido = minido
        self.number = number

    def __str__(self):
        if (self.number == 0):
            return self.minido.name
        else:
            return self.minido.name + EndPoint.SEPARATOR + str(self.number)

    def isLeaf(self):
        return self.number != 0

    @classmethod
    def exoEndpoint(cls, exoUnitId, endpointId):
        return EndPoint(MINIDO(exoUnitId + EXOOFFSET), endpointId)

    @classmethod
    def exiEndpoint(cls, exiUnitId, endpointId):
        return EndPoint(MINIDO(exiUnitId + EXIOFFSET), endpointId)

    @classmethod
    def endpoint(cls, message):
        if message == "None":
            return None
        split = str(message).split(EndPoint.SEPARATOR)
        if len(split) == 1:
            return EndPoint(MINIDO[split[0]])
        else:
            return EndPoint(MINIDO[split[0]], int(split[1]))



class CMD(Enum):
    NONE = 0x00  # Fake command
    EXO_UPDATE = 0x01  # Packet to update all the outputs of an EXO
    EXI_STATUS = 0x25  # Exi state changed
    UNK_CONSOLE_PRINT = 0x02  # Used by D2000, to print message on console
    UNK_CONSOLE_03 = 0x03  # Used by D2000, communicate with console, comes after two 0x02 messages
    D2000_UNK15_GET = 0x15  # Used by PC to get status of all ???: could be bits, could be seqencers ??? in single request, params (01,00), responce 64 elements
    D2000_EXI_GET = 0x0A  # Used by PC to get status of all EXI in two request, params (01,00) and (01,01)
    D2000_EXO_GET = 0x18  # Used by PC to get status of all EXO in single request, params (01,00)
    D2000_UNK23_GET = 0x23  # Used by PC to get status of all ???: could be bits, could be seqencers ??? in single request, params (01,00), responce 12 elements
    BUS_TOKEN_GRANT = 0x3F  # Used by D2000 for granting communication slot for 1 message
    BUS_TOKEN_REFUSE = 0x21  # Used by D2000 for refusing communication slot
    EXICENT = 0x31  # Not faced with my D2000
    EXI_ECHO_REQUEST = 0x39  # Not faced with my D2000
    EXI_ECHO_REPLY = 0x38  # Not faced with my D2000
    EXO_ECHO_REQUEST = 0x49  # Not faced with my D2000
    EXO_ECHO_REPLY = 0x05  # Not faced with my D2000

    @staticmethod
    def ignoreCMD(value):
        cmd = CMD(value)

        if cmd.name[:3] in ("UNK", "BUS"):
            return True
        return False


class STATUS(Enum):
    OFF = 0x00
    ON = 0xFF
    Pulse = 0xFB

    @staticmethod
    def isValueIn(value):
        return value in map(lambda x: x.value, list(STATUS))




class Pdu():
    def __init__(self, chardata = None):
        if(chardata):
            self.chardata = list()
            self.chardata.extend(chardata)
        else:
            self.chardata = [MINIDOSTART, None, None, 2, CMD.NONE, None]

    @property
    def src(self):
        return MINIDO(self.chardata[PacketOffset.SRC])
    @src.setter
    def src(self, value):
        self.chardata[PacketOffset.SRC] = int(value.value)

    @property
    def dst(self):
        return MINIDO(self.chardata[PacketOffset.DST])
    @dst.setter
    def dst(self, value):
        self.chardata[PacketOffset.DST] = int(value.value)

    @property
    def datalen(self):
        return self.chardata[PacketOffset.LEN]
    @datalen.setter
    def datalen(self, value):
        lendelta = value - self.datalen
        if(lendelta < 0):
            self.chardata = self.chardata[:lendelta]
            self.chardata[self.datalen + PacketOffset.LEN] = None
        elif(lendelta > 0):
            self.chardata[self.datalen + PacketOffset.LEN] = None
            for n in range(lendelta):
                self.chardata.append(None)
        self.chardata[PacketOffset.LEN] = value

    @property
    def chk(self):
        if(len(self.chardata) > (self.datalen + PacketOffset.LEN)):
            return self.chardata[self.datalen + PacketOffset.LEN]
        else:
            return None

    @property
    def payload(self):
        return self.chardata[PacketOffset.COM:PacketOffset.COM+self.datalen - 1]

    def copy2payload(self, src, size, payloadIndex):
        ret = True
        for i in range(size):
            val = src[i]
            self.chardata[PacketOffset.COM + payloadIndex + i] = val
            if val is None:
                ret = False
        return ret

    def checksum(self):
        return checksum(self.payload)

    def setchk(self):
        self.chardata[self.datalen + PacketOffset.LEN] = self.checksum()

    def isOk(self):
        return self.chardata[PacketOffset.SRC] is not None and self.chardata[PacketOffset.DST] is not None and (self.chk == self.checksum())

    def isCommand(self):
        return isinstance(self, CommandPdu)

    def getpdu(self):
        self.setchk()
        return self.chardata

    def __str__(self):
        return "{src}->{dst}, {payload} {ok} {extra}".format(src=self.src.name, dst=self.dst.name, payload=self._strPayload(), ok=self._strOk(), extra=self._strExtra())

    def _strPayload(self):
        return "payload: {pld}".format(pld=strHex(self.payload))

    def _strOk(self):
        if not self.isOk():
            return " <<< ERROR: CHECKSUM"
        else:
            return ""

    def _strExtra(self):
        return ""



class CommandPdu(Pdu):
    def __init__(self, chardata = None):
        Pdu.__init__(self, chardata)


    def setcommand(self, command, paramsLen = 0):
        self.command = command
        self.datalen = paramsLen + 2

    @property
    def command(self):
        return CMD(self.chardata[PacketOffset.COM])

    @command.setter
    def command(self, value):
        self.chardata[PacketOffset.COM] = int(value.value)

    @property
    def params(self):
        return self.payload[1:]

    def setparam(self, i, value):
        self.chardata[PacketOffset.PAR + i] = int(value)

    def _strPayload(self):
        str = "{cmd}{params}".format(cmd=self.command.name, params=self._strParams())

        return str

    def _strParams(self):
        if (len(self.params) > 0):
            return ", params: {pld}".format(cmd=self.command, pld=strHex(self.params))
        return ""


class ExiStatusPdu(CommandPdu):
    def __init__(self, chardata = None):
        CommandPdu.__init__(self, chardata)
        if(self.command != CMD.EXI_STATUS):
            self.setcommand(CMD.EXI_STATUS, 6)

    def setcommand(self, command = CMD.EXI_STATUS, paramsLen = 0):
        super().setcommand(CMD.EXI_STATUS, 6)
        self.setparam(0, 0x00)
        self.setparam(1, 0x00)
        self.setparam(5, 0x01)

    @property
    def endpoint(self):
        params = self.params
        return EndPoint.exiEndpoint(params[2] + 1, params[3] + 1)

    @endpoint.setter
    def endpoint(self, value):
        self.setparam(2, value.minido.value - EXIOFFSET - 1)
        self.setparam(3, value.number - 1)

    @property
    def endpointValue(self):
        return self.params[4]

    @endpointValue.setter
    def endpointValue(self, value):
        self.setparam(4, value)


    @property
    def valueStr(self):
        return strValue(self.valueInt)

    @property
    def valueInt(self):
        byte = self.params[4]
        if self.params[5] == 1:
            return byte
        else:
            return (-1) * byte


    @property
    def valueTemp(self):
        byte = self.valueInt
        return (0.5) * byte

    def _strParams(self):
        return ", {ep}={val}".format(ep=self.endpoint, val=self.valueStr)

    def _strExtra(self):
        value = self.params[4]
        if (not STATUS.isValueIn(value)):
            return " ### TEMP: " + str(self.valueTemp) + " C ###"
        return ""


class ExoUpdatePdu(CommandPdu):
    def __init__(self, chardata = None):
        CommandPdu.__init__(self, chardata)
        if(self.command != CMD.EXO_UPDATE):
            self.setcommand(CMD.EXO_UPDATE, 8)

    def endpoint(self, paramId):
        return EndPoint.exoEndpoint(self.dst.value - EXOOFFSET, paramId + 1)

    def status(self):
        return list(map(lambda x: self.strValue(x), self.params))


    def strValue(self, value):
        if STATUS.isValueIn(value):
            return strValue(value)
        else:
            return str(value) + "%"

    def _isDimer(self):
        p = self.params
        return not (STATUS.isValueIn(p[0]) and STATUS.isValueIn(p[1]) and STATUS.isValueIn(p[2]) and STATUS.isValueIn(p[3]))


    def _strParams(self):
        status = self.status()
        r = 8
        if self._isDimer():
            r = 4
        return ", " + ' '.join(map(lambda i: "{ep}={st}".format(ep=self.endpoint(i), st=status[i]), range(0, r)))

    def _strExtra(self):
        if (self._isDimer()):
            return " ### DIMER ###"
        return ""

class MiniPduFactory():
    def __init__(self):
        self.__lastCMD = CMD.NONE

    def createPdu(self, chardata):
        if self.__lastCMD.name.endswith('_GET'):
            self.__lastCMD = CMD.NONE
            return Pdu(chardata)
        else:
            try:
                cmdpdu = CommandPdu(chardata)
                self.__lastCMD = cmdpdu.command

                if self.__lastCMD == CMD.EXI_STATUS:
                    cmdpdu = ExiStatusPdu(cmdpdu.chardata)
                elif self.__lastCMD == CMD.EXO_UPDATE:
                    cmdpdu = ExoUpdatePdu(cmdpdu.chardata)
                return cmdpdu
            except:
                packet = Pdu(chardata)
                print("Unknown PDU Structure: " + str(packet))
                return packet
