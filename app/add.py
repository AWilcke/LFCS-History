from func import *

with open('full.tsv') as f:
    data = f.read().splitlines()[5:]

for line in data:
    line = line.split('\t')
    for i in range(0, len(line)):
        if line[i] == '':
            line[i] = None
    try:
        line[3] = int(line[3])
    except:
        line[3] = None
    try:
        line[2] = int(line[2])
    except:
        line[2] = None

    add_person(name=line[0] + ' ' + line[1], category=line[4], start=line[2], end=line[3], extra=line[5], thesis=line[6], location=line[8], url=line[10])



