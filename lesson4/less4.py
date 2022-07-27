
import pyvisa , time
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
# convertator
def Convertor(n,freq):
	if freq == "kHz":
		return int(n*1e+3)
	elif freq == "MHz":
		return int(n*1e+6)
	elif freq == "GHz":
		return int(n*1e+9)
	else: return print("Incorrect value")
#Scanner
def Scanner(connect):
	connect.write(f'TRIG:SOUR BUS')
	connect.write(f'INIT:CONT OFF')
	connect.write(f'INIT')
	connect.write(f'TRIG:SING')   
	connect.query(f'*OPC?')


DictHolder={}

#Preset
CMT.write(f'SYST:PRES')

#Adding trace 
CMT.write(f'CALC1:PAR:COUN 1')

#Setup Gh
CMT.write(f'SENS:FREQ:STAR { Convertor(1,"GHz")}')
 
CMT.write(f'SENS:FREQ:STOP { Convertor(6,"GHz")}')
 

#Setup 1001 points
CMT.write(f'SENS:SWE:POIN 1001')
 

#Установливаем фильтр ПЧ(ширина полосы ПЧ) 3kHz 
CMT.write(f'SENS:BWID { Convertor(3,"kHz")}')
time.sleep(1) 
#Считываем данные и выводим
star_data = CMT.query(f'SENS:FREQ:STAR?')
stop_data = CMT.query(f'SENS:FREQ:STOP?')
poin_data = CMT.query(f'SENS:SWE:POIN?')
band_data = CMT.query(f'SENS:BAND?')

print(f'Channel №1: Start = {star_data}; Stop = {stop_data}; Points = {poin_data}; IFBW = {band_data}')

#4 markers was added
for i in range (1,5):
	CMT.write(f'CALC1:TRAC1:MARK{i}:STAT ON')


#4 status marks was updated
CMT.write(f'CALC1:MARK1:X { Convertor(2,"GHz")}')
CMT.write(f'CALC1:MARK2:X { Convertor(3,"GHz")}')
CMT.write(f'CALC1:MARK3:X { Convertor(4,"GHz")}')
CMT.write(f'CALC1:MARK4:X { Convertor(5,"GHz")}')

#Ststistic on
CMT.write(f'CALC1:MST ON')
CMT.write(f'CALC1:MST:DOM ON')

#Get statistic beetwen markers 1-2,2-3,3-4,4-1
for i in range(1,5):
	if i == 4:
		CMT.write(f'CALC1:MST:DOM:STAR 1')
		 
		CMT.write(f'CALC1:MST:DOM:STOP 4')
		 
	else:
		CMT.write(f'CALC1:MST:DOM:STAR {i}')
		 
		CMT.write(f'CALC1:MST:DOM:STOP {i+1}')
		 

	#Adding data to dict
	star_data = CMT.query(f'CALC1:MST:DOM:STAR?')
	stop_data = CMT.query(f'CALC1:MST:DOM:STOP?')
	mst_data = CMT.query(f'CALC:MST:DATA?')
	array = mst_data.split(',')
	DictHolder.update({f'{star_data}-{stop_data}':{f'mean':f'{array[0]}',f's.dev':f'{array[1]}',f'p-p':f'{array[2]}'}})

#Printing dict val
for key, value in DictHolder.items():
	print(f'Marker {key}\n Average = {value["mean"]}\n Standart diff = {value["s.dev"]}\n Peak-peak factor = {value["p-p"]}')

#5 quest
#Preset
CMT.write(f'SYST:PRES')


#Trace
CMT.write(f'CALC1:PAR1:DEF S21')


#BUS mode
CMT.write(f'TRIG:SOUR BUS')
 

#Math stat on
CMT.write(f'CALC1:MST ON')


Scanner(CMT)
 

#mean val
mst_data = CMT.query(f'CALC1:TRAC1:MST:DATA?')
array = mst_data.split(',')
 
print(f'mean = {array[0]}')

#average on
CMT.write(f'SENS:AVER ON')
 
#coun aver 100
CMT.write(f'SENS1:AVER:COUN 100')


#100 times exec
aver_data = CMT.query(f'SENS1:AVER:COUN?')
for i in range(int(aver_data)):
	 Scanner(CMT)


#mean
mst_data = CMT.query(f'CALC1:TRAC1:MST:DATA?')
array = mst_data.split(',')
print(f'mean = {array[0]}')


