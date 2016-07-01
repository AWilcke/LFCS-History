from app import *
from sqlalchemy_searchable import make_searchable, SearchQueryMixin
from sqlalchemy_utils.types import TSVectorType

#config for search
make_searchable()

#phd supervisor table
supervising_table = db.Table('relationship_table',
    db.Column('staff', db.Integer, db.ForeignKey('staff.id')),
    db.Column('phd', db.Integer, db.ForeignKey('phd.id')),
    extend_existing=True
)   

#class for easy searching
class QueryClass(BaseQuery, SearchQueryMixin):
    pass

class Staff(db.Model):
    __tablename__ = 'staff'
    id = db.Column(db.Integer, primary_key=True)

    students = db.relationship('PhD', back_populates='supervisor', secondary=supervising_table)
    
    position = db.relationship('Positions', back_populates='staff')
    
    person = db.relationship('People', back_populates='staff', uselist=False)

    def __repr__(self):
        return self.person.name

class PhD(db.Model):
    query_class = QueryClass
    __tablename__ = 'phd'
    id = db.Column(db.Integer, primary_key=True)

    thesis = db.Column(db.String())

    supervisor = db.relationship('Staff', back_populates='students', secondary=supervising_table) 
    person = db.relationship('People', back_populates='phd', uselist=False)

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
    
    position=db.relationship('Positions', back_populates='associate')

    person=db.relationship('People',back_populates='associate',uselist=False)

    def __repr__(self):
        return self.person.name

class Positions(db.Model):
    query_class = QueryClass
    __tablename__='positions'
    id=db.Column(db.Integer, primary_key=True)
   
    position = db.Column(db.String())
    start = db.Column(db.Integer)
    end = db.Column(db.Integer)

    #link to the person
    staff_id=db.Column(db.Integer, db.ForeignKey('staff.id'))
    staff=db.relationship('Staff', back_populates='position')

    associate_id=db.Column(db.Integer, db.ForeignKey('associates.id'))
    associate=db.relationship('Associates', back_populates='position')

    search_vector = db.Column(TSVectorType(
        'position',
        weights={'position':'B'}))

    def __init__(self, position, start=None, end=None):
        self.position=position
        self.start=start
        self.end=end
    
    def __repr__(self):
        return self.position + '(' + str(self.start) + '-' + str(self.end) + ')'

#table of unique people
class People(db.Model):
    query_class=QueryClass
    __tablename__='people'
    id=db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String())
    url = db.Column(db.String())
    location = db.Column(db.String())
    start = db.Column(db.Integer)
    end = db.Column(db.Integer)
    #number of positions (1-3)
    size=db.Column(db.Integer)

    staff_id=db.Column(db.Integer, db.ForeignKey('staff.id'))
    staff=db.relationship('Staff',back_populates='person')

    phd_id=db.Column(db.Integer, db.ForeignKey('phd.id'))
    phd=db.relationship('PhD',back_populates='person')

    associate_id=db.Column(db.Integer, db.ForeignKey('associates.id'))
    associate=db.relationship('Associates', back_populates='person')

    search_vector=db.Column(TSVectorType(
        'name',
        'location',
        weights={'name':'A','location':'C'}))

    def __repr__(self):
        return self.name

    def __init__(self, name, url=None, location=None):
        self.size = 0
        self.name = name
        self.url = url
        self.location = location

#mappers for vectoring, for the search
db.configure_mappers()
db.create_all()
