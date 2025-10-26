from flask import Flask, render_template, request, redirect, session, url_for
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For session management

# Load user credentials from CSV
def load_users():
    return pd.read_csv('users.csv')

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        login_id = request.form['login_id']
        password = request.form['password']

        users_df = load_users()
        matched_user = users_df[(users_df['login_id'] == login_id) & (users_df['password'] == password)]

        if not matched_user.empty:
            session['user'] = login_id
            return redirect('/dashboard')
        else:
            msg = 'Invalid Login ID or Password'

    return render_template('login.html', msg=msg)

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('chandu.html', user=session['user'])
    return redirect('/login')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')
