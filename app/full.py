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

def add_person(name, category, dates=None, extra=None, thesis=None, location=None, url=None):
    person = People.query.filter(People.name==name).first()
    if not person:
        person = People(name=name, url=url, location=location)
        db.session.add(person)

    if category:
        if category.lower()=='staff':
            if not person.staff:
                person.staff = Staff()
            if extra:
                person.staff.position=[]
                for role in extra.split(' & '):
                    m = re.match('(.*) \((\d\d\d\d)-(\d\d\d\d)\)', role)
                    if m:
                        p = Positions(m.group(1))
                        p.dates.append(Dates(m.group(2), m.group(3)))
                    else:
                        p = Positions(role)
                        p.dates.append(Dates(None, None))
                    person.staff.position.append(p)

            if dates:
                person.staff.dates=[]
                for pair in dates.split(' ,'):
                    try:
                        start, end = pair.split('-')
                    except:
                        print pair
                        raise
                    start=start.strip('?')
                    end=end.strip('?')
                    try:
                        int(start)
                    except:
                        start=None
                    try:
                        int(end)
                    except:
                        end=None
                    person.staff.dates.append(Dates(start, end))
                        
        
        elif category.lower()=='phd':
            if not person.phd:
                person.phd = PhD(thesis=thesis)
            elif thesis:
                person.phd.thesis=thesis
            
            if dates:
                person.phd.dates=[]
                for pair in dates.split(' ,'):
                    start, end = pair.split('-')
                    start=start.strip('?')
                    end=end.strip('?')
                    try:
                        int(start)
                    except:
                        start=None
                    try:
                        int(end)
                    except:
                        end=None

                    person.phd.dates.append(Dates(start, end))

        elif category.lower()=='pg' or category.lower()=='postdoc':
            if not person.postdoc:
                person.postdoc = PostDoc()
           
            if dates:
                person.postdoc.dates=[]
                for pair in dates.split(' ,'):
                    start, end = pair.split('-')
                    start=start.strip('?')
                    end=end.strip('?')
                    try:
                        int(start)
                    except:
                        start=None
                    try:
                        int(end)
                    except:
                        end=None
                    person.postdoc.dates.append(Dates(start, end))

        else:
            if not person.associate:
                person.associate = Associates()
            if extra:
                person.associate.position=[]
                for role in extra.split(' & '):
                    m = re.match('(.*) \((\d\d\d\d)-(\d\d\d\d)\)', role)
                    if m:
                        p = Positions(m.group(1))
                        p.dates.append(Dates(m.group(2), m.group(3)))
                    else:
                        p = Positions(role)
                        p.dates.append(Dates(None, None))
                    person.associate.position.append(p)
            
            if dates:
                person.associate.dates=[]
                for pair in dates.split(' ,'):
                    start, end = pair.split('-')
                    start=start.strip('?')
                    end=end.strip('?')
                    try:
                        int(start)
                    except:
                        start=None
                    try:
                        int(end)
                    except:
                        end=None
                    person.associate.dates.append(Dates(start, end))
    
    if dates:
        person.dates=[]
        for pair in dates.split(' ,'):
            start, end = pair.split('-')
            start=start.strip('?')
            end=end.strip('?')
            try:
                int(start)
            except:
                start=None
            try:
                int(end)
            except:
                end=None
            person.dates.append(Dates(start, end))
    
    if location:
        person.location=location
    if url:
        person.url=url

    db.session.commit()
