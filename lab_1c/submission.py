'''
Created on 2017年9月7日

@author: wangweizhou
'''
from playground.network.packet import PacketType
from playground.network.packet.fieldtypes import UINT32, STRING, BUFFER,BOOL
from asyncio import *
from playground.asyncio_lib.testing import TestLoopEx
from playground.network.testing import MockTransportToProtocol
from IPython.utils.sysinfo import pkg_commit_hash

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

        


    
class ClientProtocol(Protocol):   #protocol type is required
    def __init__(self):    #A 
                #serialize data transfer to message
        self.transport=None
        self.deserializer=PacketType.Deserializer()
    def connection_made(self, transport):     # Send message via transport.write
        print("Client:    Connection created!")
        self.transport = transport
        
        

    def data_received(self, data):
        self.deserializer.update(data)
        for pkg in self.deserializer.nextPackets():
            # logic section
            if isinstance(pkg, ConfirmedAnswerPacket):
                print("Client:    Confirmed Answer Packet received!")
                print("Client:    Operation Request packet transported!")
                ORP = CreatOperationRequestPacket("12345", 2 ,b"100" ,b"200")
                ORPpacket=ORP.createPacket()
                self.data = ORPpacket.__serialize__()
                self.transport.write(self.data)
                
    def Login(self,usrname,passwd):
        lrp = LoginRequestPacket()
        lrp.usrname = usrname
        lrp.passwd = passwd
        self.data = lrp.__serialize__()
        self.transport.write(self.data)
                
    

    def connection_lost(self, exc):
        print('Connection stopped because {}'.format(exc))
       
class ServerProtocol(Protocol):
    def __init__(self):
        
        self.transport=None        # transport contains the data you need to transfer while connecting
        self.deserializer = PacketType.Deserializer()
    def connection_made(self, transport):
        self.transport = transport
        self.state=1;
    
    def verifiedfunc(self, usrname, passwd):
        if usrname=="wwz" and passwd=="hellowwz":
            return True
        else:
            return False
        
    
    def data_received(self, data):
        self.deserializer.update(data)
        for pkg in self.deserializer.nextPackets():
            # logic section 
            if self.state==1 and isinstance(pkg, LoginRequestPacket):
                self.state+=1
                print("Server:    Logging in request packet received!")
                if self.verifiedfunc(pkg.usrname, pkg.passwd):
                    print("Server:    Confirmed Answer Packet transported!")
                    CAP = CreatConfirmedAnswerPacket(True, "sessionid0987")
                    CAPpkg = CAP.createPacket()
                    self.data=CAPpkg.__serialize__()
                    self.transport.write(self.data)
                else:
                    #self.transport.close()
                    print("Invalid usrname or passwd!")
                    print("Connection Closed!")
                    
            elif self.state==2 and isinstance(pkg, OperationRequestPacket):
                print("Server:    Operation Request Packet received!")
                print("Server:    Logging in Successfully!")
            else:
                #self.transport.close()
                pass
    def connection_lost(self, exc):
        print('Connection stopped because {}'.format(exc))

    
def basicUnitTest(): 
    # Build a MockConnection between Client and Server
    set_event_loop(TestLoopEx())
    client = ClientProtocol()       #sending data from the protocol
    server = ServerProtocol()
    transportToServer = MockTransportToProtocol(myProtocol=client)
    transportToClient = MockTransportToProtocol(myProtocol=server)
    transportToServer.setRemoteTransport(transportToClient)
    transportToClient.setRemoteTransport(transportToServer)
    server.connection_made(transportToClient)
    client.connection_made(transportToServer)
    client.Login("wwz", "hellowwz")
    
if __name__=='__main__':
    basicUnitTest()

    
    
    
    
    
    
    