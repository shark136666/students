import datetime
import pyvisa
import json
import configparser
from json2html import *
rm = pyvisa.ResourceManager('@py')
try:
    CMT = rm.open_resource('TCPIP0::localhost::5025::SOCKET')
except:
    print("Failure to connect to VNA!")
    print("Check network settings")
CMT.read_termination = '\n'
CMT.timeout = 10000

def setup_trace(CMT, port, traces,ranges):
    for trace in traces:
        if trace is "S":
            write(CMT, f'CALC1:PAR1:DEF {trace}{port}{port}')
            setup_markers(CMT,1,ranges)
        elif trace is "T":
            write(CMT, f'CALC1:PAR2:DEF {trace}{port}')
            write(CMT, f'CALC1:PAR2:SPOR {port}')
            setup_markers(CMT,2,ranges)
        else:
            write(CMT, f'CALC1:PAR3:DEF {trace}{port}')
            write(CMT, f'CALC1:PAR3:SPOR {port}')
            setup_markers(CMT,3,ranges)

def Convertor(n,freq):
	if freq == "kHz":
		return int(n*1e+3)
	elif freq == "MHz":
		return int(n*1e+6)
	elif freq == "GHz":
		return int(n*1e+9)
	else: return print("Incorrect value")

def Convertor1(value:str):    
    n,freq = value.split(' ')
    n=int(n)
    print(n,freq)
    if freq == "kHz":
        return int(n*1e+3)
    elif freq == "MHz":
        return int(n*1e+6)
    elif freq == "GHz":
        return int(n*1e+9)
    else: return print("Incorrect value")

def AntiConvertor(number):
    number1=int(number)
    # number1=str(number1)
    if (number1) < 1000000:
        return str(float(number1)/1000) + ' kHz'
    if (number1) < 1000000000:
        return str(float(number1)/1000000) + ' MHz'
    return str(float(number1)/1000000000) + ' GHz'

def command_wrapper(f):
    def wrapped(inst, command):
        response = f(inst, command)
        error = inst.query('SYST:ERR?')
        if error != '0, No error':
            print(error)
            print(command)
        return response

    # print('декорируем', f)
    return wrapped


@command_wrapper
def query(inst, command):
    result = inst.query(command)
    return result


@command_wrapper
def write(inst, command):
    inst.write(command)

def list_to_dict(arr, ports, param):    # Перевод arr в dict
    dict = {'max_value':0}
    params = []
    for i in range(len(arr)):
        params.append(arr[(i)])
        dict.update({f'{param}{i+1}{i+1}': params[i]})
    dict['max_value'] = max(params)
    return dict
# конвертация кГц, МГц, ГГц в Гц

def get_ranges(ranges):
    result = {}
    arr=ranges.split(',')
    for i in range(len(arr)):
        result[i]={}        
        arr1 = arr[i].split('-')    
        result[i]['start'] = Convertor1(arr1[0])
        result[i]['stop'] = Convertor1(arr1[1])
    return result

# функция однократного россчерка
def one_scan(CMT):
    CMT.write('TRIG:SOUR BUS')  # устанавливаем источник триггера на шину
    CMT.write(f"INIT:CONT OFF")  # включаем повторный режим запуска триггера
    # переходим в состояние ожидания триггера
    CMT.write('INIT')
    CMT.write('TRIG:SING')  # выполняем россчерк
    CMT.query('*OPC?')

def multiplier_segments(CMT):
    b = query(CMT, 'SENS1:SEGM:DATA?').split(',')       
    # print(len(arr_end_mark))    
    for i in range(9, len(b), 6):
        b[i] = str(int(b[i]) * 2)   # домножение точек на 2
             # конечные
    upd_array = ','.join(b)
    write(CMT, f'SENS1:SEGM:DATA {upd_array}')


def setup_chanel_parametrs(CMT,att, ifbw):
    write(CMT,'SYST:PRES')
    write(CMT, 'SERVice:RFCTL:POWer:STATe 1')
    write(CMT, f'SERVice:RFCTL:POWer:ATT {att}')
    write(CMT, f'SENS1:BWID {ifbw}')
    write(CMT, 'SERV:RFCTL:POW:DAC 6554')
    write(CMT, 'SERVice:SWEep:FREQuency:FACTory')
    multiplier_segments(CMT)
            
