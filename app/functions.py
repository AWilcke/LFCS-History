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

    #create new unique person
    new.person = People()
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
    if person2.person.size==1:
        person2.person = person1.person
        person1.person.size += 1
    elif person1.person.size==1:
        person1.person = person2.person
        person1.person.size+=1
    else:
        raise "Trying to link two elements of size " + str(person1.person.size) + " and " + str(person2.person.size)
    People.query.filter((People.staff==None) & (People.phd==None) & (People.associate==None)).delete()
    db.session.commit()

def search(q):
    #get all people that match query
    staff = Staff.query.search(q)
    students = PhD.query.search(q)
    assoc = Associates.query.search(q)
    rankings={}
    unique=[]
    #create list of tuples with result and relevance
    for person in staff.all() + students.all() + assoc.all():
        rank = db.engine.execute(db.func.ts_rank(person.search_vector, db.func.plainto_tsquery(q))).fetchone()[0]
        if person.person not in unique:
            unique.append(person.person)
            rankings[person.person] = rank
        elif rankings[person.person]<rank:
            rankings[person.person]=rank


    #also search through positions, extracting the corresponding person
    for position in Positions.query.search(q).all():
        rank = db.engine.execute(db.func.ts_rank(position.search_vector, db.func.plainto_tsquery(q))).fetchone()[0]
        if position.staff:
            if position.staff.person not in unique:
                unique.append(position.staff.person)
                rankings[position.staff.person] = rank
            elif rankings[position.staff.person]<rank:
                rankings[position.staff.person] = rank
        if position.associate:
            if position.associate.person not in unique:
                unique.append(position.associate.person)
                rankings[position.associate.person] = rank
            elif rankings[position.associate.person]<rank:
                rankings[position.associate.person] = rank
    
    #return list of people sorted by relevance
    return sorted(rankings, key=rankings.get, reverse=True)
