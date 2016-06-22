from database import *

def addPerson(name, role, start=None, end=None, position=None, location=None, thesis=None):
    new = None
    if role.lower() =="phd" or role.lower() == "pg":
        new = PhD(name=name, start=start, end=end, thesis=thesis, location=location)
    else:
        new = Staff(name=name, start=start, end=end, position=position, location=location)
    db.session.add(new)
    db.session.commit()

def updateStaff(person, start=None, end=None, position=None, location=None, student=None):
    person.start=start
    person.end=end
    person.position+=position.split(',')
    person.location=location
    person.students.append(student)

def updatePhD(person, start=None, end=None, thesis=None, location=None, supervisor=None):
    person.start=start
    person.end=end
    person.thesis=thesis
    person.location=location
    person.supervisor.append(supervisor)

#there must be a better way to do this, but for now this works
def search(q):
    #get all staff and students that match query
    staff = Staff.query.search(q)
    students = PhD.query.search(q)

    rankings=[]
    #create list of tuples with result and relevance
    for person in staff.all() + students.all():
        rank = db.engine.execute(db.func.ts_rank(person.search_vector, db.func.to_tsquery(q))).fetchone()[0]
        rankings.append((person, rank))

    #return list of people sorted by relevance
    return map(lambda t:t[0], sorted(rankings, key=lambda t:t[1], reverse=True))

