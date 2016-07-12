from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy, BaseQuery
import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///lfcs-test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

@app.route('/')
def index():
    return render_template('search.html')

# Save e-mail to database and send to success page
@app.route('/search', methods=['POST'])
def search():
    search=None
    if request.method == 'POST':
        search = request.form['search']
        return redirect(url_for('results', query=search))

@app.route('/results/<query>')
def results(query):
    results=func.base_search(query)
    return render_template('results.html', results=results, query=query)


@app.route('/person/<id>')
def person(id):
    person=func.People.query.get(id)
    if person:
        return render_template('people/person_detail.html', person=person)
    else:
        #should add error page
        return redirect(url_for('index'))

@app.route('/update/<id>', methods=['GET'])
def update(id):
    person = func.People.query.get(id)
    students = [student.person for student in func.PhD.query.all()]
    staff = [staff.person for staff in func.Staff.query.all()]
    postdocs = [postdoc.person for postdoc in func.PostDoc.query.all()]
    if person:
        return render_template('forms/person_form.html', person=person, students=students, staff=staff, postdocs=postdocs)
    else:
        #should add error page
        return redirect(url_for('index'))

@app.route('/updatesend/<num>', methods=['POST','GET'])
def updatesend(num):
    if request.method == 'POST':
        #basic info
        name = request.form['name']
        url = request.form['url']
        location = request.form['location']
        starts = request.form.getlist('info_start')
        ends = request.form.getlist('info_end')
        func.update_info(num, name, url, location, starts, ends)

        #staff
        starts = request.form.getlist('staff_start')
        if starts:
            ends = request.form.getlist('staff_end')
            position_names = request.form.getlist('staff_position')
            pos_starts = []
            pos_ends = []
            for i in range(0, len(position_names)):
                pos_starts.append(request.form.getlist('staff_' + str(i) + '_start'))
                pos_ends.append(request.form.getlist('staff_' + str(i) + '_end'))
            students = request.form.getlist('staff_phd_link')
            primary = request.form.getlist('staff_primary_link')
            secondary = request.form.getlist('staff_secondary_link')
            func.update_staff(num, position_names, pos_starts, pos_ends, starts, ends, students, primary, secondary)

        #phd
        starts = request.form.getlist('phd_start')
        if starts:
            ends = request.form.getlist('phd_end')
            thesis = request.form['thesis']
            supervisors = request.form.getlist('phd_staff_link')
            func.update_phd(num, thesis, starts, ends, supervisors)


        #postdoc
        starts = request.form.getlist('postdoc_start')
        if starts:
            ends = request.form.getlist('postdoc_end')
            primary = request.form['postdoc_primary']
            secondary = request.form.getlist('postdoc_secondary_link')
            func.update_postdoc(num, starts, ends, primary, secondary)

        #associates
        starts = request.form.getlist('associate_start')
        if starts:
            ends = request.form.getlist('associate_end')
            position_names = request.form.getlist('associate_position')
            pos_starts = []
            pos_ends = []
            for i in range(0, len(position_names)):
                pos_starts.append(request.form.getlist('associate_' + str(i) + '_start'))
                pos_ends.append(request.form.getlist('associate_' + str(i) + '_end'))

            func.update_associate(num, position_names, pos_starts, pos_ends, starts, ends)

        #adding categories
        if request.form.get('cat-add-btn'):
            cat = request.form.get('new_category')
            func.add_cat(num, cat)

            func.db.session.commit()
            return redirect(url_for('update', id=num))
        
        #removing categories
        rm = request.form.get('rm-cat')
        if rm:
            func.rm_cat(num, rm)
            
            func.db.session.commit()
            return redirect(url_for('update', id=num))

        func.db.session.commit()
        return redirect(url_for('person', id=num))

@app.route('/addcategory/<id>', methods=['POST'])
def add_category(id):
    cat = request.form.get('new_category')
    func.add_cat(id, cat)
    func.db.session.commit()
    return redirect(url_for('update', id=id))

@app.route('/addperson')
def add_person():
    new_id = func.add_person()
    return redirect(url_for('update', id=new_id))

@app.route('/deleteperson/<id>', methods=['POST'])
def delete_person(id):
    func.delete_person(id)
    return redirect(url_for('index'))

@app.route('/test', methods=['POST','GET'])
def test():
    return render_template('test.html')

@app.route('/testsend', methods=['POST'])
def testsend():
    if request.method == 'POST':
        print "posted"
    return redirect(url_for('test'))

if __name__ == '__main__':
    app.debug = True
    app.run()
