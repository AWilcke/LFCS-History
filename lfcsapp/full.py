from lfcsapp.func import *
import json

def add_all(num=None):
    with open('full.tsv') as f:
        if num:
            data = f.read().splitlines()[num]
        else:
            data = f.read().splitlines()[5:]

    for line in data:
        line = line.split('\t')
        for i in range(0, len(line)):
            if line[i] == '':
                line[i] = None

        add_person(name=line[0] + ' ' + line[1], category=line[3], dates=line[2], extra=line[4], thesis=line[5], location=line[7], url=line[9], nationality=line[8])

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

    print person.name

    if cat.lower() == 'pg' or cat.lower() == 'phd':
        person.phd.supervisor = []
        for sup in supervisors:
            try:
                p = People.query.search(sup).first().staff
            except:
                p=None
            if p:
                person.phd.supervisor.append(p)

    elif cat.lower() == 'postdoc':
        person.postdoc.investigators = []
        for sup in supervisors:
            try:
                p = People.query.search(sup).first().staff
            except:
                p=None
            if p:
                person.postdoc.investigators.append(p)

    db.session.add(person)
    db.session.commit()

def add_person(name, category, dates=None, extra=None, thesis=None, location=None, url=None, nationality=None):
    person = People.query.filter(People.name==name).first()
    if not person:
        person = People(name=name, url=url, location=location, nationality=nationality)
        db.session.add(person)

    print person.name

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
                for pair in dates.split(','):
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
                        
        
        elif category.lower()=='pg'or category.lower()=='phd':
            if not person.phd:
                person.phd = PhD(thesis=thesis)
            elif thesis:
                person.phd.thesis=thesis
            
            if dates:
                person.phd.dates=[]
                for pair in dates.split(','):
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

                    person.phd.dates.append(Dates(start, end))

        elif category.lower()=='postdoc':
            if not person.postdoc:
                person.postdoc = PostDoc()
           
            if dates:
                person.postdoc.dates=[]
                for pair in dates.split(','):
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
                for pair in dates.split(','):
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
        for pair in dates.split(','):
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

def grant_person(name, title, start, end, value, url, ref, org):
    person = People.query.filter_by(name=name).first()
    if not person:
        return
    grant_refs = [grant.ref for grant in person.staff.grants]
    if ref in grant_refs:
        return
    grant = Grants()
    grant.title = title
    try:
        grant.dates = Dates(start.split(' ')[-1], end.split(' ')[-1])
    except:
        grant.dates = Dates(start, end)
    try:
        grant.value = int(value.replace(',',''))
    except:
        grant.value = value
    grant.url = url
    grant.ref = ref
    grant.org = org
    print title
    person.staff.grants.append(grant)

def grant_all():
    with open('grants.json','r') as f:
        data = f.read().splitlines()

    with open('exploregrant.json','r') as f:
        data2 = f.read().splitlines()

    for line in data[1:-1] + data2[1:-1]:
        js = json.loads(line.rstrip(','))
        grant_person(js['person'], js['title'], js['start'], js['end'], js['value'], js['url'], js['ref'], js['org'])

    db.session.commit()

def grant2_all():
    with open('grants2.json','r') as f:
        data = f.read().splitlines()
    with open('exploregrant2.json','r') as f:
        data2 = f.read().splitlines()

    for line in data[1:-1] + data2[1:-1]:
        js = json.loads(line.rstrip(','))
        grant_secondary_person(js['person'], js['title'], js['primary'], js['ref'])

    db.session.commit()


def grant_secondary_person(name, g_title, primary, ref):
    person = People.query.filter(People.name==name).first()
    if not person:
        return
    primary = People.query.search(primary.split(',')[0]).filter(People.staff).all()
    for pos in primary:
        match = Grants.query.filter(Grants.staff==pos.staff, Grants.ref==ref).first()
        if match:
            print match.title.encode('utf-8')
            if person.staff not in match.secondary:
                match.secondary.append(person.staff)
            return

def research_explorer(name, link):
    person = People.query.filter(People.name==name).first()
    if not person.staff:
        return
    print name
    person.staff.research_explorer = link

def research_all():
    with open('explorer.json','r') as f:
        data = f.read().splitlines()

    for line in data[1:-1]:
        js = json.loads(line.rstrip(','))
        research_explorer(js['person'], js['link'])

    db.session.commit()

def role(name, role):
    person = People.query.filter(People.name==name).first()
    if not person.staff:
        return
    print name
    pos_names = [position.position for position in person.staff.position]
    if role not in pos_names:
        person.staff.position.append(Positions(role))

def role_all():
    with open('exploreroles.json','r') as f:
        data = f.read().splitlines()

    for line in data[1:-1]:
        js = json.loads(line.rstrip(','))
        role(js['person'],js['role'])

    db.session.commit()

def build_db():
    add_all()
    link_all()
    grant_all()
    grant2_all()
    research_all()
    role_all()
