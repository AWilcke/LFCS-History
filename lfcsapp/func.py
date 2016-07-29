from database import People, Staff, PhD, PostDoc, Associates, Positions, Dates, Users, Grants, Suggestions
from lfcsapp import db, bcrypt
from flask_login import current_user
from datetime import datetime
from sqlalchemy_searchable import parse_search_query
from sqlalchemy import and_, or_
import re

#search on basic keywords
def base_search(query):
    filter_list = []
    remove_list = []

    if '-phd' in query.lower():
        remove_list.append(People.phd==None)
        query = query.replace('-phd','')
    elif 'phd' in query.lower():
        filter_list.append(People.phd)
        query = query.replace('phd','')
    if '-staff' in query.lower():
        remove_list.append(People.staff==None)
        query = query.replace('-staff','')
    elif 'staff' in query.lower():
        filter_list.append(People.staff)
        query = query.replace('staff','')
    if '-postdoc' in query.lower():
        remove_list.append(People.postdoc==None)
        query = query.replace('-postdoc','')
    elif 'postdoc' in query.lower():
        filter_list.append(People.postdoc)
        query = query.replace('postdoc','')
    if '-associate' in query.lower():
        remove_list.append(People.associate==None)
        query = query.replace('-associate','')
    elif 'associate' in query.lower():
        filter_list.append(People.associate)
        query = query.replace('associate','')

    #for a simple "query all" function
    if '*' in query:
        all = People.query.filter(and_(*remove_list)).filter(or_(*filter_list))
        return all.all()

    phd_vec = People.search_vector | PhD.search_vector
    phd = db.session.query(People).join(PhD).filter(phd_vec.match(parse_search_query(query)))

    pos_vec = People.search_vector | Positions.search_vector
    staff = db.session.query(People).join(Staff).join(Positions).filter(pos_vec.match(parse_search_query(query)))
    associates = db.session.query(People).join(Associates).join(Positions).filter(pos_vec.match(parse_search_query(query)))
    
    staff_nopos = People.query.join(Staff).filter(~(Staff.position.any())).search(query)
    assoc_nopos = People.query.join(Associates).filter(~(Associates.position.any())).search(query)

    others = People.query.filter(People.staff==None, People.associate==None, People.phd==None).search(query)

    union = phd.union(staff, staff_nopos, associates, assoc_nopos, others)
    union = union.filter(and_(*remove_list)).filter(or_(*filter_list))
    return union.all()

#primitive version of the search
def old_search(query):
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

#search on specific parameters
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

#updates information of person
def update_info(person, name, url, location, nationality, starts, ends):
    person.name = name
    person.url = url
    person.location = location
    person.nationality = nationality
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

#adds person to database with information
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

#updates information given from form for staff
def update_staff(id, positions, pos_starts, pos_ends, research_explorer, grant_titles, grant_values, grant_urls, grant_refs, grant_orgs, grant_starts, grant_ends, grant_secondary, starts, ends, students, postdoc):
    person = id.staff
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

    person.research_explorer = research_explorer
    person.grants = []
    for i in range(0, len(grant_titles)):
        if grant_titles[i]:
            try:
                grant_values[i] = int(grant_values[i])
            except:
                grant_values[i] = None
            newGrant = Grants(grant_titles[i], grant_values[i], grant_urls[i], grant_refs[i], grant_orgs[i])
            try:
                start = int(grant_starts[i])
            except:
                start=None
            try:
                end = int(grant_ends[i])
            except:
                end=None
            newGrant.dates = Dates(start, end)
            
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
    for id in postdoc:
        if id:
            person.postdocs.append(People.query.get(id).postdoc)

#updates information given from form for associates
def update_associate(id, positions, pos_starts, pos_ends, starts, ends):
    person = (id).associate
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

#updates information given from form for phd
def update_phd(id, thesis, starts, ends, supervisors):
    person = (id).phd
    
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

#updates information given from form for postdoc
def update_postdoc(id, starts, ends, investigators):
    person = (id).postdoc
    
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

    person.investigators = []
    for id in investigators:
        if id:
            person.investigators.append(People.query.get(id).staff)

#adds category to person
def add_cat(person, cat):
    if cat=='staff' and not person.staff:
        person.staff = Staff()
    elif cat=='phd' and not person.phd:
        person.phd = PhD()
    elif cat=='postdoc' and not person.postdoc:
        person.postdoc = PostDoc()
    elif cat=='associate' and not person.associate:
        person.associate = Associates()

#removes category from person
def rm_cat(person, cat):
    if cat=='rm-staff' and person.staff:
        person.staff = None
    elif cat=='rm-phd' and person.phd:
        person.phd = None
    elif cat=='rm-postdoc' and person.postdoc:
        person.postdoc = None
    elif cat=='rm-associate' and person.associate:
        person.associate = None

#updates information from form for user
def update_user(first, last, email, password):
    current_user.first_name = first
    current_user.last_name = last
    current_user.email = email
    if password:
        current_user.password = bcrypt.generate_password_hash(password)

#adds user with information
def add_user(first, last, email, password):
    new_user = Users(first_name=first, last_name=last, email=email)
    new_user.password = bcrypt.generate_password_hash(password)

    db.session.add(new_user)

