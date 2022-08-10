



def disable_all_correctors(inst):    
    inst.write(f"SENS:CORR:STAT 0")
    inst.write(f"SYST:CORR 0")
    inst.write(f"SERV:REC:LIN:STAT 0")
    inst.write(f"SERV:REC:CORR:STAT 0")
    inst.write(f"SERV:SYST:SENS:CORR 0")
    inst.write(f"SERV:SYST:IFSW:CORR 0")
    

def check_error(inst):
    responce = inst.query('SYST:ERR?')    
    if "No error" not in responce:        
        print(responce)
        #pass
    else:        
        pass
        #print('succes')

def enable_ifbf_for_all_segment(inst):
    data = inst.query(f'SENSe1:SEGMent:DATA?').split(',')
    data[2]=0
    str1 = ''.join(str(e)+',' for e in data)
    inst.write(f'SENSe1:SEGMent:DATA {str1[:-1]}')
    #check_error(inst)