from flask import render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from lfcsapp import app, bcrypt
import lfcsapp.func as func

login_manager = LoginManager()
login_manager.init_app(app)

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

@app.route('/advancedsearch')
def advanced():
    return render_template('advanced.html')

@app.route('/advancedsend', methods=['POST'])
def advanced_send():
    name = request.form.get('name')
    location = request.form.get('location')
    start = request.form.get('start')
    end = request.form.get('end')
    cat = request.form.get('category')
    results = func.advanced_search(name, location, start, end, cat)
    return render_template('results.html', results=results)

@app.route('/results/<query>')
def results(query):
    results=func.base_search(query)
    return render_template('results.html', results=results, query=query)

@app.route('/viewall')
def view_all():
    return render_template('people/alphabetical.html', results=func.People.query.all())

@app.route('/viewall/<letter>')
def view_letter(letter):
    results = func.People.query.filter(func.People.name.like(letter + "%")).all()
    return render_template('people/alphabetical.html', results=results, letter=letter)

@app.route('/person/<id>')
def person(id):
    person=func.People.query.get(id)
    if person:
        return render_template('people/person_detail.html', person=person)
    else:
        #should add error page
        return redirect(url_for('index'))

@login_manager.user_loader
def user_loader(user_id):
    return func.Users.query.get(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    flash("It looks like you tried to access an unauthorized page! Please log in.", ("warn","bottom right"))
    previous = request.referrer
    if previous:
        return redirect(previous)
    
    return redirect(url_for('index'))

@app.route('/login', methods=['GET','POST'])
def login():

    username = request.form.get('username')
    password = request.form.get('password')
    
    user = func.Users.query.get(username)
    
    if user:
        if bcrypt.check_password_hash(user.password, password):
            user.authenticated = True
            func.db.session.commit()
            login_user(user, remember=True)
            flash(user.first_name + ' logged in!', ("success", "bottom right"))
        else:
            flash("Invalid credentials", ("error", "bottom right"))
    else:
        flash("Invalid credentials", ("error", "bottom right"))

    previous = request.referrer
    if previous:
        return redirect(previous)
    
    return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    user = current_user
    user.authenticated = False
    flash(user.first_name + ' logged out!', ("success", "bottom right"))
    func.db.session.commit()
    logout_user()
    return redirect(url_for('index'))

@app.route('/updateuser')
@login_required
def update_user():
    return render_template('users/user.html')

@app.route('/updateusersend', methods=["POST"])
@login_required
def update_user_send():
    first_name = request.form.get('firstname')
    last_name = request.form.get('lastname')
    email = request.form.get('email')
    pasw = request.form.get('password')

    func.update_user(first_name, last_name, email, pasw)
    func.db.session.commit()
    
    flash('Updated account information for ' + email, ('success','bottom right'))

    previous = request.referrer
    if previous:
        return redirect(previous)
    else:
        return redirect(url_for('index'))

@app.route('/adduser')
@login_required
def add_user():
    return render_template('users/add_user.html')

@app.route('/addusersend', methods=['POST'])
@login_required
def add_user_send():
    first_name = request.form.get('firstname')
    last_name = request.form.get('lastname')
    email = request.form.get('email')
    pasw = request.form.get('password')

    func.add_user(first_name, last_name, email, pasw)
    func.db.session.commit()
    
    flash('Added user account for ' + email, ('success','bottom right'))

    previous = request.referrer
    if previous:
        return redirect(previous)
    else:
        return redirect(url_for('index'))

@app.route('/deleteuser', methods=['POST'])
@login_required
def delete_user():
    flash('User account for ' + current_user.email + ' deleted', ('success','bottom right'))
    logout_user()
    func.db.session.delete(func.Users.query.get(current_user.email))
    func.db.session.commit()
    return redirect(url_for('index'))
    

@app.route('/update/<id>', methods=['GET'])
@login_required
def update(id):
    person = func.People.query.get(id)
    students = [student.person for student in func.PhD.query.all()]
    staff = [staff.person for staff in func.Staff.query.all()]
    postdocs = [postdoc.person for postdoc in func.PostDoc.query.all()]
    if person:
        return render_template('forms/person_form.html', person=person, students=students, staff=staff, postdocs=postdocs)
    else:
        return redirect(url_for('index'))

@app.route('/updatesend/<num>', methods=['POST','GET'])
@login_required
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

            grant_titles = request.form.getlist('grant_title')
            grant_urls = request.form.getlist('grant_url')
            grant_values = request.form.getlist('grant_value')
            grant_starts = request.form.getlist('grant_start')
            grant_ends = request.form.getlist('grant_end')
            grant_secondary = []
            for i in range(0, len(grant_titles)):
                grant_secondary.append(request.form.getlist('grant_' + str(i) + '_link'))
                
            students = request.form.getlist('staff_phd_link')
            primary = request.form.getlist('staff_primary_link')
            secondary = request.form.getlist('staff_secondary_link')
            
            func.update_staff(num, position_names, pos_starts, pos_ends, grant_titles, grant_values, grant_urls, grant_starts, grant_ends, grant_secondary, starts, ends, students, primary, secondary)

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
        flash('Updated information for ' + name, ('success','bottom right'))
        return redirect(url_for('person', id=num))

@app.route('/addperson')
@login_required
def add_person():
    return render_template('forms/add.html')

@app.route('/addpersonsend', methods=['GET','POST'])
def add_person_send():
    if request.method == 'POST':
        name = request.form['name']
        url = request.form['url']
        location = request.form['location']
        starts = request.form.getlist('info_start')
        ends = request.form.getlist('info_end')
        person = func.add_person(name, url, location, starts, ends)
        func.db.session.commit()
        
        if request.form.get('cat-add-btn'):
            cat = request.form.get('new_category')
            func.add_cat(person.id, cat)

            func.db.session.commit()
            return redirect(url_for('update', id=person.id))
        flash('Added ' + name + ' to the database', ('success','bottom right'))
        return redirect(url_for('person', id=person.id))

@app.route('/deleteperson/<id>', methods=['POST'])
@login_required
def delete_person(id):
    flash('Deleted ' + func.People.query.get(id).name + ' from the database', ('success','bottom right'))
    func.delete_person(id)
    return redirect(url_for('index'))

@app.route('/test', methods=['POST','GET'])
def test():
    person = func.base_search('david aspinall')[0]
    return render_template('test.html', person=person)

@app.route('/testsend', methods=['POST'])
def testsend():
    if request.method == 'POST':
        print "posted"
    return redirect(url_for('test'))

