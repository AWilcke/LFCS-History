from func import *

with open('full.tsv') as f:
    data = f.read().splitlines()[5:]

for line in data:
    line = line.split('\t')
    for i in range(0, len(line)):
        if line[i] == '':
            line[i] = None

    add_person(name=line[0] + ' ' + line[1], category=line[3], dates=line[2], extra=line[4], thesis=line[5], location=line[6], url=line[8])
