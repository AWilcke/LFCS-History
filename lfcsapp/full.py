from lfcsapp.func import *

def add_all():
    with open('full.tsv') as f:
        data = f.read().splitlines()[5:]

    for line in data:
        line = line.split('\t')
        for i in range(0, len(line)):
            if line[i] == '':
                line[i] = None

        add_person(name=line[0] + ' ' + line[1], category=line[3], dates=line[2], extra=line[4], thesis=line[5], location=line[6], url=line[8])

def link_all():
    with open('full.tsv') as f:
        data = f.read().splitlines()[5:]

    for line in data:
        line = line.split('\t')
        for i in range(0, len(line)):
            if line[i] == '':
                line[i] = None
        if line[4] and line[3] and (line[3].lower()=='phd' or line[3].lower()=='pg' or line[3].lower()=='postdoc'):
            link_person(line[0], line[1], line[3], line[4].split(', '))

def link_person(first, last, cat, supervisors):
    first = unicode(first, 'utf-8')
    last = unicode(last, 'utf-8')
    
    person = People.query.search(first + ' ' + last).first()
    if not person:
        return
    if cat.lower() == 'phd':
        person.phd.supervisor = []
        for sup in supervisors:
            try:
                p = People.query.search(sup).first().staff
            except:
                p=None
            if p:
                person.phd.supervisor.append(p)

    elif cat.lower() == 'pg' or cat.lower() == 'postdoc':
        try:
            p = People.query.search(supervisors[0]).first().staff
        except:
            p = None
        if p:
            person.postdoc.primary_investigator = p
        person.postdoc.investigators = []
        for sup in supervisors[1:]:
            try:
                p = People.query.search(sup).first().staff
            except:
                p=None
            if p:
                person.postdoc.investigators.append(p)

    db.session.add(person)
    db.session.commit()

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
