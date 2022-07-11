import json

#создаем словарь для записи с json
data = {}

#открываем файл и загружаем данные
with open('p-p_result.json', 'r', encoding='utf-8') as fh: 
    data.update(json.load(fh))

#ввод допуска
dop_abs = 2
dop_otn = 3
#dop_abs = float(input("Введите значение допуска abs "))
#dop_otn = float(input("Введите значение допуска otn "))
#создаем строку для ввода в html страницу
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
	<table border='1' >\
"
#Цикл для заолнения html страницы

for trace in data[Range]["otnosit"].keys():
    for Range in data.keys():


for Range in data.keys():
    htmlstr += f'<th><tr><td>Диапазон</td><td colspan="3">{Range}</th>'
    htmlstr += "<tr><td>Трассы</td>  <td>Нер-ть,дБ</td>  <td>Макс.дБ</td>    <td>Допуск,дБ</td> </tr><tr> "
    """ ---цикл прохода по otn--- """
    for trace in data[Range]["otnosit"].keys():
        if trace != "max_value":
            value = data[Range]["otnosit"][f'{trace}']
            htmlstr += f'<td>{trace}</td><td>{value}</td>'
            if value == data[Range]["otnosit"]["max_value"]:
                if value > dop_otn:
                    htmlstr += f'<td class = bg-warning>{value}</td>'
                    htmlstr += f'<td class = bg-warning> {dop_otn} </td><tr>'
                else:
                    htmlstr += f'<td >{value}</td>'
                    htmlstr += f'<td > {dop_otn} </td><tr>'
            else:
                htmlstr += "<td>-</td>"
                htmlstr += f'<td> {dop_otn} </td> <tr>'
        


    """ ---цикл прохода по abs--- """      
    for trace in data[Range]["absolute"].keys():  
        if trace != "max_value":
            value = data[Range]["absolute"][f'{trace}']
            htmlstr += f'<td>{trace}</td><td>{value}</td>'
            if value == data[Range]["absolute"]["max_value"]:
                if value > dop_otn:
                    htmlstr += f'<td class = bg-warning>{value}</td>'
                    htmlstr += f'<td class = bg-warning> {dop_abs} </td><tr>'
                else:
                    htmlstr += f'<td >{value}</td>'
                    htmlstr += f'<td > {dop_abs} </td><tr>'
            else:
                htmlstr += "<td>-</td>"
                htmlstr += f'<td> {dop_abs} </td> <tr>'
    htmlstr += "<th>"
#записываем в файл			
with open('html_table.html', 'w', encoding='utf-8') as fh1: 
     fh1.write(htmlstr)
