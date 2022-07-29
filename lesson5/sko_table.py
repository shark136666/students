import json

data = {}

with open('sko_result.json', 'r', encoding='utf-8') as jr:
    data.update(json.load(jr))

access_abs = input('Введите допуск для абсолютных трасс')
access_otn = input('Введите допуск для относительных трасс')

sko_result = open('sko_result.html', 'w')
htmlstr = '''<html>
    <style>
    table, th, td {
      border:1px solid black;
    }
    </style>
    <body>
        <table style="width:100%; margin-left:auto;margin-right:auto;">
            <tr>
                <th>
                    Канал
                </th>
                <th>
                    ПЧ, кГц
                </th>
                <th>
                    Аттюнеатор, дБ
                </th>
                <th>
                    Измерение, дБ
                </th>
                <th>
                    Максимум, дБ
                </th>
                <th>
                    Допуск, дБ
                </th>
            </tr>
        '''

for i in data["atthenuator"]:
    for j in data["atthenuator"][i]["IF"]:   # 300/3
        for k in data["atthenuator"][i]["IF"][j]["trace"]:  # abs/otn
            count = 0
            channel_arr = []
            channel_arr_sko = []
            for g in data["atthenuator"][i]["IF"][j]["trace"][k]:   # T, R, S, max_value
                max_value = format(float(data["atthenuator"][i]["IF"][j]["trace"][k]["max_value"]), '.8f')
                if count != 0:  # т.к. 0 индекс max value
                    channel_arr_sko.append(format(float(data["atthenuator"][i]["IF"][j]["trace"][k][g]), '.8f'))  # запись СКО
                    channel_arr.append(g)
                count += 1
                if count == (len(data["atthenuator"][i]["IF"][j]["trace"][k])):     # если достали все данные одного прохода
                    # print(data["atthenuator"][i]["IF"][j]["trace"][k])
                    # print(len(data["atthenuator"][i]["IF"][j]["trace"][k]))
                    acces = 0
                    if k == "otnosit":
                        acces = access_otn
                    else:
                        acces = access_abs
                    trace_num = len(channel_arr)

                    if float(channel_arr_sko[0]) > float(acces):    # запись строчек
                        htmlstr += f'''<tr><td>{channel_arr[0]}</td><td rowspan = {trace_num}>{j} </td><td rowspan = {trace_num}>{i}</td><td style="background-color:#FFFF00">{channel_arr_sko[0]}</td><td rowspan = {trace_num}>{max_value}</td><td rowspan = {trace_num}>{acces}</td></tr>'''
                    else:
                        htmlstr += f'''<tr><td >{channel_arr[0]}</td><td rowspan = {trace_num}>{j}</td><td rowspan = {trace_num}>{i}</td><td>{channel_arr_sko[0]}</td><td rowspan = {trace_num}>{max_value}</td><td rowspan = {trace_num}>{acces}</td></tr>'''
                    for traces in range(1, trace_num):
                        if float(channel_arr_sko[traces]) > float(acces):  # запись строчечк
                            htmlstr += f'''<tr><td>{channel_arr[traces]}</td><td style="background-color:#FFFF00">{channel_arr_sko[traces]}</td></tr>'''
                        else:
                            htmlstr += f'''<tr><td>{channel_arr[traces]}</td><td>{channel_arr_sko[traces]}</td></tr>'''

                    # if float(max_value) > float(acces):    # запись строчечк
                    #     htmlstr += f'''<tr><td>{channel_arr}</td><td>{j}</td><td>{i}</td><td style="background-color:#FFFF00">{channel_arr_sko}</td><td>{max_value}</td><td>{acces}</td></tr>'''
                    # else:
                    #     htmlstr += f'''<tr><td>{channel_arr}</td><td>{j}</td><td>{i}</td><td>{channel_arr_sko}</td><td>{max_value}</td><td>{acces}</td></tr>'''

htmlstr += '''</table>
    </body>
</html>'''
sko_result.write(htmlstr)
sko_result.close()
