from database import People, Staff, PhD, PostDoc, Associates, Positions, Dates, Users
from lfcsapp import db, bcrypt
from flask_login import current_user
import re

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
                    results[position.associate.person] = rank
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

def update_info(id, name, url, location, starts, ends):
    person = People.query.get(id)
    person.name = name
    person.url = url
    person.location = location
    person.dates = []    
    for (start, end) in zip(starts, ends):
        try:
            start = int(start)
        except:
            start=None
        try:
            end = int(end)
        except:
            end=None
        person.dates.append(Dates(start, end))

    db.session.add(person)

def add_person(name, url, location, starts, ends):
    person = People()
    person.name = name
    person.url = url
    person.location = location
    person.dates = []    
    for (start, end) in zip(starts, ends):
        try:
            start = int(start)
        except:
            start=None
        try:
            end = int(end)
        except:
            end=None
        person.dates.append(Dates(start, end))
    db.session.add(person)
    return person

def delete_person(id):
    db.session.delete(People.query.get(id))
    db.session.commit()

def update_staff(id, positions, pos_starts, pos_ends, starts, ends, students, primary, secondary):
    person = People.query.get(id).staff
    person.position = []
    for i in range(0, len(positions)):
        if positions[i]:
            newPos = Positions(positions[i])
            for (start, end) in zip(pos_starts[i], pos_ends[i]):
                try:
                    start = int(start)
                except:
                    start=None
                try:
                    end = int(end)
                except:
                    end=None
                newPos.dates.append(Dates(start, end))
            person.position.append(newPos)
    
    person.dates=[]
    for (start, end) in zip(starts, ends):
        try:
            start = int(start)
        except:
            start=None
        try:
            end = int(end)
        except:
            end=None
        person.dates.append(Dates(start, end))

    person.students=[]
    for id in students:
        if id:
            person.students.append(People.query.get(id).phd)

    person.postdocs = []
    for id in primary:
        if id:
            person.postdocs.append(People.query.get(id).postdoc)

    person.postdocs_secondary = []
    for id in secondary:
        if id:
            person.postdocs_secondary.append(People.query.get(id).postdoc)


def update_associate(id, positions, pos_starts, pos_ends, starts, ends):
    person = People.query.get(id).associate
    person.position = []
    for i in range(0, len(positions)):
        if positions[i]:
            newPos = Positions(positions[i])
            for (start, end) in zip(pos_starts[i], pos_ends[i]):
                try:
                    start = int(start)
                except:
                    start=None
                try:
                    end = int(end)
                except:
                    end=None
                newPos.dates.append(Dates(start, end))
            person.position.append(newPos)
    
    person.dates=[]
    for (start, end) in zip(starts, ends):
        try:
            start = int(start)
        except:
            start=None
        try:
            end = int(end)
        except:
            end=None
        person.dates.append(Dates(start, end))


def update_phd(id, thesis, starts, ends, supervisors):
    person = People.query.get(id).phd
    
    person.dates = []
    for (start, end) in zip(starts, ends):
        try:
            start = int(start)
        except:
            start=None
        try:
            end = int(end)
        except:
            end=None
        person.dates.append(Dates(start, end))
   
    person.supervisor = []
    for id in supervisors:
        if id:
            person.supervisor.append(People.query.get(id).staff)
    
    person.thesis = thesis

def update_postdoc(id, starts, ends, primary, secondary):
    person = People.query.get(id).postdoc
    
    person.dates = []
    for (start, end) in zip(starts, ends):
        try:
            start = int(start)
        except:
            start=None
        try:
            end = int(end)
        except:
            end=None
        person.dates.append(Dates(start, end))
    if primary:
        person.primary_investigator = People.query.get(primary).staff
    else:
        person.primary_investigator = None

    person.investigators = []
    for id in secondary:
        if id:
            person.investigators.append(People.query.get(id).staff)

def add_cat(id, cat):
    person = People.query.get(id)

    if cat=='staff' and not person.staff:
        person.staff = Staff()
    elif cat=='phd' and not person.phd:
        person.phd = PhD()
    elif cat=='postdoc' and not person.postdoc:
        person.postdoc = PostDoc()
    elif cat=='associate' and not person.associate:
        person.associate = Associates()

def rm_cat(id, cat):
    person = People.query.get(id)
    
    if cat=='rm-staff' and person.staff:
        person.staff = None
    elif cat=='rm-phd' and person.phd:
        person.phd = None
    elif cat=='rm-postdoc' and person.postdoc:
        person.postdoc = None
    elif cat=='rm-associate' and person.associate:
        person.associate = None

def update_user(first, last, email, password):
    current_user.first_name = first
    current_user.last_name = last
    current_user.email = email
    if password:
        current_user.password = bcrypt.generate_password_hash(password)

def add_user(first, last, email, password):
    new_user = Users(first_name=first, last_name=last, email=email)
    new_user.password = bcrypt.generate_password_hash(password)

    db.session.add(new_user)
