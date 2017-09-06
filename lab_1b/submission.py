'''
Created on Sep 5, 2017

@author: root
'''
from playground.network.packet import PacketType
from playground.network.packet.fieldtypes import UINT32, STRING, BUFFER,BOOL
from oauthlib.oauth2.rfc6749 import catch_errors_and_unavailability
from symbol import except_clause
from logging import basicConfig
class LoginRequestPacket(PacketType):
    DEFINITION_IDENTIFIER = "ClientLoginRequest"
    DEFINITION_VERSION = "1.0"
    FIELDS=[("usrname",BUFFER),("passwd",BUFFER)]
    

class ConfirmedAnswerPacket(PacketType):
    DEFINITION_IDENTIFIER = "ServerConfirmPacket"
    DEFINITION_VERSION="1.0"
    FIELDS=[("confirmedstatus",BOOL),("sessionID",STRING)]

class OperationRequestPacket(PacketType):
    DEFINITION_IDENTIFIER = "ClientOperationRequestPacket"
    DEFINITION_VERSION = "1.0"
    FIELDS=[("sessionID",STRING),("operation1",UINT32),("data1",BUFFER),("data2",BUFFER)]

def basicUnitTest1():
    # packet1
    packet1=LoginRequestPacket()
    packet1.usrname=b"wwz"
    packet1.passwd=b"1234"
    #packet2
    packet2=ConfirmedAnswerPacket()
    packet2.confirmedstatus=1
    packet2.sessionID="wwz1234"
    #packet3
    packet3=OperationRequestPacket()
    packet3.sessionID="wwz1234"
    packet3.operation1=1
    packet3.data1=b"hello"
    packet3.data2=b"world"
    pkyBytes=packet1.__serialize__() + packet2.__serialize__() + packet3.__serialize__()
    print("serialized Success!")
def basicUnitTest2():
    packet3=OperationRequestPacket()
    packet3.sessionID="wwz1234"
    packet3.operation1=1
    packet3.data1=b"hello"
    packet3.data2=b"world"
    pkyBytes=packet3.__serialize__()
    packet3check = PacketType.Deserialize(pkyBytes)
    if packet3check==packet3:
        print("These two packages are the same!")
def basicUnitTest3():
    packet3=OperationRequestPacket()
    packet3.sessionID="wwz1234" 
    packet3.data1=b"hello"
    packet3.data2=b"world"
    try:
        packet3.operation1=-1
    except:  
        print("Invalid value")  \
        
def basicUnitTest4():
    packet2=ConfirmedAnswerPacket()
    packet2.confirmedstatus=1
    packet2.sessionID="wwz1234"
    packet3=OperationRequestPacket()
    packet3.sessionID="wwz1234" 
    packet3.data1=b"hello"
    packet3.data2=b"world"
    packet3.operation1=1
    pkgBytes = packet2.__serialize__() + packet3.__serialize__()
    deserializer = PacketType.Deserializer()
    deserializer.update(pkgBytes)
    for packet in deserializer.nextPackets():
        if packet == packet2: print("This is packet2")
        if packet == packet3: print("This is packet3")

if __name__=="__main__":
    basicUnitTest1()
    basicUnitTest2()
    basicUnitTest3()
    basicUnitTest4()