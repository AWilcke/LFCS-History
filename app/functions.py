from database import *

def addPerson(name, role, start=None, end=None, position=None, location=None, thesis=None, url=None):
    if role.lower() =="phd" or role.lower() == "pg":
        new = PhD(name=name, start=start, end=end, thesis=thesis, location=location, url=url)
    elif role.lower() == 'staff':
        new = Staff(name=name, start=start, end=end, position=position, location=location, url=url)
    else:
        new = Associates(name=name, start=start, end=end, location=location, url=url, role=position)
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
        previous = eval(person.position)
        previous.append(position)
        person.position=str(previous)
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
        person.supervisor.append(student)
    if url:
        person.url=url
    
    db.session.commit()

def updateAssociate(person, name=None, start=None, end=None, location=None, url=None, role=None):
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
    print role
    if role:
        previous = eval(person.role)
        previous.append(role)
        person.role=str(previous)

    db.session.commit()
#there must be a better way to do this, but for now this works

def link(person1, person2):
    if type(person1) == Staff:
        person2.staff = person1
    elif type(person1) == PhD:
        person2.phd = person1
    elif type(person1) == Associates:
        person2.associate = person1

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

    #return list of people sorted by relevance
    return map(lambda t:t[0], sorted(rankings, key=lambda t:t[1], reverse=True))

