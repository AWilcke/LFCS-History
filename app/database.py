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

    search_vector = db.Column(TSVectorType('name','position','location'))

    def __repr__(self):
        return 'Name %r' % (self.name)

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

    search_vector = db.Column(TSVectorType('name','thesis','location'))
    def __repr__(self):
        if self.supervisor:
            if len(self.supervisor) == 1:
                return 'Name %r, Supervisor %r' % (self.name, self.supervisor)
            else:
                return 'Name %r, Supervisors %r' % (self.name, self.supervisor)
        else:
            return 'Name %r, Supervisor unknown' % (self.name)

#mappers for vectoring, for the search
db.configure_mappers()
db.create_all()

def addPerson(name, role, start=None, end=None, position=None, location=None, thesis=None):
    new = None
    if role.lower() =="phd" or role.lower() == "pg":
        new = PhD(name=name, start=start, end=end, thesis=thesis, location=location)
    else:
        new = Staff(name=name, start=start, end=end, position=position, location=location)
    db.session.add(new)
    db.session.commit()
