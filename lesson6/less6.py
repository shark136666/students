import configparser
config = configparser.ConfigParser()
config.read('config.cfg')
arr1=config['range']['ranges'].split(',')
arr2=[]
for i in range(len(arr1)):
    arr2.append(arr1[i].split(' '))
def Convertor(n,freq):
	if freq == "kHz":
		return int(n*1e+3)
	elif freq == "MHz":
		return int(n*1e+6)
	elif freq == "GHz":
		return int(n*1e+9)
	else: return print("Incorrect value")
for i in range(len(arr2)):
    print(Convertor(int(arr2[i][0]),arr2[i][1]))
    print(Convertor(int(arr2[i][2]),arr2[i][3]))