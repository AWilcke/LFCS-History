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
    query_class = QueryClass
    __tablename__ = 'staff'
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String())
    start = db.Column(db.Integer)
    end = db.Column(db.Integer)
    url = db.Column(db.String())
    location = db.Column(db.String())
    
    students = db.relationship('PhD', back_populates='supervisor', secondary=supervising_table)
    position = db.relationship('Positions', back_populates='staff')
    
    person = db.relationship('People', back_populates='staff', uselist=False)

    search_vector = db.Column(TSVectorType(
        'name',
        'location',
        weights={'name':'A','location':'C'}))

    def __repr__(self):
        return self.name

    def __init__(self, name, start=None, end=None, location=None, url=None):
        self.name = name
        self.start = start
        self.end = end
        self.url=url
        self.location=location

class PhD(db.Model):
    query_class = QueryClass
    __tablename__ = 'phd'
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String())
    start = db.Column(db.Integer)
    end = db.Column(db.Integer)
    thesis = db.Column(db.String())
    location = db.Column(db.String())
    url = db.Column(db.String())
    

    supervisor = db.relationship('Staff', back_populates='students', secondary=supervising_table) 
    person = db.relationship('People', back_populates='phd', uselist=False)

    search_vector = db.Column(TSVectorType(
        'name',
        'thesis',
        'location',
        weights={'name':'A','thesis':'B','location':'C'}))

    def __repr__(self):
        return self.name

    def __init__(self, name, start=None, end=None, thesis=None, location=None, url=None):
        self.name=name
        self.start=start
        self.end=end
        self.thesis=thesis
        self.location=location
        self.url=url

#table for Associate and Honorary members, and visitors
class Associates(db.Model):
    query_class = QueryClass
    __tablename__='associates'
    id = db.Column(db.Integer, primary_key=True)
    
    name = db.Column(db.String())
    start=db.Column(db.Integer)
    end=db.Column(db.Integer)
    location=db.Column(db.String())
    url=db.Column(db.String())
    
    position=db.relationship('Positions', back_populates='associate')

    person=db.relationship('People',back_populates='associate',uselist=False)

    search_vector = db.Column(TSVectorType(
        'name',
        'location',
        weights={'name':'A','location':'C'}))

    def __repr__(self):
        return self.name

    def __init__(self, name, start=None, end=None, location=None, url=None):
        self.name=name
        self.start=start
        self.end=end
        self.location=location
        self.url=url

class Positions(db.Model):
    query_class = QueryClass
    __tablename__='positions'
    id=db.Column(db.Integer, primary_key=True)
   
    position = db.Column(db.String())
    start = db.Column(db.Integer)
    end = db.Column(db.Integer)

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
    __tablename__='people'
    id=db.Column(db.Integer, primary_key=True)
    
    staff_id=db.Column(db.Integer, db.ForeignKey('staff.id'))
    staff=db.relationship('Staff',back_populates='person')

    phd_id=db.Column(db.Integer, db.ForeignKey('phd.id'))
    phd=db.relationship('PhD',back_populates='person')

    associate_id=db.Column(db.Integer, db.ForeignKey('associates.id'))
    associate=db.relationship('Associates', back_populates='person')

    def __repr__(self):
        if self.staff:
            return self.staff.name
        elif self.phd:
            return self.phd.name
        elif self.associate:
            return self.associate.name
        else:
            return "No one"

#mappers for vectoring, for the search
db.configure_mappers()
db.create_all()
