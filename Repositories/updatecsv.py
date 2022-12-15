from tempfile import NamedTemporaryFile
import shutil
import csv
import sys
import pandas as pd

orgName = "wikimedia"
filename = f"{orgName}_repository.csv"
#filter repos based on 11% pp condition;
df = pd.read_csv(filename)

dfData = df['isCriteria2Met'] == 1
filteredRepos = df[dfData]
print("number of repositories with at least 11% pp files:", len(filteredRepos))
# for row in filteredRepos:
#     print(row['name'])


sys.exit()


tempfile = NamedTemporaryFile(mode='w', delete=False)

fields = ['number', 'name', 'fulname', 'id','total_count','iac_count','iacPercent','isCriteria2Met']

with open(filename, 'r') as csvfile, tempfile:
    reader = csv.DictReader(csvfile, fieldnames=fields)
    writer = csv.DictWriter(tempfile, fieldnames=fields)

    for row in reader:
        #print('iac percent:',row)
        if float(row['iacPercent']) >= float(0.11):
            row = {'number': row['number'], 'name': row['name'], 'fulname': row['fulname']
                   , 'id': row['id'], 'total_count': row['total_count'], 'iac_count': row['iac_count']
                   , 'iacPercent': row['iacPercent'], 'isCriteria2Met': 1}
            writer.writerow(row)
        else:
            row = {'number': row['number'], 'name': row['name'], 'fulname': row['fulname']
                   , 'id': row['id'], 'total_count': row['total_count'], 'iac_count': row['iac_count']
                   , 'iacPercent': row['iacPercent'], 'isCriteria2Met': 0}
            writer.writerow(row)

shutil.move(tempfile.name, filename)
print('done')