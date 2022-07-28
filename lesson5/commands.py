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
