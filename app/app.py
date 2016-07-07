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

@app.route('/update', methods=['GET'])
def update():
    person = func.base_search("David Aspinall")[0]
    return render_template('forms/person_form.html', person=person)

@app.route('/updatetest', methods=['POST'])
def updatetest():
    name=None
    if request.method == 'POST':
        name = request.form.getlist('staff_position')
        for i in range(0, len(name)):
            start = request.form.getlist(str(i) + '_start')
            end = request.form.getlist(str(i) + '_end')
            print name[i], start, end
        return redirect(url_for('update'))


@app.route('/test')
def test():
    person = func.base_search("David Aspinall")[0]
    return render_template('test.html', person=person)

if __name__ == '__main__':
    app.debug = True
    app.run()
