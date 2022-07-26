import pyvisa



# Подключение к SNVNA
rm = pyvisa.ResourceManager()
#Connect to a Socket on the local machine at 5025
#Use the IP address of a remote machine to connect to it instead
try:
    CMT = rm.open_resource('TCPIP0::localhost::5025::SOCKET')
except:
    print("Failure to connect to VNA!")
    print("Check network settings")
    print("DONT FORGET TO ACTIVATE SNVNA!!!")
CMT.read_termination='\n'
CMT.timeout = 1000
CMT.write(f'CALC1:PAR:COUN 16')
trace_count = CMT.query(f'CALC1:PAR:COUN?')
print(trace_count)
for i in range(1,17):
    CMT.write(f'CALC1:PAR{i}:DEF S{i}{i}')
    #print(CMT.query(f'CALC1:PAR{i}:DEF?'))
    CMT.write(f'CALC1:MARK{i}:X 1e9')
    CMT.write(f'CALC1:MARK{i}:X 55e8')
    if i % 2 == 0 :
        CMT.write(f'CALC1:PAR{i}:DEF S{i}{i-1}')
    print(f'trassa #{i}='+CMT.query(f'CALC1:PAR{i}:DEF?'))


