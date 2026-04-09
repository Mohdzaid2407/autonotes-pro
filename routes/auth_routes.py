from flask import Blueprint, render_template, request, redirect, session
from flask import flash
import MySQLdb

auth = Blueprint('auth', __name__)

def get_db():
    return MySQLdb.connect(
        host="localhost",
        user="root",
        passwd="zaid@12345",
        db="autonotes_pro"
    )

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            db.close()
            return "Email already registered"

        cursor.execute(
            "INSERT INTO users (full_name, email, password) VALUES (%s, %s, %s)",
            (name, email, password)
        )
        db.commit()

        cursor.close()
        db.close()

        return redirect('/login')

    return render_template('register.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )

        user = cursor.fetchone()

        cursor.close()
        db.close()

        if user:
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['user_email'] = user[2]
            return redirect('/dashboard')
        else:
            return "Invalid email or password"

    return render_template('login.html')


@auth.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@auth.route('/change-password', methods=['GET', 'POST'])
def change_password():

    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':

        old = request.form['old']
        new = request.form['new']

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            "SELECT password FROM users WHERE id=%s",
            (session['user_id'],)
        )

        real = cursor.fetchone()[0]

        if real != old:
            flash("Wrong password", "error")
            return redirect('/change-password')

        cursor.execute(
            "UPDATE users SET password=%s WHERE id=%s",
            (new, session['user_id'])
        )

        db.commit()

        flash("Password changed", "success")

        return redirect('/profile')

    return render_template("change_password.html")