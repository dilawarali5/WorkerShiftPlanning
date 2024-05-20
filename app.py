# app.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
db = SQLAlchemy(app)

class Worker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

class Shift(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('worker.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

# Push an application context so we can use `db.create_all()`
with app.app_context():
    db.create_all()

@app.route('/worker', methods=['POST'])
def create_worker():
    name = request.json.get('name')
    if Worker.query.filter_by(name=name).first():
        return jsonify({'error': 'Worker already exists'}), 400
    worker = Worker(name=name)
    db.session.add(worker)
    db.session.commit()
    return jsonify({'id': worker.id}), 201

@app.route('/shift', methods=['POST'])
def create_shift():
    worker_id = request.json.get('worker_id')
    start_time = datetime.strptime(request.json.get('start_time'), '%Y-%m-%d %H:%M:%S')
    end_time = start_time + timedelta(hours=8)

    # return 400 if the start_time hour is not 0,8,16, or 24
    if start_time.hour % 8 != 0:
        return jsonify({'error': 'Shifts must start at 00:00, 08:00, 16:00, or 24:00'}), 400
    
    # return 400 if the worker does not exist
    if not Worker.query.get(worker_id):
        return jsonify({'error': 'Worker does not exist'}), 400

    # return 400 if the worker already has a shift on this day
    shifts = Shift.query.filter_by(worker_id=worker_id).all()
    for shift in shifts:
        if shift.start_time.date() == start_time.date():
            return jsonify({'error': 'Worker already has a shift on this day'}), 400
    
    shift = Shift(worker_id=worker_id, start_time=start_time, end_time=end_time)
    db.session.add(shift)
    db.session.commit()
    return jsonify({'id': shift.id}), 201

@app.route('/worker/<int:worker_id>/shifts', methods=['GET'])
def get_shifts(worker_id):
    shifts = Shift.query.filter_by(worker_id=worker_id).all()
    return jsonify([{'id': shift.id, 'start_time': shift.start_time.strftime('%Y-%m-%d %H:%M:%S')} for shift in shifts])

@app.route('/test', methods=['GET'])
def test():
    return jsonify([{'msg': "hello World"}])

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)