from flask_sqlalchemy import BaseQuery
from sqlalchemy_searchable import SearchQueryMixin
from sqlalchemy_utils.types import TSVectorType
from lfcsapp import db

#phd supervisor table
supervising_table = db.Table('supervising_table',
    db.Column('staff', db.Integer, db.ForeignKey('staff.id')),
    db.Column('phd', db.Integer, db.ForeignKey('phd.id')),
    extend_existing=True
)   

#postdoc investigator table
postdoc_table = db.Table('postdoc_table',
    db.Column('staff', db.Integer, db.ForeignKey('staff.id')),
    db.Column('postdocs', db.Integer, db.ForeignKey('postdocs.id')),
    extend_existing=True
)

grant_table = db.Table('grant_table',
    db.Column('staff', db.Integer, db.ForeignKey('staff.id')),
    db.Column('grants', db.Integer, db.ForeignKey('grants.id')),
    extend_existing=True
)

#class for easy searching
class QueryClass(BaseQuery, SearchQueryMixin):
    pass

class Staff(db.Model):
    __tablename__ = 'staff'
    id = db.Column(db.Integer, primary_key=True)

    position = db.relationship('Positions', back_populates='staff', cascade='all, delete-orphan')
    dates = db.relationship('Dates', back_populates='staff', cascade='all, delete-orphan')
    grants = db.relationship('Grants', back_populates='staff', cascade='all, delete-orphan')
    grants_secondary = db.relationship('Grants', back_populates='secondary', secondary='grant_table')

    students = db.relationship('PhD', back_populates='supervisor', secondary=supervising_table)
    postdocs = db.relationship('PostDoc', back_populates='primary_investigator')
    postdocs_secondary = db.relationship('PostDoc', back_populates='investigators', secondary=postdoc_table)

    person_id = db.Column(db.Integer, db.ForeignKey('people.id'))
    person = db.relationship('People', back_populates='staff')
    
    def __repr__(self):
        return self.person.name

class PhD(db.Model):
    query_class = QueryClass
    __tablename__ = 'phd'
    id = db.Column(db.Integer, primary_key=True)

    thesis = db.Column(db.String())
    dates = db.relationship('Dates', back_populates='phd', cascade='all, delete-orphan')

    supervisor = db.relationship('Staff', back_populates='students', secondary=supervising_table) 
    
    person_id = db.Column(db.Integer, db.ForeignKey('people.id'))
    person = db.relationship('People', back_populates='phd')

    search_vector = db.Column(TSVectorType(
        'thesis',
        weights={'thesis':'B'}))

    def __repr__(self):
        return self.person.name

    def __init__(self, thesis=None):
        self.thesis=thesis

#table for Associate and Honorary members, and visitors
class Associates(db.Model):
    __tablename__='associates'
    id = db.Column(db.Integer, primary_key=True)
    
    position=db.relationship('Positions', back_populates='associate', cascade='all, delete-orphan')
    dates = db.relationship('Dates', back_populates='associate', cascade='all, delete-orphan')

    person_id = db.Column(db.Integer, db.ForeignKey('people.id'))
    person=db.relationship('People',back_populates='associate')

    def __repr__(self):
        return self.person.name

class PostDoc(db.Model):
    __tablename__='postdocs'
    id = db.Column(db.Integer, primary_key=True)

    dates = db.relationship('Dates', back_populates='postdoc', cascade='all, delete-orphan')

    primary_investigator_id=db.Column(db.Integer, db.ForeignKey('staff.id'))
    primary_investigator=db.relationship('Staff', back_populates='postdocs')

    investigators=db.relationship('Staff', back_populates='postdocs_secondary', secondary=postdoc_table)

    person_id = db.Column(db.Integer, db.ForeignKey('people.id'))
    person=db.relationship('People', back_populates='postdoc')
    
    def __repr__(self):
        return self.person.name

