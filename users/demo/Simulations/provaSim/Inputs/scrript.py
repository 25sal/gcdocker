import csv
import os

with open("./0_run_0_1_ein.csv", "r") as f:
    with open("./0_run_0_1_ein2.csv", "w") as f2:
        reader = csv.reader(f, delimiter = ' ')
        writer = csv.writer(f2, delimiter=' ')
        for data in reader:
            entry = []
            entry.append(data[0])
            entry.append(float(data[1])/1000)
            writer.writerow(entry)
os.remove("./0_run_0_1_ein.csv")
os.rename("./0_run_0_1_ein2.csv", "./0_run_0_1_ein.csv")


with open("./0_run_4_1_ein.csv", "r") as f:
    with open("./0_run_4_1_ein2.csv", "w") as f2:
        reader = csv.reader(f, delimiter = ' ')
        writer = csv.writer(f2, delimiter=' ')
        for data in reader:
            entry = []
            entry.append(data[0])
            entry.append(float(data[1])/1000)
            writer.writerow(entry)
os.remove("./0_run_4_1_ein.csv")
os.rename("./0_run_4_1_ein2.csv", "./0_run_4_1_ein.csv")

with open("./6_run_3_1_eout.csv", "r") as f:
    with open("./6_run_3_1_eout2.csv", "w") as f2:
        reader = csv.reader(f, delimiter = ' ')
        writer = csv.writer(f2, delimiter=' ')
        for data in reader:
            entry = []
            entry.append(data[0])
            entry.append(float(data[1])/1000)
            writer.writerow(entry)
os.remove("./6_run_3_1_eout.csv")
os.rename("./6_run_3_1_eout2.csv", "./6_run_3_1_eout.csv")
