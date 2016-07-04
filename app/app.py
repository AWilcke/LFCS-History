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

@app.route('/results/<query>', methods=['GET'])
def results(query):
    results=func.base_search(query)
    return render_template('results.html', results=results, query=query)


@app.route('/person/<id>')
def person(id):
    return render_template('person_detail.html', person=func.People.query.get(id))

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/testing', methods=['POST'])
def testing():
    first=None
    if request.method == 'POST':
        first = request.form.getlist('positions')
        print first
        return redirect(url_for('test'))

if __name__ == '__main__':
    app.debug = True
    app.run()
