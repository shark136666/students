import json
from jinja2 import Template 

data = {}

#открываем файл и загружаем данные
with open('sko_result.json', 'r', encoding='utf-8') as fh: 
    data.update(json.load(fh))

dop = float(input())
	
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
	<table border='1' ><tr><td>Канал</td><td>ПЧ, Гц</td>\
<td>Аттенюатор, дБ</td><td>Измерение, дБ</td><td>Максимум, дБ</td>\
<td>Допуск, дБ</td></tr><tr>\
"

#ПЧ, Гц
for i in data["atthenuator"].keys():
	#Аттенюатор, дБ
	for k in data["atthenuator"][f'{i}']["IF"].keys():
		for j in data["atthenuator"][f'{i}']["IF"][f'{k}']["trace"].keys():
			count = 0
			for n in data["atthenuator"][f'{i}']["IF"][f'{k}']["trace"][f'{j}'].keys():
				if n != "max_value":
					count += 1
					if count == 1:
						htmlstr += f'<tr><td>{n}</td>'
						l = data["atthenuator"][f'{i}']["IF"][f'{k}']["trace"][f'{j}'].keys()
						htmlstr += f'<td rowspan={len(l)-1}>[{k}]</td><td rowspan={len(l)-1}>[{i}]</td>'
						max_value = data["atthenuator"][f'{i}']["IF"][f'{k}']["trace"][f'{j}']["max_value"]
						a = data["atthenuator"][f'{i}']["IF"][f'{k}']["trace"][f'{j}'][f'{n}']
						if a > dop:
							htmlstr += f'<td class = bg-warning>[{a}]</td><td rowspan={len(l)-1} >[{max_value}]</td>'
						else:
							htmlstr += f'<td>[{a}]</td><td rowspan={len(l)-1} >[{max_value}]</td>'
						
						htmlstr += f'<td rowspan={len(l)-1}  >[{dop}]</td>'
						
						
					else:
						a = data["atthenuator"][f'{i}']["IF"][f'{k}']["trace"][f'{j}'][f'{n}']
						if a > dop:
							htmlstr += f'<tr><td>{n}</td><td class = bg-warning>[{a}]</td>'
						else:
							htmlstr += f'<tr><td>{n}</td><td >[{a}]</td>'
						
						
					
				
with open('html_table.html', 'w', encoding='utf-8') as fh1: 
     fh1.write(htmlstr)

