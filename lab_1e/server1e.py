'''
Created on 2017年9月14日

@author: wangweizhou
'''
from playground.network.packet.fieldtypes import UINT32, STRING, BUFFER,BOOL
from playground.network.packet import PacketType
from playground.network.common import StackingProtocol
from playground.network.common import StackingProtocolFactory
from playground.network.common import StackingTransport
import playground
from asyncio import *


class LoginRequestPacket(PacketType):
    DEFINITION_IDENTIFIER = "ClientLoginRequest"
    DEFINITION_VERSION = "1.0"
    FIELDS=[("usrname",STRING),("passwd",STRING)]
    

class ConfirmedAnswerPacket(PacketType):
    DEFINITION_IDENTIFIER = "ServerConfirmPacket"
    DEFINITION_VERSION="1.0"
    FIELDS=[("confirmedstatus",BOOL),("sessionID",STRING)]

class OperationRequestPacket(PacketType):
    DEFINITION_IDENTIFIER = "ClientOperationRequestPacket"
    DEFINITION_VERSION = "1.0"
    FIELDS=[("sessionID",STRING),("operation1",UINT32),("data1",BUFFER),("data2",BUFFER)]
    

class CreatLoginRequestpacket():
    def __init__(self, usrname, passwd):
        self.usrname = usrname
        self.passwd = passwd
    def createPacket(self):
        pkg = LoginRequestPacket()
        pkg.usrname=self.usrname
        pkg.passwd=self.passwd
        return pkg
class CreatConfirmedAnswerPacket():
    def __init__(self, confirmedstatus, sessionID):
        self.sessionID = sessionID
        self.confirmedstatus = confirmedstatus
    def createPacket(self):
        pkg = ConfirmedAnswerPacket()
        pkg.sessionID = self.sessionID
        pkg.confirmedstatus = self.confirmedstatus
        return pkg
class CreatOperationRequestPacket():
    def __init__(self, sessionID, operation1, data1, data2):
        self.sessionID = sessionID
        self.operation1 = operation1
        self.data1 = data1
        self.data2 = data2
    def createPacket(self):
        pkg = OperationRequestPacket()
        pkg.sessionID = self.sessionID
        pkg.operation1 = self.operation1
        pkg.data1 = self.data1
        pkg.data2 = self.data2
        return pkg

class ServerProtocol(Protocol):
    def __init__(self):
        self.transport=None        # transport contains the data you need to transfer while connecting
        self.deserializer = PacketType.Deserializer()
    def connection_made(self, transport):
        print("Server connected ")
        self.transport = transport
    
    def verifiedfunc(self, usrname, passwd):
        if usrname=="wwz" and passwd=="hellowwz":
            return True
        else:
            return False
        
    
    def data_received(self, data):
        print("Data received by server")
        self.deserializer.update(data)
        for pkg in self.deserializer.nextPackets():
            # logic section 
            if isinstance(pkg, LoginRequestPacket):
                print("Server:    Logging in request packet received!")
                print("Server:    Confirmed Answer Packet transported!")
                if self.verifiedfunc(pkg.usrname, pkg.passwd):
                    CAP = CreatConfirmedAnswerPacket(True, "sessionid0987")
                    CAPpkg = CAP.createPacket()
                    self.data=CAPpkg.__serialize__()
                    self.transport.write(self.data)
                else: 
                    self.transport.close()
                    print("Invalid usrname or passwd!")
            if isinstance(pkg, OperationRequestPacket):
                print("Server:    Operation Request Packet received!")
                print("Server:    Logging in Successfully!")
            
            
    def connection_lost(self, exc):
        print('Connection stopped because {}'.format(exc))
        
    
    
'''
    Protocol Stack
'''
class FirstUnderLayerProtocol(StackingProtocol):
    def __init__(self):
        super().__init__
        
    def connection_made(self,transport):
        self.transport=transport
        print("Layer 1 connected")
        higherTransport = StackingTransport(self.transport)
        self.higherProtocol().connection_made(higherTransport)
        
    def data_received(self,data):
        print("Data received by FIRST layer!")
        self.data = data
        self.higherProtocol().data_received(self.data)
    
    def connection_lost(self,exc):
        self.higherProtocol().connection_lost(exc)
        print('Connection stopped because {}'.format(exc))

class SecondUnderLayerProtocol(StackingProtocol):
    def __init__(self):
        super().__init__
        
    def connection_made(self,transport):
        self.transport=transport
        print("Layer 2 connected")
        higherTransport= StackingTransport(self.transport)
        self.higherProtocol().connection_made(higherTransport)

    
    def data_received(self,data):
        print("Data received by SECOND layer!")
        self.higherProtocol().data_received(data)
    
    def connection_lost(self,exc):    
        self.higherProtocol().connection_lost(exc)
        print('Connection stopped because {}'.format(exc))
    
if __name__=='__main__':
    loop = get_event_loop()
    f = StackingProtocolFactory(lambda: FirstUnderLayerProtocol(), lambda: SecondUnderLayerProtocol())
    ptConnector = playground.Connector(protocolStack=f)
    playground.setConnector('passthrough', ptConnector)
    coro = playground.getConnector('passthrough').create_playground_server(lambda:ServerProtocol(),8000)
    myserver= loop.run_until_complete(coro)
    loop.run_forever()
    myserver.close()
    loop.close()
    
    
    
    
    
