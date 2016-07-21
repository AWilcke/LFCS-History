from database import People, Staff, PhD, PostDoc, Associates, Positions, Dates, Users, Grants
from lfcsapp import db, bcrypt
from flask_login import current_user
import re

def base_search(query):
    people = People.query.search(query).all()
    positions = Positions.query.search(query).all()
    phd = PhD.query.search(query).all()

    for position in positions:
        if position.staff:
            people.append(position.staff.person)
        elif position.associate:
            people.append(position.associate.person)

    for student in phd:
        people.append(student.person)

    return set(people)

def advanced_search(name, location, start, end, cat):
    results = People.query
    dates = Dates.query.filter(Dates.person)

    if name:
        results = results.filter_by(name=name)
    if location:
        results = results.filter_by(location=location)
    if cat=='staff':
        results = results.filter(People.staff)
    if cat=='phd':
        results = results.filter(People.phd)
    if cat=='postdoc':
        results = results.filter(People.postdoc)
    if cat=='associate':
        results = results.filter(People.associate)
    if start:
        dates = dates.filter(Dates.start==start)
    if end:
        dates = dates.filter(Dates.end==end)

    dates = [date.person for date in dates]
    return set.intersection(set(results), set(dates))

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

def update_staff(id, positions, pos_starts, pos_ends, grant_titles, grant_values, grant_urls, grant_starts, grant_ends, grant_secondary, starts, ends, students, primary, secondary):
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

    person.grants = []
    for i in range(0, len(grant_titles)):
        if grant_titles[i]:
            try:
                grant_values[i] = int(grant_values[i])
            except:
                grant_values[i] = None
            newGrant = Grants(grant_titles[i], grant_values[i], grant_urls[i])
            try:
                start = int(grant_starts[i])
            except:
                start=None
            try:
                end = int(grant_ends[i])
            except:
                end=None
            newGrant.dates.append(Dates(start, end))
            
            print grant_secondary
            for staff in grant_secondary[i]:
                if staff:
                    newGrant.secondary.append(People.query.get(staff).staff)
            person.grants.append(newGrant)

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
