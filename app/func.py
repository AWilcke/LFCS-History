from database import *
import re

def add_person(name, category, dates=None, extra=None, thesis=None, location=None, url=None):
    person = People.query.filter(People.name==name).first()
    if not person:
        person = People(name=name, url=url, location=location)
        db.session.add(person)

    if category:
        if category.lower()=='staff':
            if not person.staff:
                person.staff = Staff()
                person.size+=1
            if extra:
                person.staff.position=[]
                for role in extra.split(' & '):
                    m = re.match('(.*) \((\d\d\d\d)-(\d\d\d\d)\)', role)
                    if m:
                        p = Positions(m.group(1))
                        p.dates.append(Dates(m.group(2), m.group(3)))
                    else:
                        p = Positions(role)
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
                person.size+=1
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
                person.size+=1
           
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
                person.size+=1
            if extra:
                person.associate.position=[]
                for role in extra.split(' & '):
                    m = re.match('(.*) \((\d\d\d\d)-(\d\d\d\d)\)', role)
                    if m:
                        p = Positions(m.group(1))
                        p.dates.append(Dates(m.group(2), m.group(3)))
                    else:
                        p = Positions(role)
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

def base_search(query):
    people = People.query.search(query).all()
    positions = Positions.query.search(query).all()
    phd = PhD.query.search(query).all()

    results = {}
    for p in people:
        rank = db.engine.execute(db.func.ts_rank(p.search_vector, db.func.plainto_tsquery(query))).fetchone()[0]
        if p in results.keys():
            if results[p]<rank:
                results[p]=rank
        else:
            results[p] = rank

    for position in positions:
        rank = db.engine.execute(db.func.ts_rank(position.search_vector, db.func.plainto_tsquery(query))).fetchone()[0]
        if position.staff:
            if position.staff.person in results.keys():
                if results[position.staff.person]<rank:
                    results[position.staff.person] = rank
            else:
                results[position.staff.person] = rank
        elif position.associate:
            if position.associate.person in results.keys():
                if results[position.associate.person]<rank:
                    result[position.associate.person] = rank
            else:
                results[position.associate.person] = rank

    for s in phd:
        rank = db.engine.execute(db.func.ts_rank(s.search_vector, db.func.plainto_tsquery(query))).fetchone()[0]
        if s.person in results.keys():
            if results[s.person]<rank:
                results[s.person]=rank
        else:
            results[s.person]=rank

    return sorted(results, key=results.get, reverse=True)
