# Pet Wala – Pet Adoption System
<!-- This is my Pet Adoption project repository -->

## Description:

Pet wala is a web based application where users can list his pets for donate and adopt the pets which are listed by another user. And it's absolutely complete free plateform.

---

## Features:
- User account Creation
- User account login/logout
- Pet listing 
- Pet donation
- Pet adoption
- Call request generation feature
- Transaction tracking
- User edit profile

---

## Tech Stack:
- FrontEnd: HTML5, CSS3, Javascript
- BackEnd: Python
- BackEnd Framework: Flask
- Database: MySQL

---

## Installation:

```bash
git clone https://github.com/mangalji/Pet-Adoption-Management-System
cd Pet-Adoption-Management-System
```
### create your database :

```
create database <your database name>;
use <your database name>;
CREATE TABLE `user_table` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `phone` varchar(12) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `user_desc` varchar(255) DEFAULT NULL,
  `active_session` varchar(255) DEFAULT NULL,
  `last_active` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `unique_username` (`name`),
  UNIQUE KEY `unique_email` (`email`)
);

CREATE TABLE `pet_table` (
  `pet_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `category` varchar(255) DEFAULT NULL,
  `breed` varchar(255) DEFAULT NULL,
  `age` varchar(5) DEFAULT NULL,
  `weight` varchar(5) DEFAULT NULL,
  `pet_description` varchar(255) DEFAULT NULL,
  `added_at` datetime(6) DEFAULT NULL,
  `image` varchar(255) DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  PRIMARY KEY (`pet_id`),
  KEY `fk_user_id` (`user_id`),
  CONSTRAINT `fk_user_id` FOREIGN KEY (`user_id`) REFERENCES `user_table` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_user_pet_table` FOREIGN KEY (`user_id`) REFERENCES `user_table` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE `call_request_table` (
  `request_id` int NOT NULL AUTO_INCREMENT,
  `pet_id` int DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  `status` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`request_id`),
  KEY `pet_id` (`pet_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `call_request_table_ibfk_1` FOREIGN KEY (`pet_id`) REFERENCES `pet_table` (`pet_id`),
  CONSTRAINT `call_request_table_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user_table` (`user_id`)
);

CREATE TABLE `transaction_table` (
  `tr_id` int NOT NULL AUTO_INCREMENT,
  `request_id` int DEFAULT NULL,
  `pet_id` int DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  `status` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`tr_id`),
  KEY `request_id` (`request_id`),
  KEY `pet_id` (`pet_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `transaction_table_ibfk_1` FOREIGN KEY (`request_id`) REFERENCES `call_request_table` (`request_id`),
  CONSTRAINT `transaction_table_ibfk_2` FOREIGN KEY (`pet_id`) REFERENCES `pet_table` (`pet_id`),
  CONSTRAINT `transaction_table_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `user_table` (`user_id`)
);

CREATE TABLE `notification_table` (
  `notification_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `message` text NOT NULL,
  `notification_type` varchar(50) NOT NULL,
  `is_read` tinyint(1) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`notification_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `notification_table_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user_table` (`user_id`) ON DELETE CASCADE);

```

### create the file .env and write the code :

```
SECRET_KEY = "your_secret_key_here"
HOST = "your_host_name" #generally in local system host name is localhost
USER = "your database user name"
PASSWORD = "your database password"
DB = "your database name"
```


```
pip install -r requirements.txt
flask run
```

--- 

## Database Tables:
- Users
- Pets
- Call_Requests
- Transactions 

## Future Improvements:
- AI pet recommended system
- Chat between adopter and owner
- Live monitoring of the process

---

## Developer Name:
**RAJ MANGAL**
