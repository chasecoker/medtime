from flask import Flask, render_template, url_for, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta 
import numpy as np

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
db = SQLAlchemy(app)

# initilizing the database and its columns.
class Meds(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    medtype = db.Column(db.String(60), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    time_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Med %r' % self.id

# application route to run logic to determine if the time has elapsed since medication was taken.
@app.route('/notify', methods=['POST'])
def notify_user():
    due = []
    medi = Meds.query.order_by(Meds.id).all()
    for x in medi:
        delt = x.duration
        delt_var = timedelta(minutes=delt)
        diff = ((x.time_created) + delt_var)
        if diff < datetime.utcnow():
            i = str(x.medtype)
            due.append(i)

    return jsonify('', render_template('notify_user.html', x=due))

# application route to add new medications and time intervals to take them.
@app.route('/', methods=['POST', 'GET'])
def index():

    if request.method == 'POST':
        med_content = request.form['medication']
        time_content = int(request.form['interval'])
        new_med = Meds(medtype=med_content, duration=time_content)

        try:
            db.session.add(new_med)
            db.session.commit()
            return redirect('/')
        except:
            return 'Failed to Create'

    else:
        meds = Meds.query.order_by(Meds.id).all()
        return render_template('index.html', meds=meds)
        
# application route to delete a medication from the que from its unique id.
@app.route('/delete/<int:id>')
def delete(id):
    med_to_delete = Meds.query.get_or_404(id)

    try:
        db.session.delete(med_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'Failed to Delete'

# application route to reset the clock on a medication when taken by its unique id.
@app.route('/take/<int:id>')
def take(id):
    med_to_take = Meds.query.get_or_404(id)

    try:
        newtime = datetime.utcnow()
        med_to_take.time_created = newtime
        db.session.commit()
        return redirect('/')
    except:
        return 'could not be taken' 


if __name__ == "__main__":
    app.run(debug=True)