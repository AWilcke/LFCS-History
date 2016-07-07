from func import *

def add_all():
    with open('full.tsv') as f:
        data = f.read().splitlines()[5:]

    for line in data:
        line = line.split('\t')
        for i in range(0, len(line)):
            if line[i] == '':
                line[i] = None

        add_person(name=line[0] + ' ' + line[1], category=line[3], dates=line[2], extra=line[4], thesis=line[5], location=line[6], url=line[8])

'''
def link_all():
    with open('full.tsv') as f:
        data= f.read().splitlines()[5:]

    for line in data:
        line=line.split('\t')
        for i in range(0, len(line)):
            if line[i] == '':
                line[i] = None
       
        try:
            person=People.query.search(line[0] + ' ' + line[1])[0]
        except:
            #print line[0] + ' ' + line[1]
            pass 
        if line[3]:
            if line[3].lower()=='phd':
                #person.phd.supervisor=[]
                if line[4]:
                    for sup in line[4].split(', '):
                        try:
                            print People.query.search(sup)[0].staff
                        except:
                            pass
        elif line[3].lower()=='pg' or line[3].lower()=='postdoc':
            try:
                person.postdoc.primary_investigator=People.query.search(line[4].split(', ')[0])[0].staff
            except:
                person.postdoc.primary_investigator=None

            person.postdoc.investigators=[]
            if line[4]:
                for sup in line[4].split(', ')[1:]:
                    try:
                        person.postdoc.investigators.append(People.query.search(sup)[0].staff)
                    except:
                        pass
    db.session.commit()
'''
