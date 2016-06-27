import re

with open('output2.txt') as f:
    dic = eval(f.read())

csv = ''
for name in dic.keys():
    m = re.match('(.+) (\S+)', name)
    if m:
        first = m.group(1)
        last = m.group(2)
        role = dic[name]['role']
        url = dic[name]['url']
        start, end = dic[name]['year'].split('-')

        csv += first + ',' + last + ',' + start + ',' + end + ',' + ' and '.join(role) + ',,,' + url + '\n'

with open('csv2.csv','w') as o:
    o.write(csv)

