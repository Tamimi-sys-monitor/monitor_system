from pysnmp.hlapi import *

def get_snmp_data(oid):
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData('public'),  # Replace 'public' with your SNMP community string
               UdpTransportTarget(('localhost', 161)),  # Replace with your SNMP server details
               ContextData(),
               ObjectType(ObjectIdentity(oid)))
    )

    if errorIndication:
        print(f"SNMP error: {errorIndication}")
        return None
    elif errorStatus:
        print(f"SNMP error: {errorStatus.prettyPrint()}")
        return None
    else:
        return Integer.__ceil__(varBinds[0][1])

# OIDs for the requested information
memory_total_oid = "1.3.6.1.4.1.2021.4.5.0"  # UCD-SNMP-MIB::memTotalReal
cpu_usage_oid = "1.3.6.1.4.1.2021.11.11.0"  # UCD-SNMP-MIB::ssCpuIdle


# Retrieve and print memory information
memory_total = get_snmp_data(memory_total_oid)
print(memory_total)

# Retrieve and print CPU information
cpu_usage = get_snmp_data(cpu_usage_oid)
print(cpu_usage)


