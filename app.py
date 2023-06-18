from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user

app = Flask(__name__)
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'user'
app.secret_key = 'your_secret_key'

conn = mysql.connector.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    password=app.config['MYSQL_PASSWORD'],
    database=app.config['MYSQL_DB']
)
cursor = conn.cursor()

login_manager = LoginManager(app)

class User(UserMixin):
    pass

@login_manager.user_loader
def load_user(user_id):
    select_user_query = "SELECT * FROM user WHERE id = %s"
    cursor.execute(select_user_query, (user_id,))
    user_data = cursor.fetchone()

    if user_data:
        user = User()
        user.id = user_data[0]
        user.name = user_data[1]
        user.email = user_data[2]
        user.password = user_data[3]
        user.role = user_data[4]
        return user

    return None

@app.route('/')
def home():
    return render_template('student/home.html')

@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        # Check if user with the same email already exists
        existing_user_query = "SELECT * FROM user WHERE email = %s"
        cursor.execute(existing_user_query, (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            error_message = 'User with this email already exists! Please try a different email.'
            return render_template('student/registration.html', error_message=error_message, name=name, email=email)

        # Create a new user
        new_user_query = "INSERT INTO user (name, email, password, role) VALUES (%s, %s, %s, %s)"
        cursor.execute(new_user_query, (name, email, password, role))
        conn.commit()

        registration_success = True
        return render_template('student/registration.html', registration_success=registration_success)

    return render_template('student/registration.html')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return redirect(url_for('login'))

        find_user_query = "SELECT * FROM user WHERE email = %s"
        cursor.execute(find_user_query, (email,))
        user_data = cursor.fetchone()

        if not user_data or user_data[3] != password:
            flash('Invalid email or password!', 'error')
            return redirect(url_for('login'))

        user = User()
        user.id = user_data[0]
        user.name = user_data[1]
        user.email = user_data[2]
        user.password = user_data[3]
        user.role = user_data[4]

        login_user(user)
        flash('Logged in successfully!', 'success')
        return redirect(url_for('profile'))

    return render_template('student/login.html')

@app.route('/profile')
def profile():
    if current_user.is_authenticated:
        if current_user.role == 'student':
            return redirect(url_for('student_profile'))
        elif current_user.role == 'teacher':
            return redirect(url_for('teacher_profile'))
    flash('Please log in to access the profile page.', 'error')
    return redirect(url_for('login'))

@app.route('/profile/student')
def student_profile():
    if current_user.is_authenticated and current_user.role == 'student':
        return render_template('student/student_profile.html', current_user=current_user)
    return redirect(url_for('login'))
@app.route('/teacher_profile')


def teacher_profile():
    if current_user.is_authenticated and current_user.role == 'teacher':
        # Modify the MySQL query according to your database schema
        select_students_query = "SELECT * FROM user WHERE role = 'student'"
        cursor.execute(select_students_query)
        students = cursor.fetchall()

        return render_template('student/teacher_profile.html', current_user=current_user, students=students)
    else:
        flash('Invalid email or password for teacher role.', 'error')
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
