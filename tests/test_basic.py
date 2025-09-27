# from flask import get_flashed_messages
from bs4 import BeautifulSoup
from io import BytesIO
from flask import session

def test_home_page(client):
	response = client.get("/")
	assert response.status_code == 200
	assert b"Registration",b"" in response.data

def test_login_invalid(client):
	response = client.post('/login',data={
		"username":"RajMangal",
		"email":"raj@@gmail.@.com",
		"password":"raj12345"
		},follow_redirects = True)
	assert response.status_code == 200
	assert b"Incorrect username/email/password!!" in response.data

# def test_login_valid(client):
# 	response = client.post('/login', data={
# 		"username":"raj123",
# 		"email":"raj@gmail.com",
# 		"password":"raj@123"
# 		},follow_redirects=True)
# 	assert response.status_code == 200
# 	assert b"logged in succeesfully" in response.data

def test_register_invalid_username(client):
    response = client.post('/registration', data={
        "username": "ab12",
        "email": "test@gmail.com",
        "phone": "8827598493",
        "address": "Some address 123",
        "city": "TestCity",
        "password": "Mangal@123",
        "generate_otp":"Generate OTP"
    }, follow_redirects=True)
    assert response.status_code == 200
    soup = BeautifulSoup(response.data,'html.parser')
    flashes = [div.text.strip() for div in soup.find_all("div",class_="flash-messages")]

    assert any("Invalid! Username must be 5-10 characters in alphanumeric form and also in valid form" in msg for msg in flashes)


def test_register_invalid_email(client):
	response = client.post('/registration', data={
        "username": "raj12345",  
        "email": "test@gmail@.gm.com",
        "phone": "8827598493",
        "address": "Some address 123",
        "city": "TestCity",
        "password": "Mangal@123",
        "generate_otp":"Generate OTP"
    }, follow_redirects=True)
	assert response.status_code == 200
	soup = BeautifulSoup(response.data, "html.parser")
	flashes = [div.text.strip() for div in soup.find_all("div",class_="flash-messages")]
	assert any("Invalid! email address" in msg for msg in flashes)

def test_register_invalid_phone(client):
	response = client.post('/registration', data={
        "username": "raj12345",  
        "email": "test@gmail.com",
        "phone": "6666666666",
        "address": "Some address 123",
        "city": "TestCity",
        "password": "Mangal@123",
        "generate_otp":"Generate OTP"
    }, follow_redirects=True)
	assert response.status_code == 200
	soup = BeautifulSoup(response.data, "html.parser")
	flashes = [div.text.strip() for div in soup.find_all("div",class_="flash-messages")]
	assert any("Invalid! phone no, Please enter valid phone number" in msg for msg in flashes)

def test_register_invalid_password(client):
	response = client.post('/registration', data={
        "username": "raj12345",  
        "email": "test@gmail.com",
        "phone": "9876543210",
        "address": "some address 123",
        "city": "testCity",
        "password": "testuser",
        "generate_otp":"Generate OTP"
    }, follow_redirects=True)
	assert response.status_code == 200
	soup = BeautifulSoup(response.data, "html.parser")
	flashes = [div.text.strip() for div in soup.find_all("div", class_ = "flash-messages")]
	assert any("Invalid! password must be 6-12 digit long, contain atleast 1 letter, 1 number and 1 special character" in msg for msg in flashes)

# def test_register_valid_all_field(client):
# 	response = client.post('/registration',data={
# 		"username":"raj12345",
# 		"email":"test@gmail.com",
# 		"phone":"9876522102",
# 		"address":"somewhere 232",
# 		"city":"testcity",
# 		"password":"test@123",
# 		"generate_otp":"Generate OTP"
# 		}, follow_redirects=True)
# 	assert response.status_code == 200
# 	soup = BeautifulSoup(response.data, "html.parser")
# 	flashes = [div.text.strip() for div in soup.find_all("div", class_="flash-messages")]
# 	assert any("OTP sent successfully on terminal" in msg for msg in flashes)

def test_donate_pet_age_invalid(client):

	with client.session_transaction() as sess:
		sess['user_id'] = 1
		sess['name'] = 'TestUser'

	response = client.post('/donate', data={
		"pet_category" : "cow",
		"pet_breed":"sahiwal",
		"pet_name":"bansuri",
		"pet_age":"10000",
		"pet_weight":"100000",
		"pet_desc":"aaaaaaaaaaaaaaaaaaaa",
		"pet_image":(BytesIO(b"dummy image"), "test.jpg")
		}, content_type='multipart/form-data' ,follow_redirects=True)
	assert response.status_code == 200
	# print(response.data.decode())
	# assert b"Pet age must be valid" in response.data
	soup = BeautifulSoup(response.data, "html.parser")
	flashes = [div.text.strip() for div in soup.find_all("div",class_="flash")]
	assert any("Pet age must be valid" in msg for msg in flashes)

	# print(response.data.decode())

def test_donate_pet_weight_invalid(client):

	with client.session_transaction() as sess:
		sess['user_id'] = 1
		sess['name'] = 'TestUser'

	response = client.post('/donate', data={
		"pet_category" : "cow",
		"pet_breed":"sahiwal",
		"pet_name":"bansuri",
		"pet_age":"100",
		"pet_weight":"100000",
		"pet_desc":"aaaaaaaaaaaaaaaaaaaa",
		"pet_image":(BytesIO(b"dummy image"), "test.jpg")
		}, content_type='multipart/form-data' ,follow_redirects=True)
	
	assert response.status_code == 200
	soup = BeautifulSoup(response.data, "html.parser")
	flashes = [div.text.strip() for div in soup.find_all("div", class_="flash")]
	assert any("Pet weight must be a valid" in msg for msg in flashes)

def test_donate_pet_image_invalid(client):

	with client.session_transaction() as sess:
		sess['user_id'] = 1
		sess['name'] = 'TestUser'

	response = client.post('/donate', data={
		"pet_category" : "cow",
		"pet_breed":"sahiwal",
		"pet_name":"bansuri",
		"pet_age":"100",
		"pet_weight":"100000",
		"pet_desc":"aaaaaaaaaaaaaaaaaaaa",
		"pet_image":(BytesIO(b"dummy image"), "test.mp4")
		}, content_type='multipart/form-data' ,follow_redirects=True)
	
	assert response.status_code == 200
	soup = BeautifulSoup(response.data, "html.parser")
	flashes = [div.text.strip() for div in soup.find_all("div", class_="flash")]
	assert any("please upload valid image" in msg for msg in flashes)


def test_donate_pet_successfull(client):
	with client.session_transaction() as sess:
		sess['user_id'] = 1
		sess['name'] = 'TestUser'
	response = client.post()