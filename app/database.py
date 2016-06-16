from app import *

supervising_table = db.Table('relationship_table',
    db.Column('staff', db.Integer, db.ForeignKey('staff.id')),
    db.Column('phd', db.Integer, db.ForeignKey('phd.id'))
)

class Staff(db.Model):
    __tablename__ = 'staff'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    start = db.Column(db.Integer)
    end = db.Column(db.Integer)
    position = db.Column(db.String())
    students = db.relationship('PhD', back_populates='supervisor', secondary=supervising_table)
    location = db.Column(db.String())

    def __repr__(self):
        return 'Name %r' % (self.name)


class PhD(db.Model):
    __tablename__ = 'phd'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    start = db.Column(db.Integer)
    end = db.Column(db.Integer)
    supervisor = db.relationship('Staff', back_populates='students', secondary=supervising_table)
    thesis = db.Column(db.String())
    location = db.Column(db.String())

    def __repr__(self):
        if self.supervisor:
            if len(self.supervisor) == 1:
                return 'Name %r, Supervisor %r' % (self.name, self.supervisor)
            else:
                return 'Name %r, Supervisors %r' % (self.name, self.supervisor)
        else:
            return 'Name %r, Supervisor unknown' % (self.name)



def addPerson(name, role, start=None, end=None, position=None, location=None, thesis=None):
    new = None
    if role.lower() =="staff":
        new = Staff(name=name, start=start, end=end, position=position, location=location)
    else:
        new = PhD(name=name, start=start, end=end, thesis=thesis, location=location)
    db.session.add(new)
    db.session.commit()
