# -*- coding: utf-8 -*-
"""
Created on Mon Jun 21 09:28:15 2021
@author: kuzma.m
"""

import pyvisa as visa
import time


# Подключение к SNVNA
rm = visa.ResourceManager()
rm = visa.ResourceManager('@py')
try:
    CMT = rm.open_resource('TCPIP0::localhost::5025::SOCKET')
except:
    print("Failure to connect to VNA!")
    print("Check network settings")

#The VNA ends each line with this. Reads will time out without this
CMT.read_termination='\n'
#Set a really long timeout period for slow sweeps
CMT.timeout = 100000


def dicorate(func):
    def wrapper(connect, command):
        print("start")
        func(connect, command)
        err = connect.query(f'SYST:ERR?')
        if  err != "0, No error":
            print(err)
        print("end")
    return wrapper





# функции
def convert (m, f):
    if  f == "GHz":
        m = m * 1000000000
    if  f == "kHz":
        m = m * 1000
    if  f == "MHz":
        m = m * 1000000
    return m


    
   
def scan(connect):
    connect.write(f'TRIG:SOUR BUS')
    ERR(CMT)
    connect.write(f'INIT:CONT ON')
    ERR(CMT)
    connect.write(f'TRIG:SING')
    ERR(CMT)
    connect.query(f'*OPC?')
    ERR(CMT)

@dicorate
def write (connect, command):
    connect.write(command)
    
write(CMT, f'SENS:FREQ:STAR {convert(1, "GHz")}')
write(CMT, f'SENS:FREQ:STAR {convert(1, "GHz")}')