def setup_markers(CMT,trace,ranges):
        CMT.write(f'CALC1:PAR{trace}:SEL')
        marker_count=len(ranges)*2
        CMT.write(f'CALC1:MARK{marker_count}:STAT ON')
        CMT.write(f'CALC1:MST ON')
        CMT.write(f'CALC1:MST:DOM ON')
        for key in ranges.keys():
            # ((key+1) * 2 ) - 1 start
            # # ((key+1) * 2 ) stop
            CMT.write(f'CALC1:MARK{((key+1) * 2 ) - 1}:X {ranges[key]["start"]}')
            CMT.write(f'CALC1:MARK{((key+1) * 2 )}:X {ranges[key]["stop"]}')


def get_data(CMT,port,result,start,stop):

    for i in range(1,4):
        CMT.write(f'CALC1:PAR{i}:SEL')
   
        CMT.write(f'CALC:MST:DOM:START {((key+1) * 2 ) - 1}')
        CMT.write(f'CALC:MST:DOM:STOP {((key+1) * 2 )}')
        mst_data=CMT.query(f'CALC1:MST:DATA?')
        value = mst_data.split(',')
        value = format(float(value[2]),'.8f')
        if i is 1:
                result['segment'][f'{start}-{stop}']['absolute'][f'S{port}{port}']=value
        elif i is 2:
                result['segment'][f'{start}-{stop}']['otnosit'][f'T{port}{port}']=value
        else:
                result['segment'][f'{start}-{stop}']['otnosit'][f'R{port}{port}']=value
    return result

def dict_gen(result):
    for key in ranges.keys():
        start = AntiConvertor(ranges[key]['start'])
        stop = AntiConvertor(ranges[key]['stop'])
        result['segment'][f'{start}-{stop}']={'absolute':{},'otnosit':{}}
        result['segment'][f'{start}-{stop}']['absolute']={f"S{j}{j}" : f"{0}" for j in range (1,trace_count+1)}
        T={f"T{j}{j}" : f"{0}" for j in range (1,trace_count+1)}
        R={f"R{j}{j}" : f"{0}" for j in range (1,trace_count+1)}
        result['segment'][f'{start}-{stop}']['otnosit']={**T,**R}
    return result



start_time = datetime.datetime.now()
config = configparser.ConfigParser()
config.read('config.cfg')
ranges = get_ranges(config['range']['ranges'])
IFBW = Convertor1(config['options']['IFBW'])
attenuator = config['options']['attenuator']
traces = ['S','T','R']
setup_chanel_parametrs(CMT,attenuator,IFBW)
trace_count=int(query(CMT, f'SERV:PORT:COUNT?'))
print(trace_count)
write(CMT, f'CALC1:PAR:COUN 3')
result=dict_gen(result={"segment":{}})




for port in range(1,trace_count+1):   
    setup_trace(CMT,port,traces,ranges)
    one_scan(CMT)
    for key in ranges.keys():
        start = AntiConvertor(ranges[key]['start'])
        stop = AntiConvertor(ranges[key]['stop'])
        result=get_data(CMT,port,result,start,stop)
for key in ranges.keys():
    start = AntiConvertor(ranges[key]['start'])
    stop = AntiConvertor(ranges[key]['stop'])
    result['segment'][f'{start}-{stop}']['absolute']['max_abs']=max(result['segment'][f'{start}-{stop}']['absolute'].values())
    result['segment'][f'{start}-{stop}']['otnosit']['max_diff']=max(result['segment'][f'{start}-{stop}']['otnosit'].values())


# json_data=json.dumps(result, indent=4)
#  print(json_data)
# json = open('freq_test.json', 'w')
# json.write(json_data)
# json.close()

perf_data=query(CMT,f'*IDN?').split(',')
print(perf_data)
print(start_time)

