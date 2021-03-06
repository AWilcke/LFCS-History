from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
from lfcsapp import app, bcrypt, login_manager, os
import lfcsapp.func as func
import lfcsapp.backup as backup
from apscheduler.schedulers.background import BackgroundScheduler
import re

@app.before_first_request
def start_jobs():
    sched = BackgroundScheduler()
    sched.start()
    print "Scheduling started"
    #create automatic backup at midnight
    sched.add_job(lambda:backup.backup(os.environ['DB_NAME']), 'cron', hour='0', minute='0', second='0')
    #clean backups before midnight
    sched.add_job(backup.clean_backups, 'cron', hour='23', minute='59', second='0')
    #clear non final suggestions at midnight
    sched.add_job(func.clear_suggestions, 'cron', hour='0', minute='0', second='0')
    #increment current staffs dates every year
    sched.add_job(func.new_year, 'cron', month='1', day='1', hour='1', minute='0', second='0')

@app.errorhandler(404)
def page_not_found(e):
        flash("The page you are looking for does not seem to exist", ('warn','bottom right'))
        return redirect(url_for('index'))

#checks if previous is safe, else returns to index
def return_to_previous(request):
    previous = request.referrer
    if previous:
        if re.match('http://localhost.*', previous):
            return previous
    
    return url_for('index')

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
    query = request.form.get('search')
    #filters
    name = request.form.get('name')
    location = request.form.get('location')
    nationality = request.form.get('nationality')
    date_type = request.form.get('date_type')
    start = request.form.get('start')
    end = request.form.get('end')
    full_query = '%s&=%s&=%s&=%s&=%s&=%s&=%s' % (query, name, location, nationality, date_type, start, end)
    return redirect(url_for('advanced_results', full_query=full_query))
    
@app.route('/advanced/results/<full_query>')
def advanced_results(full_query):
    query, name, location, nationality, date_type, start, end = full_query.split('&=')
    results = func.advanced_search(query, name, location, nationality, date_type, start, end)

    #to display information about query
    if date_type=='inclusive':
        typ = 'between'
    else:
        typ = 'exactly'
    
    if query=='' or query=='*':
        query='all'

    display_query = query + ', filters: name: %s, location: %s, nationality: %s, %s start: %s, end: %s' % (name, location, nationality, typ, start, end)
    return render_template('results.html', results=results, query=display_query)

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

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/person/<id>')
def person(id):
    person=func.People.query.get(id)
    if person:
        return render_template('people/person_detail.html', person=person)
    else:
        flash("The page you are looking for does not seem to exist", ('warn','bottom right'))
        return redirect(return_to_previous(request))

@app.route('/grant/<id>')
def grant(id):
    grant = func.Grants.query.get(id)
    if grant:
        return render_template('people/grant.html', grant=grant)
    else:
        flash("The page you are looking for doesn't seem to exist", ('warn','bottom right'))
        return redirect(return_to_previous(request))

