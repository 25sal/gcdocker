import csv

with open('7_freezer.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    with open('7_freezer2.csv') as csv_write:
	csv_writer = csv.writer(csv_write, delimiter = ' ')
	for row in csv_reader:
	     csv_writer.writerow([row[0], row[1]])
