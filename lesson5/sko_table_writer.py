# -*- coding: utf-8 -*-
import json

with open('sko_result.json') as f:
    templates = json.load(f)

with open('sko_table.html', 'w', encoding="utf-8") as file:
    file.write("""
<html lang="ru">
  <head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta http-equiv="charset" content="utf8">
    <meta http-equiv="content-type" content="text/html;">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">

    <title>Hello, world!</title>

    <style>
table, th, td {
    border: 1px solid black;
	border-collapse: collapse;
}
th, td {
    padding: 30px;;
}
    </style>

  </head>

  <body>

    <h1>Результаты СКО</h1>

    <table style="width:100%">
""")

#допуски
count = 0
dop = []
for i in templates['atthenuator'].keys():
    for k in templates['atthenuator'][f'{i}']['IF'].keys():
        for d in range(2):
            dop.append(int(input()))


with open('sko_table.html', 'a', encoding="utf-8") as file:
    file.write(f'<td>Канал</td>\n')
"""цикл по смене DB"""
for i in templates['atthenuator'].keys():  #аттенюаторы
    #print(  )
    print('аттенюатор = ', i)
    """ смена чистот """
    for k in templates['atthenuator'][f'{i}']['IF'].keys(): #ПЧ
        #print(  )
        print('ПЧ = ', k)

        with open('sko_table.html', 'a', encoding="utf-8") as file:
            """Выбор абсалют и относ"""
            for q in templates['atthenuator'][f'{i}']['IF'][f'{k}']['trace'].keys():
                with open('sko_table.html', 'a', encoding="utf-8") as file:
                    file.write(f'<td>')
                """вывод трасс"""
                for t in templates['atthenuator'][f'{i}']['IF'][f'{k}']['trace'][f'{q}'].keys():

                    if t != "max_value":
                        print(t)
                        a = templates['atthenuator'][f'{i}']['IF'][f'{k}']['trace'][f'{q}'][f'{t}']
                        with open('sko_table.html', 'a', encoding="utf-8") as file:  # открываем файл штмл на дозапись
                            file.write(f'<p> {t} = {a} </p>\n')

                        print(templates['atthenuator'][f'{i}']['IF'][f'{k}']['trace'][f'{q}'][f'{t}'])  #значение измерения
                    else:
                        print("max_value", templates['atthenuator'][f'{i}']['IF'][f'{k}']['trace']['absolute']['max_value']) #значение максимума

                with open('sko_table.html', 'a', encoding="utf-8") as file:
                    file.write(f'</td>\n')

with open('sko_table.html', 'a', encoding="utf-8") as file:
    file.write("""
    <tr>
    <td>ПЧ, кГц</td>
    """)
"""выписываем ПЧ"""
for i in templates['atthenuator'].keys():  #аттенюаторы
    print('аттенюатор = ', i)
    """ смена чистот """
    for k in templates['atthenuator'][f'{i}']['IF'].keys(): #ПЧ
        with open('sko_table.html', 'a', encoding="utf-8") as file:  # открываем файл штмл на дозапись
            file.write(f'<td> {k} </td>\n')
            file.write(f'<td> {k} </td>\n')

with open('sko_table.html', 'a', encoding="utf-8") as file:
    file.write("""
    <tr>
    <td>Аттентюатор, дБ</td>
    """)
"""выписываем аттенюаторы"""
for i in templates['atthenuator'].keys():  #аттенюаторы
    with open('sko_table.html', 'a', encoding="utf-8") as file:  # открываем файл штмл на дозапись
        file.write(f'<td> {i} </td>\n')
        file.write(f'<td> {i} </td>\n')
        file.write(f'<td> {i} </td>\n')
        file.write(f'<td> {i} </td>\n')

with open('sko_table.html', 'a', encoding="utf-8") as file:
    file.write("""
    <tr>
    <td>Максимум, дБ</td>
    """)
"""выписываем максимумы"""
for i in templates['atthenuator'].keys():  #аттенюаторы
    """ смена чистот """
    for k in templates['atthenuator'][f'{i}']['IF'].keys(): #ПЧ
        #print(  )
        print('ПЧ = ', k)
        """Выбор абсалют и относ"""
        for q in templates['atthenuator'][f'{i}']['IF'][f'{k}']['trace'].keys():
            """вывод трасс"""
            for t in templates['atthenuator'][f'{i}']['IF'][f'{k}']['trace'][f'{q}'].keys():

                if t != "max_value":
                    print(t)
                    print(templates['atthenuator'][f'{i}']['IF'][f'{k}']['trace'][f'{q}'][f'{t}'])  #значение измерения
                else:
                    a = templates['atthenuator'][f'{i}']['IF'][f'{k}']['trace'][f'{q}'][f'{t}']
                    if a > dop[count]:
                        count += 1
                        with open('sko_table.html', 'a', encoding="utf-8") as file:
                            file.write(f'<td class = bg-warning> {a} </td>\n')
                        print(templates['atthenuator'][f'{i}']['IF'][f'{k}']['trace']['absolute']['max_value']) #значение максимума
                    else:
                        count += 1
                        with open('sko_table.html', 'a', encoding="utf-8") as file:
                            file.write(f'<td> {a} </td>\n')
                        print(templates['atthenuator'][f'{i}']['IF'][f'{k}']['trace']['absolute'][
                                  'max_value'])  # значение максимума

with open('sko_table.html', 'a', encoding="utf-8") as file:
    file.write("""
    <tr>
    <td>Допуск, дБ</td>
    """)

for count in dop:
    with open('sko_table.html', 'a', encoding="utf-8") as file:
        file.write(f'<td> {count} </td>\n')

with open('sko_table.html', 'a', encoding="utf-8") as file:
    file.write("""
      </tr>
    </table>
  </body>
</html>
        """)