from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import os
from werkzeug.utils import secure_filename
import config

app = Flask(__name__)
app.secret_key = 'space_secret'
app.config.from_object(config)

mysql = MySQL(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'explorer123':
            session['admin'] = True
            return redirect(url_for('index'))
        else:
            return 'Identifiants incorrects'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))


@app.route('/')
def index():
    cur = mysql.connection.cursor()

    cur.execute("SELECT COUNT(*) FROM planets")
    planet_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM explorers")
    explorer_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM missions")
    mission_count = cur.fetchone()[0]

    return render_template('index.html', 
        planet_count=planet_count, 
        explorer_count=explorer_count, 
        mission_count=mission_count
    )

@app.route('/planets')
def planets():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM planets")
    data = cur.fetchall()
    return render_template('planets.html', planets=data)

@app.route('/add_planet', methods=['GET', 'POST'])
def add_planet():
    if request.method == 'POST':
        name = request.form['name']
        type = request.form['type']
        distance = request.form['distance']
        temperature = request.form['temperature']
        habitable = 1 if 'habitable' in request.form else 0
        description = request.form['description']
        discovery_date = request.form['discovery_date']
        
        # image
        image = request.files['image']
        filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO planets (name, type, distance, temperature, habitable, description, image_url, discovery_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (name, type, distance, temperature, habitable, description, image_path, discovery_date))
        mysql.connection.commit()
        return redirect(url_for('planets'))

    return render_template('add_planet.html')

@app.route('/planet/<int:id>')
def planet_detail(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM planets WHERE id = %s", (id,))
    planet = cur.fetchone()
    return render_template('planet_detail.html', planet=planet)

@app.route('/reserve', methods=['GET', 'POST'])
def reserve():
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        planet_id = request.form['planet_id']
        explorer_id = request.form['explorer_id']
        departure_date = request.form['departure_date']
        duration = request.form['duration']

        cur.execute("""
            INSERT INTO missions (planet_id, explorer_id, departure_date, duration)
            VALUES (%s, %s, %s, %s)
        """, (planet_id, explorer_id, departure_date, duration))
        mysql.connection.commit()

        return redirect(url_for('planets'))

    # Récupérer les listes pour les menus déroulants
    cur.execute("SELECT id, name FROM planets")
    planets = cur.fetchall()

    cur.execute("SELECT id, name FROM explorers")
    explorers = cur.fetchall()

    return render_template('reserve.html', planets=planets, explorers=explorers)

@app.route('/missions')
def missions():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT missions.id, planets.name, explorers.name, missions.departure_date, missions.duration, missions.status
        FROM missions
        JOIN planets ON missions.planet_id = planets.id
        JOIN explorers ON missions.explorer_id = explorers.id
    """)
    data = cur.fetchall()
    return render_template('missions.html', missions=data)

@app.route('/explorers')
def explorers():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM explorers")
    data = cur.fetchall()
    return render_template('explorers.html', explorers=data)

@app.route('/add_explorer', methods=['GET', 'POST'])
def add_explorer():
    if 'admin' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        speciality = request.form['speciality']
        experience = request.form['experience']
        email = request.form['email']

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO explorers (name, speciality, experience, email)
            VALUES (%s, %s, %s, %s)
        """, (name, speciality, experience, email))
        mysql.connection.commit()
        return redirect(url_for('explorers'))

    return render_template('add_explorer.html')


@app.route('/edit_explorer/<int:id>', methods=['GET', 'POST'])
def edit_explorer(id):
    if 'admin' not in session:
        return redirect(url_for('login'))

    # suite du traitement...
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        name = request.form['name']
        speciality = request.form['speciality']
        experience = request.form['experience']
        email = request.form['email']
        cur.execute("""
            UPDATE explorers SET name=%s, speciality=%s, experience=%s, email=%s WHERE id=%s
        """, (name, speciality, experience, email, id))
        mysql.connection.commit()
        return redirect(url_for('explorers'))

    cur.execute("SELECT * FROM explorers WHERE id=%s", (id,))
    explorer = cur.fetchone()
    return render_template('edit_explorer.html', explorer=explorer)

@app.route('/delete_explorer/<int:id>')
def delete_explorer(id):
    if 'admin' not in session:
        return redirect(url_for('login'))

    # suppression...
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM explorers WHERE id=%s", (id,))
    mysql.connection.commit()
    return redirect(url_for('explorers'))

@app.route('/explorer/<int:id>/missions')
def explorer_missions(id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT missions.id, planets.name, missions.departure_date, missions.duration, missions.status
        FROM missions
        JOIN planets ON missions.planet_id = planets.id
        WHERE explorer_id = %s
    """, (id,))
    missions = cur.fetchall()

    cur.execute("SELECT name FROM explorers WHERE id = %s", (id,))
    explorer = cur.fetchone()

    return render_template('explorer_missions.html', explorer=explorer[0], missions=missions)


if __name__ == '__main__':
    os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
