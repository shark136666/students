import time
import pyvisa
import configparser
import json
from connect import SNVNAopen, write, query, query_ascii_values, HzConvertor, singlescan

#словарь для хранения входных данных
conf_data = {
	'IFBW':None,
	'range':{
	}
}
#словарь для записи в json
jsondict = {}

CMT = SNVNAopen()

#Функция чтения файла config.txt и записи его значений
def readconfig():
    #Читаем значения из конфиг файла
    config = configparser.ConfigParser()
    config.read_file(open(r'config.txt'))

    #Записываем в словарь
    conf_data['IFBW'] = int(config['IFBW']['IFBW'])
    for key in config['range'].keys():
            range_value = []
            range_value =  config['range'][f'{key}'].split(' ')
            conf_data['range'][f'{key}'] = HzConvertor(int (range_value[0]),range_value[1])

def param(conf_data):
	#Пресет
	write(CMT, f'SYST:PRES')
	
	#Attenuator control – вкл. 
	write(CMT, f'SERV:RFCTL:POW:STAT 1')
	write(CMT, f'SERV:RFCTL:POW:ATT 10')	
	
	#Установить фильтр ПЧ из conf_data
	write(CMT, f'SENS:BWID {conf_data["IFBW"]}')
	time.sleep(1) 
	
	#установить Код ЦАП.
	write(CMT, f'SERV:RFCTL:POW:DAC 6554')
	
	#Устанавливаем определенный сегментный план и считываем данные
	write(CMT, f'SERV:SWE:FREQ:FACT')

def double_point():
	segm_data = query_ascii_values(CMT,f'SENS:SEGM:DATA?')
	str = 'SENS:SEGM:DATA '
	k = 9
	for i in range(len(segm_data)):
		if i == k:
			segm_data[i] = int(segm_data[i]) * 2
			k += 6
		if i != len(segm_data)-1:
			str += f'{segm_data[i]},'
		else:
			str += f'{segm_data[i]}'
	write(CMT, str)

#Функция проведения тестов и записи в json

def start_frequency_test(conf_data):
    #date_inf = query(CMT,f'SYST:DATE?') эта команда не работает
    time_inf = query(CMT,f'SYST:TIME?')
    idn_inf = list(query(CMT,f'*IDN?'))
    idn_inf = "".join(idn_inf).split(", ")
    jsondict.update({"inf":{}})
    jsondict["inf"].update({"time":f'{time_inf}'})
    jsondict["inf"].update({"device":f'{idn_inf[0]}'})
    jsondict["inf"].update({"model":f'{idn_inf[1]}'})
    jsondict["inf"].update({"serial":f'{idn_inf[2]}'})
    jsondict["inf"].update({"version":f'{idn_inf[3]}'})

    #Подключаемся к SNVNA
    k = 1
    """ ввод колличества потоков """
    tracc_count = int(query(CMT,f'SERV:PORT:COUN?'))
    param(conf_data)
    double_point()
    config = configparser.ConfigParser()
    config.read_file(open(r'config.txt'))
    #цикл вывода otn
    start_data = 0
    stop_data = 0
    stop = 0
    start = 0
    general_range1 = config["range"]['v'].split(", ")
    for keys in range(0, len(general_range1)):
            range1 = general_range1[int(f'{keys}')].split("-")
            start_data = range1[0]
            stop_data = range1[1]
            jsondict.update({f'{start_data} - {stop_data}': {}})
            jsondict[f'{start_data} - {stop_data}'].update({'max_abs': 0.0, 'max_otn': 0.0})


    for canal in range(1,tracc_count+1):
            #создание 3 трасс
            write(CMT, f'CALC1:PAR:COUN 1')
            write(CMT, f'CALC1:PAR1:DEF S{canal}{canal}')
            singlescan(CMT)
            #--------------------
            start_data = 0
            stop_data = 0
            stop = 0
            start = 0
            general_range1 = config["range"]['v'].split(", ")
            for keys in range(0, len(general_range1)):
                    range1 = general_range1[int(f'{keys}')].split("-")
                    range_start = range1[0].split(" ")
                    range_stop = range1[1].split(" ")
                    start = HzConvertor(int(range_start[0]), range_start[1])
                    stop = HzConvertor(int(range_stop[0]), range_stop[1])
                    start_data = range1[0]
                    stop_data = range1[1]

                    write(CMT, f'CALC1:TRAC:MARK1:STAT ON')
                    write(CMT, f'CALC1:TRAC:MARK2:STAT ON')
                    write(CMT, f'CALC1:MARK2:X {stop}')
                    write(CMT, f'CALC1:MARK1:X {start}')
                    write(CMT, f'CALC1:MST ON')
                    write(CMT, f'CALC1:MST:DOM ON')

                    mst_data = query_ascii_values(CMT,f'CALC:MST:DATA?')
                    trace = query(CMT, f'CALC1:PAR:DEF?')
                    if k < 2 :
                            jsondict.update({f'{trace}': {}})
                            k += 1
                    jsondict[f'{trace}'].update({f'{start_data} - {stop_data}':{}})

                    if mst_data[2] > jsondict[f'{start_data} - {stop_data}']["max_otn"] or jsondict[f'{start_data} - {stop_data}']["max_otn"] == 0.0 :
                            jsondict[f'{start_data} - {stop_data}'].update({"max_otn" : mst_data[2]})
                    jsondict[f'{trace}'][f'{start_data} - {stop_data}'].update({'Value':mst_data[2]})

            k = 1

    #цикл вывода abs

    for canal in range(1,tracc_count+1):
            #создание 3 трасс
            write(CMT, f'CALC1:PAR:COUN 2')
            write(CMT, f'CALC1:PAR1:DEF R{canal}')
            write(CMT, f'CALC1:PAR1:SPOR {canal}')
            write(CMT, f'CALC1:PAR2:DEF T{canal}')
            write(CMT, f'CALC1:PAR2:SPOR {canal}')
            singlescan(CMT)
            #--------------------

            general_range1 = config["range"]['v'].split(", ")
            for keys in range(0,len(general_range1)):
                    start_data = 0
                    stop_data = 0
                    stop = 0
                    start = 0
                    range1 = general_range1[int(f'{keys}')].split("-")
                    range_start = range1[0].split(" ")
                    range_stop = range1[1].split(" ")
                    start = HzConvertor(int (range_start[0]),range_start[1])
                    stop = HzConvertor(int (range_stop[0]),range_stop[1])
                    start_data = range1[0]
                    stop_data = range1 [1]
                    for n_trace in range(1,3):
                            write(CMT, f'CALC:PAR{n_trace}:SEL')
                            write(CMT, f'CALC1:TRAC{n_trace}:MARK1:STAT ON')
                            write(CMT, f'CALC1:TRAC{n_trace}:MARK2:STAT ON')
                            write(CMT, f'CALC1:MARK2:X {stop}')
                            write(CMT, f'CALC1:MARK1:X {start}')
                            write(CMT, f'CALC1:MST ON')
                            write(CMT, f'CALC1:MST:DOM ON')

                            mst_data = query_ascii_values(CMT,f'CALC:MST:DATA?')
                            trace = query(CMT, f'CALC1:PAR{n_trace}:DEF?')
                            if k < 3 :
                                    jsondict.update({f'{trace}': {}})
                                    k += 1
                            jsondict[f'{trace}'].update({f'{start_data} - {stop_data}':{}})
                            if mst_data[2] > jsondict[f'{start_data} - {stop_data}']["max_abs"] or jsondict[f'{start_data} - {stop_data}']["max_abs"] == 0.0 :
                                    jsondict[f'{start_data} - {stop_data}'].update({"max_abs" : mst_data[2]})
                            jsondict[f'{trace}'][f'{start_data} - {stop_data}'].update({'Value':mst_data[2]})

            k = 1

