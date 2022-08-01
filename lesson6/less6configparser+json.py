import pyvisa
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
CMT.timeout = 10000


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


# конвертация кГц, МГц, ГГц в Гц
def HZ_convert(pref, hertz):
    try:
        hertz = int(hertz)
    except ValueError:
        return -1
    if pref == "k":
        return hertz * 1000
    if pref == "M":
        return hertz * 1000000
    if pref == "G":
        return hertz * 1000000000
    return -1


# функция однократного россчерка
def one_scan(ch_num):
    CMT.write('TRIG:SOUR BUS')  # устанавливаем источник триггера на шину
    CMT.write(f"INIT{ch_num}:CONT OFF")  # включаем повторный режим запуска триггера
    # переходим в состояние ожидания триггера
    CMT.write('INIT')
    CMT.write('TRIG:SING')  # выполняем россчерк
    CMT.query('*OPC?')




write(CMT, 'SERVice:RFCTL:POWer:STATe 1')
write(CMT, 'SERVice:RFCTL:POWer:ATT 10')
write(CMT, f'SENS1:BWID {HZ_convert("k", "10")}')
write(CMT, 'SERV:RFCTL:POW:DAC 6554')
write(CMT, 'SERVice:SWEep:FREQuency:FACTory')


# точки при заводской калибровке
#
# import configparser
#
# config = configparser.ConfigParser()
# config.read(r'C:\Users\user\PycharmProjects\Students\lab6\table_info.ini')
# a = config.sections()
# print(a)
# size = config.get(f"{a[0]}", r"_META\activeIndex")
# arr = []
# for i in range(int(size)+1):
#     arr.append(int(config.get(f"{a[0]}", fr"{i}\pointCount\value")))
#     print(config.get(f"{a[0]}", fr"{i}\pointCount\value"))
# print(sum(arr))
#  "C:\Users\user\PycharmProjects\Students\lab6\test_segment.seg"
# write(CMT, r'MMEMory:STORe:SEGMent')
print(query(CMT, 'SENS1:SEGM:DATA?'))
b = query(CMT, 'SENS1:SEGM:DATA?').split(',')
print(b)
arr_start_mark = []
arr_end_mark = []
for i in range(9, len(b), 6):
    b[i] = str(int(b[i]) * 2)   # домножение точек на 2
    arr_end_mark.append(b[i - 1])   # начальные координаты марки
    arr_start_mark.append(b[i - 2])     # конечные
# print(b)
# print(arr_start_mark)
# print(arr_end_mark)
trace_count=int(query(CMT, f'SERV:PORT:COUNT?'))
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


upd_array = ','.join(b)
#
write(CMT, f'SENS1:SEGM:DATA {upd_array}')

# # write(CMT, r'MMEM:LOAD:SEGM C:\Users\user\PycharmProjects\Students\lab6\table_info.ini')