@login_manager.user_loader
def user_loader(user_id):
    return func.Users.query.get(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    flash("It looks like you tried to access an unauthorized page! Please log in.", ("warn","bottom right"))
    return redirect(return_to_previous(request))

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
            suggestions = func.Suggestions.query.filter(func.Suggestions.final==True).count()

            if suggestions>0:
                flash("There are %d pending suggestions" % (suggestions), ("warn","bottom right"))
            flash(user.first_name + ' logged in!', ("success", "bottom right"))
        else:
            flash("Invalid credentials", ("error", "bottom right"))
    else:
        flash("Invalid credentials", ("error", "bottom right"))

    return redirect(return_to_previous(request))

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

    exists = func.Users.query.get(email)
    if exists!=current_user:
        flash('That email is already in use', ('error','bottom right'))
        return redirect(return_to_previous(request))
    
    func.update_user(first_name, last_name, email, pasw)
    func.db.session.commit()
    
    #log in again
    user = func.Users.query.get(email)
    user.authenticated = True
    func.db.session.commit()
    login_user(user, remember=True)
    
    flash('Updated account information for ' + email, ('success','bottom right'))
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

    exists = func.Users.query.get(email)
    if exists:
        flash('That email is already in use', ('error','bottom right'))
        return redirect(return_to_previous(request))

    func.add_user(first_name, last_name, email, pasw)
    func.db.session.commit()
    
    flash('Added user account for ' + email, ('success','bottom right'))

    return redirect(return_to_previous(request))

@app.route('/deleteuser', methods=['POST'])
@login_required
def delete_user():
    flash('User account for ' + current_user.email + ' deleted', ('success','bottom right'))
    func.db.session.delete(func.Users.query.get(current_user.email))
    func.db.session.commit()
    logout_user()
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
        return redirect(return_to_previous(request))

@app.route('/updatesend/<num>', methods=['POST','GET'])
@login_required
def updatesend(num):
    if request.method == 'POST':
        person = func.People.query.get(num)
        #basic info
        name = request.form['name']
        url = request.form['url']
        location = request.form['location']
        nationality = request.form['nationality']
        starts = request.form.getlist('info_start')
        ends = request.form.getlist('info_end')
        func.update_info(person, name, url, location, nationality, starts, ends)

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

            research = request.form.get('explorer')
            grant_titles = request.form.getlist('grant_title')
            grant_urls = request.form.getlist('grant_url')
            grant_values = request.form.getlist('grant_value')
            grant_refs = request.form.getlist('grant_ref')
            grant_orgs = request.form.getlist('grant_org')
            grant_starts = request.form.getlist('grant_start')
            grant_ends = request.form.getlist('grant_end')
            grant_secondary = []
            for i in range(0, len(grant_titles)):
                grant_secondary.append(request.form.getlist('grant_' + str(i) + '_link'))
                
            students = request.form.getlist('staff_phd_link')
            postdocs = request.form.getlist('staff_primary_link')
            
            func.update_staff(person, position_names, pos_starts, pos_ends, research, grant_titles, grant_values, grant_urls, grant_refs, grant_orgs, grant_starts, grant_ends, grant_secondary, starts, ends, students, postdocs)

        #phd
        starts = request.form.getlist('phd_start')
        if starts:
            ends = request.form.getlist('phd_end')
            thesis = request.form['thesis']
            supervisors = request.form.getlist('phd_staff_link')
            func.update_phd(person, thesis, starts, ends, supervisors)


        #postdoc
        starts = request.form.getlist('postdoc_start')
        if starts:
            ends = request.form.getlist('postdoc_end')
            inv = request.form.getlist('postdoc_primary_link')
            func.update_postdoc(person, starts, ends, inv)

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

            func.update_associate(person, position_names, pos_starts, pos_ends, starts, ends)

        #adding categories
        if request.form.get('cat-add-btn'):
            cat = request.form.get('new_category')
            func.add_cat(person, cat)

            func.db.session.commit()
            return redirect(url_for('update', id=num))
        
        #removing categories
        rm = request.form.get('rm-cat')
        if rm:
            func.rm_cat(person, rm)
            
            func.db.session.commit()
            return redirect(url_for('update', id=num))

        func.db.session.commit()
        flash('Updated information for ' + name, ('success','bottom right'))
        return redirect(url_for('person', id=num))

#initial suggestion
@app.route('/suggest/<id>', methods=['GET'])
def suggest(id):
    person = func.People.query.get(id)
    students = [student.person for student in func.PhD.query.all()]
    staff = [staff.person for staff in func.Staff.query.all()]
    postdocs = [postdoc.person for postdoc in func.PostDoc.query.all()]
    if person:
        return render_template('suggest/initial.html', person=person, students=students, staff=staff, postdocs=postdocs)
    else:
        return redirect(return_to_previous(request))

@app.route('/suggestsend/<num>', methods=['POST'])
def suggestsend(num):
    if request.method == 'POST':
        person = func.People.query.get(num)
        suggest = func.Suggestions()
        suggest.person = person
        func.db.session.add(suggest)
        func.db.session.commit()
        
        #basic info
        name = request.form['name']
        url = request.form['url']
        location = request.form['location']
        nationality = request.form['nationality']
        starts = request.form.getlist('info_start')
        ends = request.form.getlist('info_end')
        func.update_info(person, name, url, location, nationality, starts, ends)

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

            research = request.form.get('explorer')
            grant_titles = request.form.getlist('grant_title')
            grant_urls = request.form.getlist('grant_url')
            grant_values = request.form.getlist('grant_value')
            grant_refs = request.form.getlist('grant_ref')
            grant_orgs = request.form.getlist('grant_org')
            grant_starts = request.form.getlist('grant_start')
            grant_ends = request.form.getlist('grant_end')
            grant_secondary = []
            for i in range(0, len(grant_titles)):
                grant_secondary.append(request.form.getlist('grant_' + str(i) + '_link'))
                
            students = request.form.getlist('staff_phd_link')
            postdocs = request.form.getlist('staff_primary_link')
            
            func.update_staff(person, position_names, pos_starts, pos_ends, research, grant_titles, grant_values, grant_urls, grant_refs, grant_orgs, grant_starts, grant_ends, grant_secondary, starts, ends, students, postdocs)

        #phd
        starts = request.form.getlist('phd_start')
        if starts:
            ends = request.form.getlist('phd_end')
            thesis = request.form['thesis']
            supervisors = request.form.getlist('phd_staff_link')
            func.update_phd(person, thesis, starts, ends, supervisors)


        #postdoc
        starts = request.form.getlist('postdoc_start')
        if starts:
            ends = request.form.getlist('postdoc_end')
            inv = request.form.getlist('postdoc_primary_link')
            func.update_postdoc(person, starts, ends, inv)

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

            func.update_associate(person, position_names, pos_starts, pos_ends, starts, ends)

        #adding categories
        if request.form.get('cat-add-btn'):
            cat = request.form.get('new_category')
            func.add_cat(person, cat)
            dic = func.person_to_dict(person)
            func.db.session.rollback()
            suggest.dict = str(dic)
            func.db.session.commit()
            return redirect(url_for('suggest_edit', ind=suggest.id))
        
        #store submitted form as a dic
        dic = func.person_to_dict(person)
        func.db.session.rollback()
        
        #removing categories
        rm = request.form.get('rm-cat')
        if rm:
            cat = rm.replace('rm-','')
            dic[cat] = {}
            suggest.dict = str(dic)
            func.db.session.commit()
            return redirect(url_for('suggest_edit', ind=suggest.id))

        suggest.dict = str(dic)
        suggest.final = True
        func.db.session.commit()
        flash('Thank you for your contribution',('success','bottom right'))
        return redirect(url_for('person',id=num)) 

#for editing an initial suggestion (adding categories)
@app.route('/suggest_edit/<ind>')
def suggest_edit(ind):
    suggest = func.Suggestions.query.get(ind)
    if suggest.final:
        flash("This suggestion has already been submitted, please submit another one", ("danger","bottom right"))
        return redirect(url_for('index'))

    dic = suggest.dict
    if dic:
        dic = eval(dic)
        person = func.dic_to_person(dic)
        students = [student.person for student in func.PhD.query.all()]
        staff = [staff.person for staff in func.Staff.query.all()]
        postdocs = [postdoc.person for postdoc in func.PostDoc.query.all()]
        return render_template('suggest/edit.html', ind=ind, person=person, students=students, staff=staff, postdocs=postdocs)

@app.route('/suggest_edit_send/<ind>', methods=['POST'])
def suggest_edit_send(ind):
    suggest = func.Suggestions.query.get(ind)
    dic = suggest.dict
    if request.method == 'POST':
        dic = eval(dic)
        person = func.dic_to_person(dic)
        print person
        cancel = request.form.get('cancel')
        if cancel:
            func.db.session.delete(suggest)
            func.db.session.commit()
            flash('Cancelled suggestion for ' + person.name, ('danger','bottom right'))
            return redirect(url_for('person', id=suggest.person_id))
        
        #basic info
        name = request.form['name']
        url = request.form['url']
        location = request.form['location']
        nationality = request.form['nationality']
        starts = request.form.getlist('info_start')
        ends = request.form.getlist('info_end')
        func.update_info(person, name, url, location, nationality, starts, ends)

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

            research = request.form.get('explorer')
            grant_titles = request.form.getlist('grant_title')
            grant_urls = request.form.getlist('grant_url')
            grant_values = request.form.getlist('grant_value')
            grant_refs = request.form.getlist('grant_ref')
            grant_orgs = request.form.getlist('grant_org')
            grant_starts = request.form.getlist('grant_start')
            grant_ends = request.form.getlist('grant_end')
            grant_secondary = []
            for i in range(0, len(grant_titles)):
                grant_secondary.append(request.form.getlist('grant_' + str(i) + '_link'))
                
            students = request.form.getlist('staff_phd_link')
            postdocs = request.form.getlist('staff_primary_link')
            
            func.update_staff(person, position_names, pos_starts, pos_ends, research, grant_titles, grant_values, grant_urls, grant_refs, grant_orgs, grant_starts, grant_ends, grant_secondary, starts, ends, students, postdocs)

        #phd
        starts = request.form.getlist('phd_start')
        if starts:
            ends = request.form.getlist('phd_end')
            thesis = request.form['thesis']
            supervisors = request.form.getlist('phd_staff_link')
            func.update_phd(person, thesis, starts, ends, supervisors)


        #postdoc
        starts = request.form.getlist('postdoc_start')
        if starts:
            ends = request.form.getlist('postdoc_end')
            inv = request.form.getlist('postdoc_primary_link')
            func.update_postdoc(person, starts, ends, inv)

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

            func.update_associate(person, position_names, pos_starts, pos_ends, starts, ends)

        #adding categories
        if request.form.get('cat-add-btn'):
            cat = request.form.get('new_category')
            func.add_cat(person, cat)
            dic = func.person_to_dict(person)
            func.db.session.rollback()
            suggest.dict = str(dic)
            func.db.session.commit()
            return redirect(url_for('suggest_edit', ind=suggest.id))
        
        #store submitted form as a dic
        dic = func.person_to_dict(person)
        func.db.session.rollback()
        
        #removing categories
        rm = request.form.get('rm-cat')
        if rm:
            cat = rm.replace('rm-','')
            dic[cat] = {}
            suggest.dict = str(dic)
            func.db.session.commit()
            return redirect(url_for('suggest_edit', ind=suggest.id))

        suggest.dict = str(dic)
        suggest.final = True
        func.db.session.commit()
        flash('Thank you for your contribution',('success','bottom right'))
        return redirect(url_for('person', id=suggest.person_id)) 

@login_required
@app.route('/approve_suggestions')
def get_first_suggestion():
    first = func.Suggestions.query.filter_by(final=True).first()
    if first:
        return redirect(url_for('approve_suggestion', id=first.id))
    else:
        flash('There are no more suggestions!',('warn','bottom right'))
        return redirect(url_for('index'))

@login_required
@app.route('/approve_suggestions/<id>')
def approve_suggestion(id):
    suggest = func.Suggestions.query.get(id)
    if not suggest.final:
        return redirect(url_for('get_first_suggestion'))
    person = func.dic_to_person(eval(suggest.dict))
    students = [student.person for student in func.PhD.query.all()]
    staff = [staff.person for staff in func.Staff.query.all()]
    postdocs = [postdoc.person for postdoc in func.PostDoc.query.all()]
    return render_template('suggest/confirm.html', id=suggest.id, num=suggest.person_id, person=person, students=students, staff=staff, postdocs=postdocs)

@login_required
@app.route('/approve_suggest_send/<num>/<id>', methods=['POST'])
def approve_suggest_send(num, id):
    if request.method == 'POST':
        
        suggest = func.Suggestions.query.get(id)
        func.db.session.delete(suggest)
        
        person = func.People.query.get(num)
        
        cancel = request.form.get('cancel')
        if cancel:
            func.db.session.commit()
            flash('Refused update suggestion for ' + person.name, ('error','bottom right'))
            return redirect(url_for('get_first_suggestion'))
       
        
        #basic info
        name = request.form['name']
        url = request.form['url']
        location = request.form['location']
        nationality = request.form['nationality']
        starts = request.form.getlist('info_start')
        ends = request.form.getlist('info_end')
        func.update_info(person, name, url, location, nationality, starts, ends)

        #staff
        starts = request.form.getlist('staff_start')
        if starts:
            if not person.staff:
                person.staff = func.Staff()
            ends = request.form.getlist('staff_end')
            position_names = request.form.getlist('staff_position')
            pos_starts = []
            pos_ends = []
            for i in range(0, len(position_names)):
                pos_starts.append(request.form.getlist('staff_' + str(i) + '_start'))
                pos_ends.append(request.form.getlist('staff_' + str(i) + '_end'))
            
            research = request.form.get('explorer')
            grant_titles = request.form.getlist('grant_title')
            grant_urls = request.form.getlist('grant_url')
            grant_values = request.form.getlist('grant_value')
            grant_refs = request.form.getlist('grant_ref')
            grant_orgs = request.form.getlist('grant_org')
            grant_starts = request.form.getlist('grant_start')
            grant_ends = request.form.getlist('grant_end')
            grant_secondary = []
            for i in range(0, len(grant_titles)):
                grant_secondary.append(request.form.getlist('grant_' + str(i) + '_link'))
                
            students = request.form.getlist('staff_phd_link')
            postdocs = request.form.getlist('staff_primary_link')
            
            func.update_staff(person, position_names, pos_starts, pos_ends, research, grant_titles, grant_values, grant_urls, grant_refs, grant_orgs, grant_starts, grant_ends, grant_secondary, starts, ends, students, postdocs)
        elif person.staff:
            person.staff = None

        #phd
        starts = request.form.getlist('phd_start')
        if starts:
            if not person.phd:
                person.phd = func.PhD()
            ends = request.form.getlist('phd_end')
            thesis = request.form['thesis']
            supervisors = request.form.getlist('phd_staff_link')
            func.update_phd(person, thesis, starts, ends, supervisors)
        elif person.phd:
            person.phd = None

        #postdoc
        starts = request.form.getlist('postdoc_start')
        if starts:
            if not person.postdoc:
                person.postdoc = func.PostDoc()
            ends = request.form.getlist('postdoc_end')
            inv = request.form.getlist('postdoc_primary_link')
            func.update_postdoc(person, starts, ends, inv)
        elif person.postdoc:
            person.postdoc = None

        #associates
        starts = request.form.getlist('associate_start')
        if starts:
            if not person.associate:
                person.associate = func.Associates()
            ends = request.form.getlist('associate_end')
            position_names = request.form.getlist('associate_position')
            pos_starts = []
            pos_ends = []
            for i in range(0, len(position_names)):
                pos_starts.append(request.form.getlist('associate_' + str(i) + '_start'))
                pos_ends.append(request.form.getlist('associate_' + str(i) + '_end'))

            func.update_associate(person, position_names, pos_starts, pos_ends, starts, ends)
        elif person.associate:
            person.associate = None

        flash('Accepted edit suggestion for ' + name, ('success','bottom right'))
        #adding categories
        if request.form.get('cat-add-btn'):
            cat = request.form.get('new_category')
            func.add_cat(person, cat)
            func.db.session.commit()
            return redirect(url_for('update', id=num))
        
        #removing categories
        rm = request.form.get('rm-cat')
        if rm:
            func.rm_cat(person, rm)
            func.db.session.commit()
            return redirect(url_for('update', id=num))


        func.db.session.commit()
        return redirect(url_for('get_first_suggestion'))


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

@login_required
@app.route('/create_backup', methods=['POST'])
def create_backup():
    name = request.form.get('backup_name')
    backup.backup(os.environ['DB_NAME'], name=name)
    return redirect(return_to_previous(request))

@login_required
@app.route('/backup')
def view_backups():
    backups = backup.get_backups()
    return render_template('backup.html', list=backups)

@login_required
@app.route('/restore_backup/<version>', methods=['POST'])
def restore_backup(version):
    time = backup.restore(os.environ['DB_NAME'], version)
    flash("Restored database version from %s" % (time), ('success','bottom right'))
    return redirect(return_to_previous(request))

@login_required
@app.route('/delete_backup/<version>', methods=['POST'])
def delete_backup(version):
    backup.delete_backup(version)
    return redirect(url_for('view_backups'))

@login_required
@app.route('/clean')
def clean():
    backup.clean_backups()
    return redirect(return_to_previous(request))
