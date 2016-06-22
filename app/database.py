from app import *
from sqlalchemy_searchable import make_searchable, SearchQueryMixin
from sqlalchemy_utils.types import TSVectorType

#config for search
make_searchable()

#phd supervisor table
supervising_table = db.Table('relationship_table',
    db.Column('staff', db.Integer, db.ForeignKey('staff.id')),
    db.Column('phd', db.Integer, db.ForeignKey('phd.id')),
)

#class for easy searching for staff
class StaffQuery(BaseQuery, SearchQueryMixin):
    pass

class Staff(db.Model):
    query_class = StaffQuery
    __tablename__ = 'staff'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    start = db.Column(db.Integer)
    end = db.Column(db.Integer)
    position = db.Column(db.String())
    students = db.relationship('PhD', back_populates='supervisor', secondary=supervising_table)
    location = db.Column(db.String())
    
    search_vector = db.Column(TSVectorType(
        'name',
        'position',
        'location',
        weights={'name':'A','position':'B','location':'C'}))

    def __repr__(self):
        return self.name

    def __init__(self, name, start=None, end=None, position=None, location=None, students=None):
            self.name = name
            self.start = start
            self.end = end
            if type(position) == 'list':
                self.position=position
            elif type(position) == 'str':
                self.position=position.split(',')
            else:
                self.position=[]
            self.location=location
            if type(students) == 'list':
                self.students=students
            elif type(students) == 'str':
                self.students=students.split(',')
            else:
                self.students=[]

#class for easy searchign for students
class PhDQuery(BaseQuery, SearchQueryMixin):
    pass

class PhD(db.Model):
    query_class = PhDQuery
    __tablename__ = 'phd'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    start = db.Column(db.Integer)
    end = db.Column(db.Integer)
    supervisor = db.relationship('Staff', back_populates='students', secondary=supervising_table)
    thesis = db.Column(db.String())
    location = db.Column(db.String())
    
    search_vector = db.Column(TSVectorType(
        'name',
        'thesis',
        'location',
        weights={'name':'A','thesis':'B','location':'C'}))

    def __repr__(self):
        return self.name

    def __init__(self, name, start=None, end=None, thesis=None, location=None, supervisor=None):
        self.name=name
        self.start=start
        self.end=end
        self.thesis=thesis
        self.location=location
        if type(supervisor) == 'list':
            self.supervisor = supervisor
        elif type(supervisor) == 'str':
            self.supervisor = supervisor.split(',')
        else:
            self.supervisor = []

#mappers for vectoring, for the search
db.configure_mappers()
db.create_all()
