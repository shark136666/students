import pyvisa
from commands import one_scan, HZ_convert

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


sko_abs_max = 0     # максимальный абсолютный ско
sko_otn_max = 0     # относительный
trace_num = int(input('Введите количество портов'))       # последний порядковый номер трассы
while(trace_num>16 or trace_num < 1):
    print('Некорректное число портов, введите число от 1 до 16')
    trace_num = int(input('Введите количество портов'))
math_stats = []
for i in [10, 30, 50]:      # Алгоритм для ПЧ 300 и 3 кГц, аттенюатора 10, 30, 50 дБ
    for j in [300, 3]:
        math_stat = sko_algorithm(trace_num, j, i)
        for k in range(trace_num*3):    # Проверка на макс. ско
            if (float(math_stat[k][1]) > sko_otn_max) and (k % 3 == 0):
                sko_otn_max = float(math_stat[k][1])
            elif (float(math_stat[k][1]) > sko_abs_max) and (k % 3 != 0):
                sko_abs_max = float(math_stat[k][1])
        math_stats.append(math_stat)
        # print(f"for att = {i} and bwid = {j}")
        # print(math_stat)
for i in math_stats:
    print(i)
print(f'sko otn max {sko_otn_max}')
print(f'sko abs max {sko_abs_max}')



# кол-во трасс = порты * 3 (S, T, R) * 6 (10-300,10-3,30-300...)
# # Создание трасс
#     write(CMT, f'CALC1:PAR:COUN {trace_count}')
#     for i in range(trace_count):
#         params = ['S', 'T', 'R']
#         # T, R
#         if i%3 != 0:
#             write(CMT, f'CALC1:PAR{i + 1}:DEF {params[i % 3]}{(i // 3) + 1}')
#             # установка порта-источника
#             write(CMT, f'CALC1:PAR{i+1}:SPOR {(i//3) + 1}')
#         # S
#         else:
#             write(CMT, f'CALC1:PAR{i + 1}:DEF {params[i%3]}{(i // 3) + 1}{(i // 3) + 1}')