#return a dictionary representation of a person
def person_to_dict(person, id=None):
    dic = {'staff':{}, 'phd':{}, 'postdoc':{}, 'associate':{}}
    dic['name'] = person.name
    dic['url'] = person.url
    dic['location'] = person.location
    dic['nationality'] = person.nationality
    dic['dates'] = [(date.start, date.end) for date in person.dates]
    #this is to pass the id down to the final suggestion
    if id:
        dic['id'] = id
    else:
        dic['id'] = person.id
    if person.staff:
        staff = dic['staff']
        staff['position'] = [(position.position, [(date.start, date.end) for date in position.dates]) for position in person.staff.position]
        staff['dates'] = [(date.start, date.end) for date in person.staff.dates]
        staff['research_explorer'] = person.staff.research_explorer
        staff['students'] = [student.person.id for student in person.staff.students]
        staff['postdocs'] = [postdoc.person.id for postdoc in person.staff.postdocs]
        staff['grants'] = []
        for grant in person.staff.grants:
            g = {}
            g['ref'] = grant.ref
            g['title'] = grant.title
            g['dates'] = (grant.dates.start, grant.dates.end)
            g['value'] = grant.value
            g['url'] = grant.url
            g['org'] = grant.org
            staff['grants'].append(g)
        staff['grants_secondary'] = []
        for grant in person.staff.grants_secondary:
            g = {}
            g['ref'] = grant.ref
            g['title'] = grant.title
            g['dates'] = (grant.dates.start, grant.dates.end)
            g['value'] = grant.value
            g['url'] = grant.url
            g['org'] = grant.org
            staff['grants_secondary'].append(g)

    if person.phd:
        phd = dic['phd']
        phd['thesis'] = person.phd.thesis
        phd['dates'] = [(date.start, date.end) for date in person.phd.dates]
        phd['supervisor'] = [sup.person.id for sup in person.phd.supervisor]

    if person.postdoc:
        postdoc = dic['postdoc']
        postdoc['dates'] = [(date.start, date.end) for date in person.postdoc.dates]
        postdoc['investigators'] = [inv.person.id for inv in person.postdoc.investigators]

    if person.associate:
        associate = dic['associate']
        associate['position'] = [(position.position, [(date.start, date.end) for date in position.dates]) for position in person.associate.position]
        associate['dates'] = [(date.start, date.end) for date in person.associate.dates]

    return dic

#return a person object generated from a dictionary
def dic_to_person(dic):
    staff, phd, pg, assoc = None, None, None, None
   
    person = People()
    person.name = dic['name']
    person.url = dic['url']
    person.location = dic['location']
    person.nationality = dic['nationality']
    for date in dic['dates']:
        person.dates.append(Dates(date[0], date[1]))
    
    if dic['staff']:
        staff_d = dic['staff']
        staff = Staff()
        for (position, dates) in staff_d['position']:
            pos = Positions(position)
            [pos.dates.append(Dates(start, end)) for (start, end) in dates]
            staff.position.append(pos)
        for (start, end) in staff_d['dates']:
            staff.dates.append(Dates(start, end))
        staff.research_explorer = staff_d['research_explorer']
        for id in staff_d['students']:
            staff.students.append(People.query.get(id).phd)
        for id in staff_d['postdocs']:
            staff.postdocs.append(People.query.get(id).postdoc)

        for grant in staff_d['grants']:
            g = Grants(grant['title'],grant['value'],grant['url'],grant['ref'], grant['org'])
            g.dates = Dates(grant['dates'][0], grant['dates'][1])
            staff.grants.append(g)
        for grant in staff_d['grants_secondary']:
            g = Grants(grant['title'],grant['value'],grant['url'],grant['ref'], grant['org'])
            g.dates = Dates(grant['dates'][0], grant['dates'][1])
            staff.grants_secondary.append(g)
        
    if dic['phd']:
        phd_d = dic['phd']
        phd = PhD()
        phd.thesis = phd_d['thesis']
        for (start, end) in phd_d['dates']:
            phd.dates.append(Dates(start, end))
        for id in phd_d['supervisor']:
            phd.supervisor.append(People.query.get(id).staff)

    if dic['postdoc']:
        pg_d = dic['postdoc']
        pg = PostDoc()
        for (start, end) in pg_d['dates']:
            pg.dates.append(Dates(start, end))
        for id in pg_d['investigators']:
            pg.investigators.append(People.query.get(id).staff)
    if dic['associate']:
        a_d = dic['associate']
        assoc = Associates()
        for (position, dates) in a_d['position']:
            pos = Positions(position)
            [pos.dates.append(Dates(start, end)) for (start, end) in dates]
            assoc.position.append(pos)
        for (start, end) in a_d['dates']:
            assoc.dates.append(Dates(start, end))


    person.staff = staff
    person.phd = phd
    person.postdoc = pg
    person.associate = assoc

    return person

#delete all non-final suggestions
def clear_suggestions():
    Suggestions.query.filter(Suggestions.final==False).delete()
    db.session.commit()

#update dates of all people at lfcs
#I'm sure this can be done with a query, but cannot figure it out
def new_year():
    ny = datetime.now().year
    year = ny-1
    dates = Dates.query.filter(Dates.end==year).all()
    current = People.query.filter(People.location=='LFCS').all()
    for person in current:
        for date in person.dates:
            if date in dates:
                date.end = ny
        if person.staff:
            for date in person.staff.dates:
                if date in dates:
                    date.end = ny
            if person.staff.position:
                for position in person.staff.position:
                    for date in position.dates:
                        if date in dates:
                            date.end = ny
        if person.phd:
            for date in person.phd.dates:
                if date in dates:
                    date.end = ny
        if person.postdoc:
            for date in person.postdoc.dates:
                if date in dates:
                    date.end = ny
        if person.associate:
            for date in person.associate.dates:
                if date in dates:
                    date.end = ny
            if person.associate.position:
                for position in person.associate.position:
                    for date in position.dates:
                        if date in dates:
                            date.end = ny
    db.session.commit()

