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
    return render_template('people/person_detail.html', person=func.People.query.get(id))

@app.route('/update/<id>', methods=['GET'])
def update(id):
    person = func.People.query.get(id)
    return render_template('forms/person_form.html', person=person)

@app.route('/updatesend/<num>', methods=['POST','GET'])
def updatesend(num):
    if request.method == 'POST':
        name = request.form['name']
        url = request.form['url']
        location = request.form['location']
        starts = request.form.getlist('info_start')
        ends = request.form.getlist('info_end')
        func.update_info(num, name, url, location, starts, ends)
        return redirect(url_for('update', id=19))


@app.route('/test')
def test():
    person = func.base_search("David Aspinall")[0]
    return render_template('test.html', person=person)

if __name__ == '__main__':
    app.debug = True
    app.run()
