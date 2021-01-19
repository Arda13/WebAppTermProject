from flask import Flask, flash, redirect, url_for, render_template, request, session, abort
# from forms import RegistrationForm, LoginForm, BookForm 
import datetime
import os.path
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db = os.path.join(BASE_DIR, 'Database/db.sqlite3')

# db = 'Database/db.sqlite3'
conn = sqlite3.connect(db)
app = Flask(__name__)
app.secret_key= 'supersecretkey'

# import secrets in python3 
# secrets.token_hex(16)
cur = conn.cursor()
  
  
conn.execute('CREATE TABLE IF NOT EXISTS Users (Name text NOT NULL, Email text NOT NULL, Password text NOT NULL, Contact integer NOT NULL)')


cur.execute('''CREATE TABLE IF NOT EXISTS classes (event_id integer NOT NULL UNIQUE,
				class_title varchar(20) NOT NULL,
				class_type varchar(20) NOT NULL,
				class_data date NOT NULL,
				class_time time NOT NULL,
				info varchar(200),
				location varchar(50) NOT NULL,
				lecturer integer NOT NULL,
				PRIMARY KEY(event_id)	
				);''')

cur.execute('''CREATE TABLE IF NOT EXISTS students (event_id integer NOT NULL,
				name varchar(30) NOT NULL,
				student_mail varchar(7) NOT NULL,
				student_number integer NOT NULL,
				class_type varchar(9) NOT NULL,
				seat_no varchar(2) NOT NULL
				);''')

cur.execute('''CREATE TABLE IF NOT EXISTS lecturers (event_id integer NOT NULL,
				name varchar(30) NOT NULL,
				about text
			);''')

cur.execute('''CREATE TABLE IF NOT EXISTS seats ( event_id integer NOT NULL,
				class_type varchar(9) NOT NULL,
				class_code varchar(2) NOT NULL,
				status integer NOT NULL DEFAULT 0
			);''')
conn.commit()
conn.close()

def check_tables():		
	with sqlite3.connect(db) as conn:
		cur = conn.cursor()
		cur.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
		var = cur.fetchall()
		print(var)

@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    nm = request.form['nm']
    contact = request.form['contact']
    email = request.form['email']
    password = request.form['password']
         
    with sqlite3.connect(db) as con:
      cur = con.cursor()
      #check if User already present
      cur.execute("SELECT Email FROM Users WHERE Email=(?)",[(email)])
      data = cur.fetchall()
      if len(data)>0:
        print('User already exists')
        user_exists=1
      else:
        print("User not found, register new user")
        user_exists=0
        cur.execute("INSERT INTO Users (Name,Email,Password,Contact) VALUES (?,?,?,?)",(nm,email,password,contact) )
        
  return render_template('login.html',user_exists=user_exists, invalid = None, logged_out=None)

@app.route('/',  methods=['GET', 'POST'])
def login():
  invalid = None
  if request.method == 'POST':
    email = request.form['email']
    password = request.form['password']     
    with sqlite3.connect(db) as con:
      cur = con.cursor()
      #Validate user credentails from database
      cur.execute("SELECT Email FROM Users WHERE Email=(?) AND Password=(?)",[(email),(password)])
      data = cur.fetchall()
      if len(data)>0:
        print('Login Success')
        # Fetch name of user
        cur.execute("SELECT Name FROM Users WHERE Email=(?) AND Password=(?)",[(email),(password)])
        nm = cur.fetchall()
        nm=nm[0][0]
        # Store User details in Session and log in user
        session['nm'] = nm
        session['email'] = email
        session['logged_out'] = None
        return redirect(url_for('home'))
      else:
        print("Invalid Login")
        invalid=1  
  return render_template('login.html',user_exists=None, invalid = invalid, logged_out=None)

@app.route('/home')
def home():
	with sqlite3.connect(db) as conn:
		cur = conn.cursor()
		cur.execute("SELECT * FROM classes ORDER BY class_data")
		events = cur.fetchall()
	
	session['logged_out']= 1
	return render_template('home.html',events = events)

@app.route('/seats',methods = ['GET','POST'])
def seats():
	if request.method == 'POST':
		eventid = request.form["eventid"]
		print(eventid)
		with sqlite3.connect(db) as conn:
			cur = conn.cursor()
			cur.execute("SELECT * FROM seats,classes WHERE classes.event_id=? AND classes.event_id = seats.event_id",[eventid])
			seats = cur.fetchall()
			
		return render_template('seats.html',seats = seats, eventid = eventid)
		

