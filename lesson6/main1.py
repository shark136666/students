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
                qwe=[]
                qwe =  config['range'][f'{key}'].split(' ')
                conf_data['range'][f'{key}'] = HzConvertor(int (qwe[0]),qwe[1])

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

        #date_inf = query(CMT,f'SYST:DATE?')
        time_inf = query(CMT,f'SYST:TIME?')
        idn_inf = list(query(CMT,f'*IDN?'))

        #print(date_inf)
        print(time_inf)
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
        tracc_count = 3
        if int(query(CMT,f'SERV:PORT:COUN?')) < tracc_count:
                tracc_count = int(query(CMT,f'SERV:PORT:COUN?'))
        
        param(conf_data)
        double_point()
        config = configparser.ConfigParser()
        config.read_file(open(r'config.txt'))
        #цикл вывода otn


        for keys in range(1,int(len(conf_data['range'].keys())/2)+1):
                start_data = config["range"][f'{keys}_start']
                stop_data = config["range"][f'{keys}_stop']
                jsondict.update ({f'{start_data} - {stop_data}':{}})
                jsondict[f'{start_data} - {stop_data}'].update({'max_abs' : 0.0,'max_otn' : 0.0})
                

        for canal in range(1,tracc_count+1):
                #создание 3 трасс
                write(CMT, f'CALC1:PAR:COUN 1')
                write(CMT, f'CALC1:PAR1:DEF S{canal}{canal}')
                singlescan(CMT)
                #--------------------
                
                for keys in range(1,int(len(conf_data['range'].keys())/2)+1): 
                        start = conf_data["range"][f'{keys}_start']
                        stop = conf_data["range"][f'{keys}_stop']
                        start_data = config["range"][f'{keys}_start']
                        stop_data = config["range"][f'{keys}_stop']
                        

                        write(CMT, f'CALC1:TRAC:MARK1:STAT ON')
                        write(CMT, f'CALC1:TRAC:MARK2:STAT ON')
                        write(CMT, f'CALC1:MARK1:X {start}')
                        write(CMT, f'CALC1:MARK2:X {stop}')
                        write(CMT, f'CALC1:MST ON')
                        write(CMT, f'CALC1:MST:DOM ON')
                        
                        mst_data = query_ascii_values(CMT,f'CALC:MST:DATA?')
                        trace = query(CMT, f'CALC1:PAR:DEF?')
                        if k < 2 :
                                jsondict.update({f'{trace}': {}})
                                k += 1
                        jsondict[f'{trace}'].update({f'{start_data} - {stop_data}':{}})
                        print(jsondict)
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

                for keys in range(1,int(len(conf_data['range'].keys())/2)+1): 
                        start = conf_data["range"][f'{keys}_start']
                        stop = conf_data["range"][f'{keys}_stop']
                        start_data = config["range"][f'{keys}_start']
                        stop_data = config["range"][f'{keys}_stop']


                        for n_trace in range(1,3):
                                write(CMT, f'CALC:PAR{n_trace}:SEL')
                                write(CMT, f'CALC1:TRAC{n_trace}:MARK1:STAT ON')
                                write(CMT, f'CALC1:TRAC{n_trace}:MARK2:STAT ON')
                                write(CMT, f'CALC1:MARK1:X {start}')
                                write(CMT, f'CALC1:MARK2:X {stop}')
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



readconfig()
start_frequency_test(conf_data)
with open("p-p_result.json", "w") as write_file:
	json.dump(jsondict, write_file, indent=2)
	
