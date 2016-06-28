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
    position = db.relationship('Positions', back_populates='staff')
    students = db.relationship('PhD', back_populates='supervisor', secondary=supervising_table)
    location = db.Column(db.String())
    url = db.Column(db.String())
    
    phd_id = db.Column(db.Integer, db.ForeignKey('phd.id'))
    phd = db.relationship('PhD', back_populates='staff')
    
    associate = db.relationship('Associates',back_populates='staff',uselist=False)

    search_vector = db.Column(TSVectorType(
        'name',
        'location',
        weights={'name':'A','position':'B','location':'C'}))

    def __repr__(self):
        return self.name

    def __init__(self, name, start=None, end=None, location=None, students=[], url=None):
        self.name = name
        self.start = start
        self.end = end
        self.url=url
        self.location=location
        self.students=students

class PhD(db.Model):
    query_class = QueryClass
    __tablename__ = 'phd'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    start = db.Column(db.Integer)
    end = db.Column(db.Integer)
    supervisor = db.relationship('Staff', back_populates='students', secondary=supervising_table)
    thesis = db.Column(db.String())
    location = db.Column(db.String())
    url = db.Column(db.String())
    
    associate_id = db.Column(db.Integer, db.ForeignKey('associates.id'))
    associate = db.relationship('Associates',back_populates='phd')

    staff = db.relationship('Staff',back_populates='phd',uselist=False)

    search_vector = db.Column(TSVectorType(
        'name',
        'thesis',
        'location',
        weights={'name':'A','thesis':'B','location':'C'}))

    def __repr__(self):
        return self.name

    def __init__(self, name, start=None, end=None, thesis=None, location=None, supervisor=[], url=None):
        self.name=name
        self.start=start
        self.end=end
        self.thesis=thesis
        self.location=location
        self.url=url
        self.supervisor=supervisor

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
    role=db.Column(db.String())

    staff_id=db.Column(db.Integer, db.ForeignKey('staff.id'))
    staff=db.relationship('Staff', back_populates='associate')
    
    phd=db.relationship('PhD',back_populates='associate',uselist=False)

    search_vector = db.Column(TSVectorType(
        'name',
        'role',
        'location',
        weights={'name':'A','role':'B','location':'C'}))

    def __repr__(self):
        return self.name

    def __init__(self, name, start=None, end=None, location=None, url=None, role=None):
        self.name=name
        self.start=start
        self.end=end
        self.location=location
        self.url=url
        if role:
            self.role=str(role.split(' & '))
        else:
            self.role='[]'

class Positions(db.Model):
    __tablename__='positions'
    id=db.Column(db.Integer, primary_key=True)
    position = db.Column(db.String())
    start = db.Column(db.Integer)
    end = db.Column(db.Integer)
    staff_id=db.Column(db.Integer, db.ForeignKey('staff.id'))
    staff=db.relationship('Staff', back_populates='position')

    def __init__(self, position, start=None, end=None, staff=None):
        self.position=position
        self.staff=staff
        self.start=start
        self.end=end
    
    def __repr__(self):
        return self.position

#mappers for vectoring, for the search
db.configure_mappers()
db.create_all()
