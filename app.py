
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def init_db():
    with sqlite3.connect("health.db") as conn:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS patients (id INTEGER PRIMARY KEY, name TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS doctors (id INTEGER PRIMARY KEY, name TEXT, specialty TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS appointments (id INTEGER PRIMARY KEY, patient_id INTEGER, doctor_id INTEGER, date TEXT)")
        c.execute("INSERT OR IGNORE INTO users (id, username, password) VALUES (1, 'admin', 'admin')")
        conn.commit()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect("health.db") as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            user = c.fetchone()
            if user:
                session['user'] = username
                return redirect(url_for('dashboard'))
        return "Invalid credentials"
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/patients', methods=['GET', 'POST'])
def patients():
    if 'user' not in session:
        return redirect(url_for('login'))
    with sqlite3.connect("health.db") as conn:
        c = conn.cursor()
        if request.method == 'POST':
            name = request.form['name']
            c.execute("INSERT INTO patients (name) VALUES (?)", (name,))
            conn.commit()
        c.execute("SELECT * FROM patients")
        patients = c.fetchall()
    return render_template('patients.html', patients=patients)

@app.route('/doctors', methods=['GET', 'POST'])
def doctors():
    if 'user' not in session:
        return redirect(url_for('login'))
    with sqlite3.connect("health.db") as conn:
        c = conn.cursor()
        if request.method == 'POST':
            name = request.form['name']
            specialty = request.form['specialty']
            c.execute("INSERT INTO doctors (name, specialty) VALUES (?, ?)", (name, specialty))
            conn.commit()
        c.execute("SELECT * FROM doctors")
        doctors = c.fetchall()
    return render_template('doctors.html', doctors=doctors)

@app.route('/appointments', methods=['GET', 'POST'])
def appointments():
    if 'user' not in session:
        return redirect(url_for('login'))
    with sqlite3.connect("health.db") as conn:
        c = conn.cursor()
        if request.method == 'POST':
            patient_id = request.form['patient_id']
            doctor_id = request.form['doctor_id']
            date = request.form['date']
            c.execute("INSERT INTO appointments (patient_id, doctor_id, date) VALUES (?, ?, ?)", (patient_id, doctor_id, date))
            conn.commit()
        c.execute("SELECT a.id, p.name, d.name, a.date FROM appointments a JOIN patients p ON a.patient_id=p.id JOIN doctors d ON a.doctor_id=d.id")
        appointments = c.fetchall()
        c.execute("SELECT * FROM patients")
        patients = c.fetchall()
        c.execute("SELECT * FROM doctors")
        doctors = c.fetchall()
    return render_template('appointments.html', appointments=appointments, patients=patients, doctors=doctors)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
