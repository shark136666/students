import pyvisa as visa

# Подключение к SNVNA
rm = visa.ResourceManager('@py')
# Connect to a Socket on the local machine at 5025
# Use the IP address of a remote machine to connect to it instead
try:
    CMT = rm.open_resource('TCPIP0::localhost::5025::SOCKET')
except:
    print("Failure to connect to VNA!")
    print("Check network settings")

# The VNA ends each line with this. Reads will time out without this
CMT.read_termination = '\n'
# Set a really long timeout period for slow sweeps
CMT.timeout = 100000

# Ожидание завершения команды

def check_error(inst):
    result = inst.query(f'SYST:ERR?')
    if (result == "0, No error"):
        pass
    else:
        print(result)
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
    check_error(CMT)
    CMT.write(f"INIT{ch_num}:CONT OFF")   # включаем повторный режим запуска триггера
    check_error(CMT)                          # переходим в состояние ожидания триггера
    CMT.write('INIT')
    check_error(CMT)
    CMT.write('TRIG:SING')      # выполняем россчерк
    check_error(CMT)
    CMT.query('*OPC?')
    check_error(CMT)
    print("end scan")



# Пресет
CMT.write('SYST:PRESET')
check_error(CMT)

# Устанавливаем частоту росчерка
CMT.write(f'SENS1:FREQ:STAR {HZ_convert("G", 1)}')
check_error(CMT)

CMT.write(f'SENS1:FREQ:STOP {HZ_convert("G", 6)}')
check_error(CMT)

# Устанавливаем кол-во точек в канале 1001
CMT.write('SENS1:SWE:POIN 1001')
check_error(CMT)


# Устанавливаем фильтр ПЧ
CMT.write(f'SENS1:BWID {HZ_convert("k", 300)}')
check_error(CMT)


# Параметры канала
print("channel")
print('Канал №1: \n start = ' + str(CMT.query('SENS1:FREQ:STAR?')) + "Hz")
check_error(CMT)
print(' stop = ' + str(CMT.query('SENS1:FREQ:STOP?')) + "Hz")
check_error(CMT)
print(' points = ' + str(CMT.query('SENS1:SWE:POIN?')))
check_error(CMT)
print(' bandwith = ' + str(CMT.query('SENS1:BAND?')) + "Hz")
check_error(CMT)

# Создаем 4 маркера на 2, 3, 4 и 5 ГГц
print("markers")
CMT.write('CALC1:MARK4:ACT')
for i in [2, 3, 4, 5]:
    CMT.write(f'CALC1:MARK{i-1}:X {i}e9')

print("end markers")
# Словарь для хранения результатов статистики
range_dict = {}
# Включаем индикацию и диапазон расчета мат. стат-ики
CMT.write('CALC1:MST ON')
CMT.write('CALC1:MST:DOM ON')
for i in range(1, 5):
    if i != 4:
        CMT.write(f'CALC1:MST:DOM:STAR {i}')
        CMT.write(f'CALC1:MST:DOM:STOP {i+1}')
    else:
        CMT.write(f'CALC1:MST:DOM:STAR {1}')
        CMT.write(f'CALC1:MST:DOM:STOP {i}')
    math_stat = CMT.query(f'CALC1:MST:DATA?').split(',')
    range_dict.update({f'{i}-{i + 1}': {'mean': f'{math_stat[0]}', 's.dev': f'{math_stat[1]}', 'peak-peak': f'{math_stat[2]}'}})

# Вывод данных мат статистики
for key,value in range_dict.items():
    print(f'Маркеры {key}\n Среднее значение = {value["mean"]}')
    print(f' Стандартное отклонение = {value["s.dev"]}\n Фактор пик-пик = {value["peak-peak"]}')

CMT.write('SYST:PRESET')
# устанавливаем трассу s21
CMT.write('CALC1:PAR1:DEF S21')
# переводим триггер в режим bus
CMT.write('TRIG:SOUR BUS')
# включаем мат. стат-ику для всего диапазона
CMT.write(f'CALC1:MST ON')
# Проводим одноразовое сканирование
one_scan(1)
math_stat = CMT.query(f'CALC1:MST:DATA?').split(',')
print(f'mean = {math_stat[0]}')

# Включили усреднение
CMT.write(f'SENS:AVER ON')
# установили фактор усреднения на 100
CMT.write(f'SENS1:AVER:COUN 100')
# выполняем россчерк столько раз, на сколько установлен фактор усреднения
for i in range(CMT.write('SENS1:AVER:COUN?')):
    one_scan(1)
math_stat = CMT.query(f'CALC1:MST:DATA?').split(',')
print(f'mean = {math_stat[0]}')