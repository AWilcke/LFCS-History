from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy, BaseQuery
import functions

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
        print search
        return redirect(url_for('results', query=search))

@app.route('/results/<query>', methods=['GET'])
def results(query):
    results=functions.search(query)
    return render_template('results.html', results=results)
'''
@app.route('/test')
def test():
    don = database.Staff.query.get(1)
    return render_template('person.html', result=don)
'''
if __name__ == '__main__':
    app.debug = True
    app.run()