def table_generator():
    # создаем словарь для записи с json
    data = {}

    # открываем файл и загружаем данные
    with open('freq_test.json', 'r', encoding='utf-8') as fh:
        data.update(json.load(fh))

    # ввод допуска
    config = configparser.ConfigParser()
    config.read_file(open(r'config.txt'))
    dop_otn = float(config['DOP']['dop_otn'])
    dop_abs = float(config['DOP']['dop_abs'])

    # создаем строку для ввода в html страницу
    htmlstr = "<!-- Bootstrap CSS -->\
        <link rel='stylesheet' href='https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css' integrity='sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T' crossorigin='anonymous'>\
    <style>\
    table, th, td {\
        border: 2px solid black;\
    	border-collapse: collapse;\
    }\
    th, td {\
        padding: 1px;;\
    }\
        </style>\
    "

    htmlstr += "<table border='1' ><tr><td> Время запуска </td><td>  device </td><td> model </td><td> serial </td><td>  version </td></tr><tr>"
    for i in data["inf"].keys():
        htmlstr += f'<td>{data["inf"][i]}</td>'

    htmlstr += "<table border='1' ><tr><td> Диапазон </td>"
    # Цикл для заолнения html страницы

    for i in list(data.keys()):
        if i == "S11":
            break
        if i != "inf":
            htmlstr += f'<td colspan="3">{i}</td>'

    htmlstr += "</tr> <tr><td>Трассы</td>"
    for i in list(data.keys()):
        if i == "S11":
            break
        if i != "inf":
            htmlstr += " <td>Нер-ть,дБ</td>  <td>Макс.дБ</td>    <td>Допуск,дБ</td>"
    htmlstr += "<tr>"
    k = 0
    for trace in data.keys():
        if trace == "S11" or k == 3:
            k = 3
            htmlstr += f'<td>{trace}</td> '
            for Range in data[f'{trace}'].keys():
                value = data[f'{trace}'][f'{Range}']["Value"]
                if "S" in f'{trace}':
                    """ otnositelnie """
                    if value == data[f'{Range}']["max_otn"]:
                        htmlstr += f'<td>{value}</td> '

                        if value > dop_otn:
                            htmlstr += f'<td class = bg-warning> {"{:0.9f}".format(value)} </td> <td class = bg-warning> {"{:0.9f}".format(dop_otn)} </td> '
                        else:
                            htmlstr += f'<td> {"{:0.6f}".format(value)} </td> <td> {"{:0.6f}".format(dop_otn)} </td>'
                    else:
                        htmlstr += f'<td> {"{:0.6f}".format(value)} </td> <td> - </td><td>{"{:0.6f}".format(dop_otn)}</td>'
                    """ absolute """
                else:
                    if value == data[f'{Range}']["max_abs"]:
                        htmlstr += f'<td>{value}</td> '

                        if value > dop_abs:
                            htmlstr += f'<td class = bg-warning> {"{:0.6f}".format(value)} </td> <td class = bg-warning> {"{:0.6f}".format(dop_abs)} </td> '
                        else:
                            htmlstr += f'<td> {"{:0.6f}".format(value)} </td> <td> {"{:0.6f}".format(dop_abs)} </td>'
                    else:
                        htmlstr += f'<td> {"{:0.6f}".format(value)} </td> <td> - </td> <td>{"{:0.6f}".format(dop_abs)}</td>'
            htmlstr += "</tr><tr>"
    with open('html_table.html', 'w', encoding='utf-8') as fh1:
        fh1.write(htmlstr)

readconfig()
start_frequency_test(conf_data)
with open("freq_test.json", "w") as write_file:
    json.dump(jsondict, write_file, indent=2)
table_generator()
