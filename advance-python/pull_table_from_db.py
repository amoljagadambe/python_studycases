import pymysql
import re
import csv

conn = pymysql.connect(host='43.231.127.150', port=3306, user='amol-jagadambe', password='Gais@2021$amol-jagadambe',
                       database='accent17')

cursor = conn.cursor()
query = 'SELECT distinct sentence FROM accent17.tb_sentence'
csv_file_path = 'D:\\Personal\\Projects\\python_studycases\\advance-python\\sentence_corpus.csv'

try:
    cursor.execute(query)
    rows = cursor.fetchall()
finally:
    conn.close()

# Write result to file.
with open(csv_file_path, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter='\t')
    for row in rows:
        data_list = []

        the_string = re.sub('[^.,a-zA-Z0-9 \n\.]', '', str(row[0]))
        data_list.append(the_string)
        the_string = the_string.replace(' ', '')
        data_list.append(len(the_string.replace('.', '')))
        csvwriter.writerow(data_list)
