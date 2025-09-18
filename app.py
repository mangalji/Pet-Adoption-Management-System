from flask import Flask, render_template, request 
from flask import redirect, url_for, session, make_response, flash
from flask_mysqldb import MySQL
import re
import os
import random
from werkzeug.utils import secure_filename
import MySQLdb.cursors
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.exceptions import RequestEntityTooLarge


now = datetime.now()

def generate_otp():
	return str(random.randint(100000,999999))

app = Flask(__name__)

app.secret_key = "supersecretkey"


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'RajMangal'
app.config['MYSQL_PASSWORD'] = 'raj12345'
app.config['MYSQL_DB'] = 'pet_adoption_system_database'

mysql = MySQL(app)

@app.route("/")
def home():
	return render_template("index.html")

@app.route('/registration', methods=['GET','POST'])
def registration():
	username = ''
	email = ''
	phone = ''
	address = ''
	city = ''
	password = ''
	if request.method == 'POST':
		if 'generate_otp' in request.form:
			username = request.form['username']
			print('username: ',username)
			email = request.form['email']
			print('email:', email)
			phone = request.form['phone']
			address = request.form['address']
			city = request.form['city']
			password = request.form['password']
			print('password:',password)
			created_at = datetime.now()

			if not all([username, email, phone, address, city, password]):
				flash("Please fill all field before generating OTP.", "danger")
				return render_template('registration.html',username=username,email=email,phone=phone,address=address,city=city,password=password)
			
			if ( not re.match(r'^(?!\d)(?!.*(.)\1\1)(?!.*__)(?!.*_$)(?!^_)(?=.*[A-Za-z])(?=.*\d)[A-Za-z0-9_]{5,10}$', username)):
				flash("Username must be 5-10 characters in alphanumeric form and also in valid form", "danger")
				return render_template('registration.html',username=username,email=email,phone=phone,address=address,city=city,password=password)
			
			# if not re.match(r'^[a-zA-Z0-9]+[a-zA-Z0-9._-]*@[a-zA-Z0-9-]+\.[a-zA-Z]{2,6}$', email):
			if not re.match(r'^[a-zA-Z][a-zA-Z0-9._-]{0,17}@[a-zA-Z0-9-]+\.[a-zA-Z]{2,6}$', email):
				flash("Invalid email address", "danger")
				return render_template('registration.html', username=username,email=email,phone=phone,address=address,city=city,password=password)
			
			if not re.match(r'^(?!.*(\d)\1{9})(?![6-9]0{9})[6-9]\d{9}$', phone):
				flash("Invalid phone no, Please enter valid phone number","danger")
				return render_template('registration.html',username=username,email=email,phone=phone,address=address,city=city,password=password)
			
			if not re.match(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[^A-Za-z0-9]).{6,12}$",password):
				flash("password must be 6-12 digit long, contain atleast 1 letter, 1 number and 1 special character","danger")
				return render_template('registration.html',username=username,email=email,phone=phone,address=address,city=city)

			if not re.match(r"^[A-Za-z0-9\s,.-]{10,50}$", address):
				flash("Invalid address. Use 10–50 characters with letters, numbers, commas, periods, or hyphens only.", "danger")
				return render_template('registration.html', username=username, email=email, phone=phone, address=address, city=city, password=password)
			
			if not re.match(r"^[A-Za-z\s-]{3,15}$", city):
				flash("Invalid city name. Only letters, spaces, and hyphens are allowed (3–15 characters).", "danger")
				return render_template('registration.html', username=username, email=email, phone=phone, address=address, city=city, password=password)

			cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			cur.execute("SELECT * FROM user_table WHERE name=%s OR email=%s", (username,email))
			existing_user = cur.fetchone()
			cur.close()
		
			if existing_user:
				if existing_user['name'] == username:
					flash("Account with this username already exists","danger")
				elif existing_user['email'] == email:
					flash("Email id is already in use with another account","danger")
				return render_template('registration.html',username=username, email=email, phone=phone, address=address, city=city, password=password) 


			otp = generate_otp()
			session['register_data'] = {'username': username, 'email' : email, 'phone' : phone, 
			'address' : address, 'city' : city, 'password' : password, 'otp' : otp, 'created_at' : created_at
			}

			print(f" OTP for Registration: {otp}")
			flash("OTP sent successfully on terminal","info")
			return render_template('registration.html',username=username,email=email,phone=phone,address=address,city=city,password=password)

		elif request.form.get('otp'):
			entered_otp = request.form['otp']
			data_stored_in_session = session.get('register_data')

			if data_stored_in_session and data_stored_in_session['otp'] == entered_otp:
				username = data_stored_in_session.get('username')
				email = data_stored_in_session.get('email')
				phone = data_stored_in_session.get('phone')
				address = data_stored_in_session.get('address')
				city = data_stored_in_session.get('city')
				password = data_stored_in_session.get('password')
				created_at = data_stored_in_session.get('created_at')

				cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
				hashed_password = generate_password_hash(password)
				cur.execute("INSERT INTO user_table(name,phone,email,password,address,city,created_at) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        		      (username,phone,email,hashed_password,address,city,created_at))
				mysql.connection.commit()
				cur.close()


				session.pop('register_data',None)
				flash("Registration Successful! Please login.", "success")
				return redirect(url_for('login'))
			
			else:
				flash("Invalid OTP","danger")
				return render_template('registration.html',username=username,email=email,phone=phone,address=address,city=city,password=password)
	return render_template("registration.html")


@app.route("/login", methods=['GET', 'POST'])
def login():	
	# print("request form: ",request.form)
	if request.method == 'POST':
		try:
			username = request.form['username']
			email = request.form['email']
			password = request.form['password']
			print("username: ",username)
			print("email: ",email)
			print("password: ",password)
			cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			cur.execute('SELECT * FROM user_table WHERE name = %s AND email = %s',(username,email))
			user = cur.fetchone()

			if user and check_password_hash(user['password'],password):
				session['loggedin'] = True
				session['user_id'] = user['user_id']
				session['name'] = user['name']
				session['city'] = user['city']
				flash("logged in successfully")
				print("logged in successfully")
				return redirect(url_for('dashboard'))
			else:
				flash('Incorrect username/email/password!!')
		except Exception as e:
			print("Error: ",str(e))
	return render_template("login_page.html")


@app.route('/forgot_pass',methods=["POST","GET"])
def forgot_password():
	if request.method == 'POST':
		username = request.form['username']
		email = request.form['email']
		password = request.form['password']

		cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		
		cur.execute("SELECT * FROM user_table WHERE name=%s AND email=%s AND name=%s",(username,email,username))
		user = cur.fetchone()

		if user:

			if not re.match(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[^A-Za-z0-9]).{6,12}$",password):
				flash("password must be 6-12 digit long, contain atleast 1 letter, 1 number and 1 special character","danger")
				return render_template('forgot_password.html',username=username,email=email)

			hashed_password = generate_password_hash(password)
			cur.execute("UPDATE user_table SET password=%s WHERE name=%s AND email=%s AND name=%s",(hashed_password,username,email,username))
			mysql.connection.commit()
			flash("password reset  successfully")

		else:
			flash("No user found with these details")
			return render_template('forgot_password.html',username=username,email=email)
		
		cur.close()
		return redirect(url_for('forgot_password'))

	return render_template('forgot_password.html')

@app.route("/dash")
def dashboard():
	if 'user_id' not in session:
		return redirect(url_for('login'))

	if 'name' in session:
		cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cur.execute("""SELECT cr.request_id, cr.status, p.pet_id, p.category AS pet_category, u.user_id AS adopter_id,
		u.name AS adopter_name, u.phone AS adopter_phone, u.city AS adopter_city FROM call_request_table cr
		JOIN pet_table p ON p.pet_id = cr.pet_id JOIN user_table u ON u.user_id = cr.user_id
		WHERE p.user_id = %s AND cr.status IN  ('pending', 'accepted') AND NOT EXISTS(SELECT 1 FROM transaction_table t WHERE t.request_id = cr.request_id AND t.status = 'completed') ORDER BY cr.request_id DESC""",(session['user_id'],))
		
		call_requests = cur.fetchall()
		
		cur.close()
		return render_template(
			"dashboard.html",
			username=session.get("name"),
			call_requests=call_requests
		)

@app.route('/logout')
def logout():
	session.clear()
	response = make_response(redirect(url_for('login')))
	response.headers['Cache-Control'] = 'no-cache, no_store, must_revalidate'
	response.headers['Pragma'] = 'no-cache'
	response.headers['Expires'] = '0'
	return response
	# return'<script>window.history.forward()</script>'

UPLOAD_FOLDER = os.path.join('static','uploads') 
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

ALLOWED_EXTENSIONS = {'png','jpg','jpeg'}

def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    flash("File is too large. Max size allowed is 2 MB.", "danger")
    return redirect(url_for('donate'))


@app.route('/donate', methods=['GET', 'POST'])
def donate():
	if 'user_id' not in session:
		return redirect(url_for('login'))

	if request.method == 'POST':
		pet_category = request.form['pet_category']
		pet_breed = request.form['pet_breed']
		pet_name = request.form['pet_name']
		pet_age = request.form['pet_age']
		pet_weight = request.form['pet_weight']
		pet_desc = request.form['pet_desc']
		added_at = datetime.now()
		pet_image = request.files['pet_image']

		if pet_image and allowed_file(pet_image.filename):
			filename = secure_filename(pet_image.filename)
			filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
			os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
			pet_image.save(filepath)
			image_db_path = f"uploads/{filename}"
		else:
			image_db_path = None
			flash("please upload valid image","danger")
			return redirect(url_for('donate'))

		if not all([pet_name,pet_category,pet_breed,pet_age,pet_weight,pet_desc,pet_image]):
			flash(f"{session.get('name')}Please fill all field.")
			return render_template('donate.html',pet_name=pet_name,pet_category=pet_category,pet_breed=pet_breed,pet_age=pet_age,pet_weight=pet_weight,pet_desc=pet_desc,pet_image=pet_image)

		if not re.match(r'^[A-Za-z0-9]+$', pet_name) or re.search(r'(.)\1\1', pet_name):
			flash("Pet name must be valid.","danger")
			return render_template('donate.html',pet_category=pet_category,pet_breed=pet_breed,pet_age=pet_age,pet_weight=pet_weight,pet_desc=pet_desc,pet_image=pet_image)

		if not (len(pet_name) <=12):
			flash("pet's name would be maximum up to 12 characters and valid.","danger")
			return render_template('donate.html',pet_category=pet_category,pet_breed=pet_breed,pet_age=pet_age,pet_weight=pet_weight,pet_desc=pet_desc,pet_image=pet_image) 
		
		if not re.match(r'^[0-9]{1,4}$', pet_age) and int(pet_age) > 0 and int(pet_age) <= 1000:
			flash("Pet age must be valid", "danger")
			return render_template('donate.html',pet_category=pet_category,pet_breed=pet_breed,pet_name=pet_name,pet_weight=pet_weight,pet_desc=pet_desc,pet_image=pet_image)

		if not re.match(r'^[0-9]{1,4}(\.[0-9]{1,2})?$', pet_weight):
			flash("Pet weight must be a valid", "danger")
			return render_template('donate.html',pet_category=pet_category,pet_breed=pet_breed,pet_name=pet_name,pet_age=pet_age,pet_desc=pet_desc)

		cur = mysql.connection.cursor()
		cur.execute("""
			INSERT INTO pet_table
			(name,category,breed,age,weight,pet_description,added_at,image, user_id) 
			VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
			""",(pet_name,pet_category,pet_breed,pet_age,
				pet_weight,pet_desc,added_at,
				image_db_path, session.get('user_id')))
		mysql.connection.commit()
		return redirect(url_for('dashboard'))

	return render_template("donate.html",username=session.get("name"))

@app.route('/adopt')
def adopt():

	if 'user_id' not in session:
		return redirect(url_for('login'))
	
	cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cur.execute("""SELECT p.*,u.name AS donor_name,(SELECT cr.status FROM call_request_table cr WHERE cr.pet_id = p.pet_id AND cr.user_id = %s ORDER BY cr.request_id DESC LIMIT 1) AS request_status
	FROM pet_table p JOIN user_table u ON u.user_id = p.user_id WHERE p.user_id != %s AND p.pet_id NOT IN 
	(SELECT pet_id FROM transaction_table WHERE status = 'completed')""",(session['user_id'],session['user_id']))
	
	pets = cur.fetchall()
	cur.close()

	return render_template('adopt.html',username = session.get('name'), city=session.get("city"), pets=pets)

@app.route('/create_call_request/<int:pet_id>',methods=['POST'])
def create_call_request(pet_id):
	if 'user_id' not in session:
		return redirect(url_for('login'))
		
	cur = mysql.connection.cursor()

	cur.execute('Insert into call_request_table(pet_id,user_id,status) VALUES (%s,%s,%s)',
			 (pet_id, session['user_id'],'pending'	))
	mysql.connection.commit()
	cur.close()
	return redirect(url_for('adopt'))

@app.route('/cancel_request/<int:pet_id>',methods=['POST'])
def cancel_request(pet_id):
	if 'user_id' not in session:
		return redirect(url_for('login'))

	cur = mysql.connection.cursor()

	cur.execute("DELETE FROM call_request_table WHERE pet_id = %s AND user_id = %s",(pet_id,session['user_id']))
	mysql.connection.commit()
	cur.close()

	flash("Adoption request cancelled !","info")
	return redirect(url_for('adopt'))

@app.route('/call_request/<int:request_id>/decide',methods=['POST'])
def decide_call_request(request_id):

	if 'user_id' not in session:
		return redirect(url_for('login'))

	decision = request.form.get('decision')

	cur = mysql.connection.cursor()
	
	cur.execute("UPDATE call_request_table SET status=%s WHERE request_id=%s",(decision,request_id))
	
	mysql.connection.commit()
	
	cur.close()
	return redirect(url_for('dashboard'))

@app.route('/transaction_complete/<int:request_id>',methods=['POST'])
def complete_transaction(request_id):
	if 'user_id' not in session:
		return redirect(url_for('login'))


	cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cur.execute("""SELECT cr.pet_id, cr.user_id AS adopter_id 
		FROM call_request_table cr JOIN pet_table p ON p.pet_id = cr.pet_id 
		WHERE cr.request_id=%s AND p.user_id=%s""",(request_id,session['user_id']))
	
	row = cur.fetchone()
	
	if row:
		cur.execute("""INSERT INTO transaction_table(request_id, pet_id, user_id, status)
			VALUES (%s,%s,%s,%s)""",(request_id,row['pet_id'],row['adopter_id'],'completed'))
		
		mysql.connection.commit()
	
	cur.close()
	return redirect(url_for('dashboard'))

@app.route('/profile')
def profile():
	if 'user_id' not in session:
		return redirect(url_for('login'))

	cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	# cur.execute("""
	# 		 SELECT p.*, CASE WHEN t.pet_id IS NOT NULL THEN 'donated' ELSE 'pending'
	# 		 END as status, CASE 
    #              WHEN t.pet_id IS NOT NULL THEN u.name
    #              ELSE NULL 
    #            END as adopted_by FROM pet_table p
    #     LEFT JOIN transaction_table t ON p.pet_id = t.pet_id AND t.status = 'completed'
    #     LEFT JOIN user_table u ON t.user_id = u.user_id
    #     WHERE p.user_id = %s
    #     ORDER BY 
    #       CASE WHEN t.pet_id IS NOT NULL THEN 1 ELSE 0 END,
    #       p.added_at DESC
    # """, (session['user_id'],))
	cur.execute("""SELECT p.*, IF(t.pet_id IS NOT NULL, 'donated', 'pending') as status,u.name as adopted_by
				FROM pet_table p LEFT JOIN transaction_table t ON p.pet_id = t.pet_id AND t.status = 'completed'
				LEFT JOIN user_table u ON t.user_id = u.user_id
				WHERE p.user_id = %s ORDER BY (t.pet_id IS NOT NULL), p.added_at DESC""",(session['user_id'],))
	# cur.execute("""SELECT p.*, t.user_id AS adopted_by, t.status AS transaction_status 
	# 		 FROM pet_table p LEFT JOIN transaction_table t ON 
	# 	p.pet_id = t.pet_id WHERE p.user_id = %s""", (session['user_id'],))
	donated_pets = cur.fetchall()
	# print(donated_pets)
	# cur.execute("SELECT * FROM pet_table WHERE user_id =%s",(session['user_id'],))
	# listed_pets = cur.fetchall()
	# adopters = []
	# for pet in listed_pets:
	# 	pet_id = pet['pet_id']

	# 	cur.execute("SELECT user_id FROM transaction_table WHERE pet_id=%s",(pet_id,))
	# 	adopted_by = cur.fetchall()
	# 	adopters.append(adopted_by)
	# # donated_pets 
	# print(adopters)
	# adoptions = []
	# extract_tuple = [tup for tup in adopters]
	# for tup in extract_tuple:
		
	# 	for dictionary in tup:
	# 		user_id = dictionary['user_id']
	# 		adoptions.append(user_id)
	# 		print(user_id)

	# cur.execute("SELECT * FROM transaction_table WHERE user_id = %s",(session['user_id'],))
	# donated_pets = cur.fetchall()

	# listed_pets += donated_pets
	# print(type(listed_pets))
	# print(listed_pets)
	# print(len(listed_pets	))
	# listed_pets.update(donated_pets)

	cur.execute(""" SELECT p.*, t.status FROM transaction_table t JOIN pet_table p ON t.pet_id = p.pet_id
		WHERE t.user_id = %s AND (t.status = 'completed' or t.status = 'pending') """, (session['user_id'],))
	
	adopted_pets = cur.fetchall()

	cur.execute("SELECT * FROM user_table WHERE user_id=%s", (session['user_id'],))
	user = cur.fetchone()
	cur.close()

	return render_template("profile.html",username=user['name'],city=user['city'],bio='pet lover',
		donated_pets=donated_pets,adopted_pets=adopted_pets) #adoptions = adoptions)

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
	if 'user_id' not in session:
		return redirect(url_for('login'))	
	
	cur = mysql.connection.cursor()
	cur.execute("SELECT name, email, phone, address, city FROM user_table WHERE user_id = %s", (session['user_id'],))
	user = cur.fetchone()
	cur.close()

	if request.method == 'POST':
		
		username = request.form.get('name')
		# email = request.form.get('email')
		phone = request.form.get('phone')
		address = request.form.get('address')
		city = request.form.get('city')

		if not all([username, phone, address, city]):
			flash("Please fill all field before generating OTP.", "danger")
			return render_template('edit_profile.html',username=username,phone=phone,address=address,city=city,user=user)
		
		if ( not re.match(r'^(?!\d)(?!.*(.)\1\1)(?!.*__)(?!.*_$)(?!^_)(?=.*[A-Za-z])(?=.*\d)[A-Za-z0-9_]{5,10}$', username)):
			flash("Username must be 5-10 characters in alphanumeric form and also in valid form", "danger")
			return render_template('edit_profile.html',username=username,phone=phone,address=address,city=city,user=user)
		
		# email_regex = r"^(?!.*\.\.)(?!.*\.$)[a-zA-Z0-9._%+-]{3,15}@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
		# if (not re.match(email_regex,email) or email.count('@') !=1 or email.startswith('@') or len(email.split('@')[0]) > 15) :
		# 	flash("Invalid email address", "danger")
		# 	return render_template('edit_profile.html', username=username,email=email,phone=phone,address=address,city=city,user=user)
		
		if not re.match(r'^(?!.*(\d)\1{9})(?![6-9]0{9})[6-9]\d{9}$', phone):
			flash("Invalid phone no, Please enter valid phone number","danger")
			return render_template('edit_profile.html',username=username,phone=phone,address=address,city=city,user=user)
		
		if not re.match(r"^[A-Za-z0-9\s,.-]{10,50}$", address):
			flash("Invalid address. Use 10–50 characters with letters, numbers, commas, periods, or hyphens only.", "danger")
			return render_template('edit_profile.html', username=username, phone=phone, address=address, city=city,user=user)
		
		if not re.match(r"^[A-Za-z\s-]{3,15}$", city):
			flash("Invalid city name. Only letters, spaces, and hyphens are allowed (3-15 characters).", "danger")
			return render_template('edit_profile.html', username=username, phone=phone, address=address, city=city,user=user)

		cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cur.execute("SELECT * FROM user_table WHERE name=%s", (username,))
		existing_user = cur.fetchone()
		cur.close()

		if existing_user:
			if existing_user['name'] == username:
				flash("Account with this username already exists","danger")
			# elif existing_user['phone'] == phone:
			# 	flash("phone no. is already in use with another account","danger")
			return render_template('edit_profile.html',username=username,phone=phone,address=address,city=city,user=user)

		cur = mysql.connection.cursor()
		cur.execute("UPDATE user_table SET name = %s,phone=%s,address=%s,city=%s WHERE user_id=%s",
			(username,phone,address,city,session['user_id']))
		mysql.connection.commit()
		cur.close()

		session['name'] = username
		# session['email'] = email
		session['phone'] = phone
		session['address'] = address
		session['city'] = city

		flash("Profile updated successfully","success")
		return redirect(url_for('profile'))

	return render_template("edit_profile.html", user=user)

@app.route('/view_pet/<int:pet_id>')
def view_pet(pet_id):
	if 'user_id' not in session:
		return redirect(url_for('login'))

	cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

	cur.execute("""SELECT p.*, u.name AS donor_name, u.city AS donor_city from pet_table p
		join user_table u on p.user_id = u.user_id WHERE p.pet_id = %s""",(pet_id,))

	pet = cur.fetchone()

	if not pet:
		flash("Pet not found","danger")
		return redirect(url_for('profile'))

	cur.execute("""SELECT t.*, a.name AS adopter_name, a.city AS adopter_city, a.phone AS adopter_phone
		from transaction_table t join user_table a on t.user_id = a.user_id WHERE t.pet_id = %s
		AND t.status = 'completed'""",(pet_id,))
	transaction = cur.fetchone()
	cur.close()

	return render_template('view_pet.html',pet=pet, transaction = transaction)

@app.route('/delete_pet/<int:pet_id>', methods=['POST'])
def delete_pet(pet_id):

	if 'user_id' not in session:
		return redirect(url_for('login'))

	cur = mysql.connection.cursor()

	cur.execute("DELETE FROM call_request_table WHERE pet_id = %s",(pet_id,))
	mysql.connection.commit()

	cur.execute("DELETE FROM pet_table WHERE pet_id = %s AND user_id = %s",(pet_id,session['user_id']))
	mysql.connection.commit()
	cur.close()
	flash("pet deleted successfully","success")
	return redirect(url_for('profile'))

@app.route('/support')
def support():
	return render_template("customer_support.html",username=session.get('name'),city=session.get('city'))

@app.route('/adopter_profile/<int:adopterid>')
def adopter_profile(adopterid):

	if 'user_id' not in session:
		return redirect(url_for('login'))
	
	cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

	cur.execute("SELECT * from user_table WHERE user_id=%s",(adopterid,))
	user_data = cur.fetchone()

	if not user_data:
		cur.close()
		return "Adopter not found",404

	cur.execute(""" SELECT p.*, t.user_id AS adopted_by FROM pet_table p JOIN transaction_table t ON 
	p.pet_id = t.pet_id WHERE p.user_id = %s""", (adopterid,))

	donated_pets = cur.fetchall()

	cur.execute(""" SELECT p.*, t.status FROM transaction_table t JOIN pet_table p ON t.pet_id = p.pet_id
		WHERE t.user_id = %s """, (adopterid,))
	
	adopted_pets = cur.fetchall()

	cur.close()

	return render_template('other_person_profile.html',username=user_data['name'],city=user_data['city'],donated_pets=donated_pets,adopted_pets=adopted_pets)


if __name__ == "__main__":
	app.run()






















































































		# flash("No update request found!")
		# flash(f"{field.capitalize()} updated successfully!")
		# flash("Invalid OTP. Please try again.")
		# allowed_fields = ['name','email','phone','address','city']
		# if field not in allowed_fields:
		# 	flash('Invalid field','danger')
		# 	return redirect(url_for('edit_profile'))
