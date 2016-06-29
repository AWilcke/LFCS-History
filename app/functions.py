from database import *
import re

def addPerson(name, role, start=None, end=None, position=None, location=None, thesis=None, url=None):
    if role.lower() =="phd" or role.lower() == "pg":
        new = PhD(name=name, start=start, end=end, thesis=thesis, location=location, url=url)
    elif role.lower() == 'staff':
        new = Staff(name=name, start=start, end=end, location=location, url=url)
        for role in position.split(' & '):
            m = re.match('(.*) \((\d\d\d\d)-(\d\d\d\d)\)', role)
            if m:
                p = Positions(m.group(1), start=m.group(2), end=m.group(3))
                new.position.append(p)

    else:
        new = Associates(name=name, start=start, end=end, location=location, url=url)
        for role in position.split(' & '):
            m = re.match('(.*) \((\d\d\d\d)-(\d\d\d\d)\)', role)
            if m:
                p = Positions(m.group(1), start=m.group(2), end=m.group(3))
                new.position.append(p)
    
    db.session.add(new)
    db.session.commit()

def updateStaff(person, name=None,start=None, end=None, position=None, location=None, student=None, url=None):
    if name:
        person.name=name
    if start:
        person.start=start
    if end:
        person.end=end
    if position:
        m = re.match('(.*) \((\d\d\d\d)-(\d\d\d\d)\)', position)
        if m:
            p = Positions(m.group(1), start=m.group(2), end=m.group(3))
            person.position.append(p)
    if location:
        person.location=location
    if student:
        person.students.append(student)
    if url:
        person.url=url

    db.session.commit()
    
def updatePhD(person, name=None,start=None, end=None, thesis=None, location=None, supervisor=None, url=None):
    if name:
        person.name=name
    if start:
        person.start=start
    if end:
        person.end=end
    if thesis:
        person.thesis=thesis
    if location:
        person.location=location
    if supervisor:
        person.supervisor.append(supervisor)
    if url:
        person.url=url
    
    db.session.commit()

def updateAssociate(person, name=None, start=None, end=None, location=None, url=None, position=None):
    if name:
        person.name=name
    if start:
        person.start=start
    if end:
        person.end=end
    if location:
        person.location=location
    if url:
        person.url=url
    if position:
        m = re.match('(.*) \((\d\d\d\d)-(\d\d\d\d)\)', position)
        if m:
            p = Positions(m.group(1), start=m.group(2), end=m.group(3))
            person.position.append(p)
    
    db.session.commit()

def link(person1, person2):
    if person1.person:
        person2.person = person1.person
    elif person2.person:
        person1.person = person2.person
    #if neither has a unique person attached, create one
    else:
        new_person = People()
        
        #complete appropriate fields
        if type(person1) == Staff:
            new_person.staff = person1
        elif type(person1) == PhD:
            new_person.phd = person1
        else:
            new_person.associate = person1

        if type(person2) == Staff:
            new_person.staff = person2
        elif type(person2) == PhD:
            new_person.phd = person2
        else:
            new_person.associate = person2

        db.session.add(new_person)

    db.session.commit()

def search(q):
    #get all people that match query
    staff = Staff.query.search(q)
    students = PhD.query.search(q)
    assoc = Associates.query.search(q)
    rankings=[]
    #create list of tuples with result and relevance
    for person in staff.all() + students.all() + assoc.all():
        rank = db.engine.execute(db.func.ts_rank(person.search_vector, db.func.to_tsquery(q))).fetchone()[0]
        rankings.append((person, rank))

    #also search through positions, extracting the corresponding person
    for position in Positions.query.search(q):
        rank = db.engine.execute(db.func.ts_rank(position.search_vector, db.func.to_tsquery(q))).fetchone()[0]
        if position.staff:
            rankings.append((position.staff, rank))
        elif position.associate:
            rankings.append((position.associate, rank))
    
    #return list of people sorted by relevance
    return map(lambda t:t[0], sorted(rankings, key=lambda t:t[1], reverse=True))

