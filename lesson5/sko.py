import pyvisa
from commands import one_scan, HZ_convert
import json
# Подключение к SNVNA
rm = pyvisa.ResourceManager('@py')
# Connect to a Socket on the local machine at 5025
# Use the IP address of a remote machine to connect to it instead
try:
    CMT = rm.open_resource('TCPIP0::localhost::5025::SOCKET')
except:
    print("Failure to connect to VNA!")
    print("Check network settings")
CMT.read_termination = '\n'
# Set a really long timeout period for slow sweeps
CMT.timeout = 1000


def command_wrapper(f):
    def wrapped(inst, command):
        # print('До функции')
        # try:
        #     if key == "debug":
        #         print(command)
        # except:
        #     pass
        response = f(inst, command)
        # print('После функции')
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

# костыль для определения количества портов
def port_query():
    port_count = 0
    write(CMT, f'CALC1:PAR:COUN 1')
    while True:
        port_count += 1
        CMT.write(f'CALC1:PAR1:DEF S{port_count}1')
        error = query(CMT, 'SYST:ERR?')
        if error == '-110, Command header error':
            return port_count - 1


# установка трасс
def sko_algorithm(trace_count, bwid, att):
    math_stat = []

    # Устанавливаем фильтр ПЧ 300 или 3 кГц
    write(CMT, f'SENS1:BWID {HZ_convert("k", f"{bwid}")}')

    # вкл. Аттенюатор 10, 30 или 50 дБ
    write(CMT, 'SERVice:RFCTL:POWer:STATe 1')
    write(CMT, f'SERVice:RFCTL:POWer:ATT {att}')

    # Частотный план
    write(CMT, 'SERVice:SWEep:FREQuency:FACTory')

    # Код ЦАП.  АЧХ
    write(CMT, 'SERV:RFCTL:POW:DAC 6554')

    # Создание трасс и росчерк
    write(CMT, f'CALC1:PAR:COUN 1')
    for i in range(trace_count*3):
        params = ['S', 'T', 'R']
        # T, R
        if i%3 != 0:
            write(CMT, f'CALC1:PAR1:DEF {params[i % 3]}{(i // 3) + 1}')
            # установка порта-источника
            write(CMT, f'CALC1:PAR1:SPOR {(i//3) + 1}')
        # S
        else:
            write(CMT, f'CALC1:PAR1:DEF {params[i%3]}{(i // 3) + 1}{(i // 3) + 1}')
        one_scan(1)

        # Сохранение текущего измерения в памяти и Data/mem
        write(CMT, f'CALC1:PAR1:SEL')
        write(CMT, f'CALC1:MATH:MEM')
        write(CMT, f'CALC1:MATH:FUNC DIV')
        one_scan(1)

        # запись СКО
        write(CMT, f'CALC1:MST ON')
        math_stat.append(query(CMT, f'CALC1:MST:DATA?').split(','))
    return math_stat

# костыль для количества портов
# trace_num = int(query(CMT, '*IDN?')[query(CMT, '*IDN?').find('SN5090')+7] + query(CMT, '*IDN?')[query(CMT, '*IDN?').find('SN5090')+8])       # последний порядковый номер трассы
trace_num = port_query()
math_stats = []
for i in [10, 30, 50]:      # Алгоритм для ПЧ 300 и 3 кГц, аттенюатора 10, 30, 50 дБ
    for j in [300, 3]:
        math_stat = sko_algorithm(trace_num, j, i)
        math_stats.append(math_stat)


math_result = []    # Для совмещения массивов S11 + S22 + S33, T11 + T22.....
if trace_num != 1:
    for j in range(6):
        math1 = [] # S
        math2 = [] # T
        math3 = [] # R
        for i in range(trace_num):
            math1 += math_stats[j][i*3]
            math2 += math_stats[j][(i*3) + 1]
            math3 += math_stats[j][(i*3) + 2]
        arr = [math1, math2, math3]
        math_result.append(arr)
else:
    math_result = math_stats


def list_to_dict(arr, ports, param):    # Перевод arr в dict
    dict = {'max_value':0}
    params = []
    for i in range(ports):
        params.append(arr[1+(i*3)])
        dict.update({f'{param}{i+1}{i+1}': params[i]})
    dict['max_value'] = max(params)
    return dict


Dictionar={}

Tune_value={10:Dictionar,30:Dictionar,50:Dictionar}

# result["atthenuator"]["Tune_value"]["IF"]["PCH_value"]["trace"]["absolute"].update(value)
# result["atthenuator"]["Tune_value"]["IF"]["PCH_value"]["trace"]["otnosit"].update(value1)

result = {"atthenuator":{}}
mass = [10,30,50]
iff = [300,3]
count = 0 # от 0 до 5
for i in mass:
    result["atthenuator"][f'{i}'] = {'IF':{}}
    for j in iff:
        value_otn = list_to_dict(math_result[count][0], trace_num, 'S')
        value_t = list_to_dict(math_result[count][1], trace_num, 'T')
        value_r = list_to_dict(math_result[count][2], trace_num, 'R')
        count += 1
        value_abs = value_r | value_t
        result["atthenuator"][f'{i}']['IF'][f'{j}']={'trace':{"absolute":{},"otnosit":{}}}
        result["atthenuator"][f'{i}']["IF"][f'{j}']["trace"]["absolute"].update(value_abs)
        result["atthenuator"][f'{i}']["IF"][f'{j}']["trace"]["otnosit"].update(value_otn)
json_data=json.dumps(result, indent=4)
print(json_data)
json = open('sko_result.json', 'w')
json.write(json_data)
json.close()
