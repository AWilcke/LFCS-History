import re

with open('first.csv') as datafile:
    first=datafile.read().splitlines()[1:]
with open('second.csv') as datafile:
    second=datafile.read().splitlines()[1:]

output = {}

for line in (first+second):
    line = line.split(',')
    name = line[4] + ' ' + line[3]
    year = line[2]
    role = line[1].lower()
    url = line[0]

    if name not in output.keys():
        output[name] = {'year':year + '-' + year, 'role':[role + ' (' + year + '-' + year + ')'], 'url':url}
    else:
        m = re.match('(\d\d\d\d)-(\d\d\d\d)', output[name]['year'])
        start = m.group(1)
        end = m.group(2)
        if year>end:
            end = year
        elif year<start:
            start = year
        output[name]['year'] = start + '-' + end
        
        newrole = []
        positions = []
        for r in output[name]['role']:
            m = re.match('(.*) \((\d\d\d\d)-(\d\d\d\d)\)', r)
            position = m.group(1)
            positions.append(position)
            start = m.group(2)
            end = m.group(3)
            
            if role == position:
                if year>end:
                    end = year
                elif year<start:
                    start = year
            newrole.append(position + ' (' + start + '-' + end + ')')
        if role not in positions:
            newrole.append(role + ' (' + start + '-' +  end + ')')
        output[name]['role'] = newrole

        #only update url if is most recent known
        if all(year>i for i in output[name]['year']):
            output[url] = url

with open('output.txt','w') as f:
    f.write(str(output))
