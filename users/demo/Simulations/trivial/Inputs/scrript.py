import csv
import os

with open("./8.csv", "r") as f:
    with open("./88.csv", "w") as f2:
        reader = csv.reader(f, delimiter = ' ')
        writer = csv.writer(f2, delimiter=' ')
        for data in reader:
            entry = []
            entry.append(data[0])
            entry.append(float(data[1])/10)
            writer.writerow(entry)