#table to define positions for staff and assoc
class Positions(db.Model):
    query_class = QueryClass
    __tablename__='positions'
    id=db.Column(db.Integer, primary_key=True)
   
    position = db.Column(db.String())
    dates = db.relationship('Dates', back_populates='position', cascade='all, delete-orphan')

    #link to the person
    staff_id=db.Column(db.Integer, db.ForeignKey('staff.id'))
    staff=db.relationship('Staff', back_populates='position')

    associate_id=db.Column(db.Integer, db.ForeignKey('associates.id'))
    associate=db.relationship('Associates', back_populates='position')

    search_vector = db.Column(TSVectorType(
        'position',
        weights={'position':'B'}))

    def __init__(self, position):
        self.position=position
    
    def __repr__(self):

        dates=[]
        for pair in self.dates:
            dates.append('(' + str(pair.start) + '-' + str(pair.end) + ')')
        return self.position + ' ' + ' and '.join(dates)

#grants for staff
class Grants(db.Model):
    __tablename__ = 'grants'
    id = db.Column(db.Integer, primary_key=True)
    ref = db.Column(db.String())
    title = db.Column(db.String())
    dates = db.relationship('Dates', back_populates='grant', cascade='all, delete-orphan', uselist=False)
    value = db.Column(db.Integer)
    url = db.Column(db.String())

    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'))
    staff = db.relationship('Staff', back_populates='grants')

    secondary = db.relationship('Staff', back_populates='grants_secondary', secondary='grant_table')

    def __repr__(self):
        return self.title + ' for ' + self.staff.person.name
    
    def __init__(self, title=None, value=None, url=None, ref=None):
        self.title = title
        self.value = value
        self.url = url
        self.ref = ref

#table for pairs of start-end dates
class Dates(db.Model):
    __tablename__='dates'
    id=db.Column(db.Integer, primary_key=True)

    start=db.Column(db.Integer)
    end=db.Column(db.Integer)
    
    #person link
    person_id=db.Column(db.Integer, db.ForeignKey('people.id'))
    person=db.relationship('People', back_populates='dates')

    staff_id=db.Column(db.Integer, db.ForeignKey('staff.id'))
    staff=db.relationship('Staff',back_populates='dates')

    phd_id=db.Column(db.Integer, db.ForeignKey('phd.id'))
    phd=db.relationship('PhD',back_populates='dates')

    associate_id=db.Column(db.Integer, db.ForeignKey('associates.id'))
    associate=db.relationship('Associates', back_populates='dates')

    postdoc_id=db.Column(db.Integer, db.ForeignKey('postdocs.id'))
    postdoc=db.relationship('PostDoc', back_populates='dates')
    
    position_id=db.Column(db.Integer, db.ForeignKey('positions.id'))
    position = db.relationship('Positions', back_populates='dates')

    grant_id = db.Column(db.Integer, db.ForeignKey('grants.id'))
    grant = db.relationship('Grants', back_populates='dates')

    def __init__(self, start, end):
        self.start=start
        self.end=end

    def __repr__(self):
        return str(self.start) + '-' + str(self.end)

#table of unique people
class People(db.Model):
    query_class=QueryClass
    __tablename__='people'
    id=db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String())
    url = db.Column(db.String())
    location = db.Column(db.String())
    dates = db.relationship('Dates', back_populates='person', cascade='all, delete-orphan')
    
    staff=db.relationship('Staff', back_populates='person', uselist=False, cascade='all, delete-orphan')

    phd=db.relationship('PhD',back_populates='person', uselist=False, cascade='all, delete-orphan')

    associate=db.relationship('Associates', back_populates='person', uselist=False, cascade='all, delete-orphan')

    postdoc=db.relationship('PostDoc', back_populates='person', uselist=False, cascade='all, delete-orphan')

    search_vector=db.Column(TSVectorType(
        'name',
        'location',
        weights={'name':'A','location':'C'}))

    def __repr__(self):
        return self.name

    def __init__(self, name=None, url=None, location=None):
        self.name = name
        self.url = url
        self.location = location

#users of the app
class Users(db.Model):

    __tablename__='users'
    email=db.Column(db.String(), primary_key=True)
    password = db.Column(db.String())
    first_name = db.Column(db.String())
    last_name = db.Column(db.String())

    authenticated = db.Column(db.Boolean(), default=False)
    
    def is_active(self):
        return True

    def get_id(self):
        return self.email

    def is_authenticated(self):
        return self.authenticated
    
    def is_anonymous(self):
        return False

    def __repr__(self):
        return self.email
