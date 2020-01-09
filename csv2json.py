import sys
import csv
import json

csvreader = csv.reader(sys.stdin)
names = ['Line'] + next(csvreader)
items = []
for i, row in enumerate(csvreader):
    item = {name: value for name, value in zip(names, [i+2] + row)}
    items.append(item)

json.dump(items, sys.stdout, indent=4)
