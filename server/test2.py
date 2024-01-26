from pysnmp.hlapi import *
import sys
def walk_disk_desc(host, oid):
    for (errorIndication,
     errorStatus,
     errorIndex,
     varBinds) in nextCmd(SnmpEngine(), 
                          CommunityData('public'),
                          UdpTransportTarget((host, 161)),
                          ContextData(),                                                           
                          ObjectType(ObjectIdentity(oid)),
                          lexicographicMode=False):
        if errorIndication:
            print(errorIndication, file=sys.stderr)
            break
        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?'), 
                                file=sys.stderr)             
            break
        else:
            for varBind in varBinds:
                print(varBind)
                
def walk_disk_usage(host, oid):
    for (errorIndication,
     errorStatus,
     errorIndex,
     varBinds) in nextCmd(SnmpEngine(), 
                          CommunityData('public'),
                          UdpTransportTarget((host, 161)),
                          ContextData(),                                                           
                          ObjectType(ObjectIdentity(oid)),
                          lexicographicMode=False):
        if errorIndication:
            print(errorIndication, file=sys.stderr)
            break
        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?'), 
                                file=sys.stderr)             
            break
        else:
            for varBind in varBinds:
                print(varBind)
walk_disk_desc('127.0.0.1','1.3.6.1.2.1.25.2.3.1.3')
walk_disk_usage('127.0.0.1','1.3.6.1.2.1.25.2.3.1.6')
