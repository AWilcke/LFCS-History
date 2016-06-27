from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy, BaseQuery

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///lfcs-test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

@app.route('/')
def index():
    return render_template('welcome.html')

# Save e-mail to database and send to success page
@app.route('/search', methods=['POST'])
def search():
    search=None
    if request.method == 'POST':
        search = request.form['search']
        print search
        return render_template('welcome.html')

if __name__ == '__main__':
    app.debug = True
    app.run()
