from database import *

def addPerson(name, role, start=None, end=None, position=None, location=None, thesis=None):
    new = None
    if role.lower() =="phd" or role.lower() == "pg":
        new = PhD(name=name, start=start, end=end, thesis=thesis, location=location)
    else:
        new = Staff(name=name, start=start, end=end, position=position, location=location)
    db.session.add(new)
    db.session.commit()

def search(q):
    staff = Staff.query.search(q, sort=True)
    students = PhD.query.search(q, sort=True)
    
    return staff.all() + students.all()

