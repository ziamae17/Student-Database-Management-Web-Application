from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'


# init MYSQL
mysql = MySQL(app)

# Index
@app.route('/')
def index():
    return render_template('home.html')

# About
@app.route('/about')
def about():
    return render_template('about.html')

# Register Form Class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("INSERT INTO userlogin (name, email, username, password) VALUES (%s, %s, %s, %s)", (name, email, username, password))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('index'))
    return render_template('register.html', form=form)

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM userlogin WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)

            # Close connection
            cur.close()

        else:
            error = 'Username not found'
            return render_template('login.html', error=error)
    return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard(info=0):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get student
    result = cur.execute("SELECT * FROM students")

    data = cur.fetchall()
    if info != 0:
        newdata = []
        for y in data:
            print (y)
            #a,b,c,d,e,f,g,h=y
            cake = [y.get('id'),y.get('idno'),y.get('firstname'),y.get('lastname'),y.get('gender'),y.get('course'),y.get('year'),y.get('create_date')]
            for z in cake:
                #print (y[1])
                if z == info:
                    newdata.append (y)
                    print (z+" = "+info)
                    break
        data = newdata 
        print (data)
        return render_template('dashboard.html', students=data) 

    elif result > 0:
        return render_template('dashboard.html', students=data)  
    else:
        msg = 'No Students Found'
        return render_template('dashboard.html', msg=msg)
   
    #Close connection
    cur.close()

# Student Form Class
class StudentForm(Form):
    idno = StringField('ID No:', [validators.Length(min=1, max=9)])
    firstname = StringField('First Name:', [validators.Length(min=1, max=50)])
    lastname = StringField('Last Name:', [validators.Length(min=1, max=50)])
    gender = StringField('Gender:', [validators.Length(min=1, max=6)])
    course = StringField('Course:', [validators.Length(min=4, max=25)])
    year = StringField('Year Level:', [validators.Length(min=1, max=1)])

# Add Student
@app.route('/add_student', methods=['GET', 'POST'])
@is_logged_in
def add_student():
    form = StudentForm(request.form)
    if request.method == 'POST' and form.validate():
        idno = form.idno.data
        firstname = form.firstname.data
        lastname = form.lastname.data
        gender = form.gender.data
        course = form.course.data
        year = form.year.data

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute
        cur.execute("INSERT INTO students(idno, firstname, lastname, gender, course, year) VALUES(%s, %s, %s, %s, %s, %s)",(idno, firstname, lastname, gender, course, year))

        # Commit to DB
        mysql.connection.commit()

        #Close connection
        cur.close()

        flash('Student Data Created', 'success')

        return redirect(url_for('dashboard'))
    
    return render_template('add_student.html', form=form)


# Edit Student
@app.route('/edit_student', methods = ['POST'])
def edit_student():
    if request.method == 'POST':
        flash("Data Updated Successfully")

        idno = request.form['idno']
        firstname = request.form['firstname']
        gender = request.form['gender']
        lastname = request.form['lastname']
        course = request.form['course']
        year = request.form['year']

        #Create cursor
        cur = mysql.connection.cursor()

        #Execute
        cur.execute("UPDATE students SET firstname=%s, lastname=%s, gender=%s, course=%s, year=%s WHERE idno=%s", (firstname, lastname, gender, course, year, idno))
        
        #Commit to DB
        mysql.connection.commit()

        #Close connection
        cur.close()
        return redirect(url_for('dashboard'))
#Dili ni final


# Delete Student
@app.route('/delete_student/<string:id>', methods=['GET'])
@is_logged_in
def delete_student(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Execute
    cur.execute("DELETE FROM students WHERE id = %s", [id])

    # Commit to DB
    mysql.connection.commit()

    #Close connection
    cur.close()

    flash('Student Deleted', 'success')

    return redirect(url_for('dashboard'))

# Search Student
@app.route('/search_student', methods = ['POST'])
def search_student():

    stud = request.form['searchbar']
    print (stud)
    return dashboard(stud)


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(debug=True)