@app.route('/bookseat',methods = ['GET','POST'])
def bookseat():
	if request.method == 'POST':
		eventid = request.form["eventid"]
		seatno = request.form["seatno"]

		if(seatno[0]=='A'):
			classtype = "seminar"
		elif(seatno[0]=='B'):
			classtype = "lecture"
		else:
			classtype = "lab"

		name = request.form["name"]
		student_mail = request.form["student_mail"]
		student_number = request.form["student_number"]

		with sqlite3.connect(db) as conn:
			cur = conn.cursor()
			cur.execute("SELECT status FROM seats WHERE seat_no=? AND event_id=?",[seatno,eventid])
			state = cur.fetchall()
			if state[0][0]==0:
				cur.execute("INSERT INTO students VALUES (?,?,?,?,?,?)",[eventid,name,student_mail,student_number,classtype,seatno])
				cur.execute("UPDATE seats SET status = ? WHERE seat_no = ? AND event_id =?",[1,seatno,eventid])
				conn.commit()
				errorstatus = 0
			else:
				errorstatus = 1
		return render_template('bookingdone.html',errorstatus = errorstatus)


@app.route('/admin',methods=['GET','POST'])
def admin():
	if request.method == 'POST':
		classid = request.form["classid"]
		classtitle = request.form["classtitle"]
		classtype = request.form["classtype"]
		classdate = request.form["classdate"]
		classtime = request.form["classtime"]
		info = request.form["info"]
		location = request.form["location"]
		contact = request.form["contact"]
		lecturer = request.form["lecturer"]
		aboutlecturer = request.form["aboutlecturer"]
		with sqlite3.connect(db) as conn:
			cur = conn.cursor()
			cur.execute("INSERT INTO classes VALUES(?,?,?,?,?,?,?,?)",[classid,classtitle,classtype,classdate,classtime,info,location,contact])
			cur.execute("INSERT INTO lecturers VALUES(?,?,?)",[classid,lecturer,aboutlecturer])
			cur.execute("INSERT INTO seats VALUES(?,?,?,?)",[classid,"seminar","A1",0])
			cur.execute("INSERT INTO seats VALUES(?,?,?,?)",[classid,"seminar","A2",0])
			cur.execute("INSERT INTO seats VALUES(?,?,?,?)",[classid,"seminar","A3",0])
			cur.execute("INSERT INTO seats VALUES(?,?,?,?)",[classid,"seminar","A4",0])
			cur.execute("INSERT INTO seats VALUES(?,?,?,?)",[classid,"lecture","B1",0])
			cur.execute("INSERT INTO seats VALUES(?,?,?,?)",[classid,"lecture","B2",0])
			cur.execute("INSERT INTO seats VALUES(?,?,?,?)",[classid,"lecture","B3",0])
			cur.execute("INSERT INTO seats VALUES(?,?,?,?)",[classid,"lecture","B4",0])
			cur.execute("INSERT INTO seats VALUES(?,?,?,?)",[classid,"lab","C1",0])
			cur.execute("INSERT INTO seats VALUES(?,?,?,?)",[classid,"lab","C2",0])
			cur.execute("INSERT INTO seats VALUES(?,?,?,?)",[classid,"lab","C3",0])
			cur.execute("INSERT INTO seats VALUES(?,?,?,?)",[classid,"lab","C4",0])
			conn.commit()
		return redirect("/home")
	return render_template('admin.html')

@app.route('/lecturer',methods = ['GET','POST'])
def performer():
	if request.method == 'POST':
		classid = request.form["eventid"]
		with sqlite3.connect(db) as conn:
				cur = conn.cursor()
				cur.execute("SELECT * FROM lecturers WHERE event_id = ?",[classid])
				lecturer = cur.fetchall()
	return render_template('lecturer.html',lecturer = lecturer)

@app.route('/search',methods=['GET','POST'])
def search():
	if request.method == 'POST':
		classtitle = request.form["searchbyname"]
		classdate = request.form["searchbydate"]
		classtype = request.form["searchbytype"]
		with sqlite3.connect(db) as conn:
			cur = conn.cursor()
			cur.execute("SELECT * FROM classes WHERE class_title = ? OR class_data = ? OR class_type = ? ORDER BY class_data",[classtitle,classdate,classtype])
			results = cur.fetchall()
	return render_template('search.html',results = results)

if __name__ == '__main__':
    app.run(port=5000,debug = True)
