# test_app.py
import pytest
from app import app, db, Worker, Shift
from datetime import datetime
import os

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_create_worker(client):
    rv = client.post('/worker', json={'name': 'Test Worker'})
    assert rv.status_code == 201
    assert rv.get_json()['id'] == 1

def test_create_shift(client):
    client.post('/worker', json={'name': 'Test Worker'})
    rv = client.post('/shift', json={'worker_id': 1, 'start_time': '2022-01-01 00:00:00'})
    assert rv.status_code == 201
    assert rv.get_json()['id'] == 1

def test_create_shift_conflict(client):
    client.post('/worker', json={'name': 'Test Worker'})
    client.post('/shift', json={'worker_id': 1, 'start_time': '2022-01-01 00:00:00'})
    rv = client.post('/shift', json={'worker_id': 1, 'start_time': '2022-01-01 04:00:00'})
    assert rv.status_code == 400

def test_create_shift_invalid_time(client):
    client.post('/worker', json={'name': 'Test Worker'})
    rv = client.post('/shift', json={'worker_id': 1, 'start_time': '2022-01-01 01:00:00'})
    assert rv.status_code == 400

def test_create_shift_invalid_worker(client):
    rv = client.post('/shift', json={'worker_id': 2, 'start_time': '2022-01-01 00:00:00'})
    assert rv.status_code == 400

def test_multiple_days_shift(client):
    client.post('/worker', json={'name': 'Test Worker'})
    rv = client.post('/shift', json={'worker_id': 1, 'start_time': '2022-01-02 08:00:00'})
    assert rv.status_code == 201
    rv = client.post('/shift', json={'worker_id': 1, 'start_time': '2022-01-03 16:00:00'})
    assert rv.status_code == 201

def test_shift_conflict_multiple_days(client):
    client.post('/worker', json={'name': 'Test Worker'})
    rv = client.post('/shift', json={'worker_id': 1, 'start_time': '2022-01-02 00:00:00'})
    assert rv.status_code == 400
    rv = client.post('/shift', json={'worker_id': 1, 'start_time': '2022-01-03 00:00:00'})
    assert rv.status_code == 400

def test_get_shifts(client):
    client.post('/worker', json={'name': 'Test Worker'})
    client.post('/shift', json={'worker_id': 1, 'start_time': '2022-01-01 00:00:00'})
    rv = client.get('/worker/1/shifts')
    assert rv.status_code == 200
    assert rv.get_json() == [{'id': 1, 'start_time': '2022-01-01 00:00:00'},{'id': 2, 'start_time': '2022-01-02 08:00:00'},{'id': 3, 'start_time': '2022-01-03 16:00:00'}]