# access_control
It is a command line app that let's you  manage and view users, set roles, and grant access to resources

This document outlines the following aspects:
1. Assumptions made for this project
2. How to setup this project
3. How to run this project
4. Sample run

## Assumptions
   - Below roles are assumed:
     RWD role - For Read, Write and Delete access
     R role - For Read access
     W role - For Write access
     D role - For Delete access
     RW role - For Read and Write access
     RD role - For Read and Delete access
     WD role - For Write and Delete access

   - It is assumed that the user can have multiple roles but at different points in time.
     For example, the user can have `R` role yesterday, but is assigned `RD` role today, but not 2 roles at the same time.

   - I have used sha256 hashes for storing passwords.

   - It is assumed that it is role which will define what kind of access you have to the resource,
     e.g. if your current role is RWD, then you can READ, WRITE and DELETE any of the resources.
     
   - I have used ubuntu 18.04 for dev.

   - I have used sqlite3. Please install relevant packages in your env.
     Should be easy to download and install relevant packages.

   - Admin user is added. email_id: admin@accesscontrol.com, password: admin123
   
   - Resources are added. CPU and MEMORY are the ones which are in db. Feel free to add more.
     Install sqlitebrowser for easier db related handling.

   - DB SCHEMA (sqlite3):
     - CREATE TABLE ROLE(
       ID INT PRIMARY KEY NOT NULL,
       NAME CHAR(32) NOT NULL);
     - CREATE TABLE USER_ROLE(
       user_id INTEGER,
       role_id INTEGER,
       PRIMARY KEY (user_id, role_id) 
       FOREIGN KEY (user_id) 
       REFERENCES USER (ID)
        ON DELETE CASCADE
        ON UPDATE NO ACTION,
       FOREIGN KEY (role_id)
       REFERENCES ROLE (id)
        ON DELETE CASCADE
        ON UPDATE NO ACTION
       );
     - CREATE TABLE sqlite_sequence(name,seq);
     - CREATE TABLE IF NOT EXISTS "USER" (
	    "ID"	INTEGER NOT NULL,
	    "FIRST_NAME"	CHAR(32),
	    "LAST_NAME"	CHAR(32),
	    "EMAIL"	CHAR(50) UNIQUE,
	    PRIMARY KEY("ID" AUTOINCREMENT)
       );

     - CREATE TABLE IF NOT EXISTS "AUTH" (
	    "ID"	INTEGER NOT NULL,
	    "user_id"	INTEGER,
	    "password"	CHAR(32),
	    FOREIGN KEY("user_id") REFERENCES "USER"("ID") ON DELETE CASCADE ON UPDATE NO ACTION,
	    PRIMARY KEY("ID" AUTOINCREMENT)
       );

     - CREATE TABLE IF NOT EXISTS "RESOURCE" (
	    "ID"	INTEGER NOT NULL,
	    "NAME"	CHAR(32) NOT NULL,
	    PRIMARY KEY("ID" AUTOINCREMENT)
       );

## How to setup this project
   - Create a python3.7 virtualenv and activate it
   - pip install -r requirements.txt (only one package to install - docopt for reading command line args)
   - user.py takes care of user management
   - db.py takes care of db related tasks
   - auth.py takes care of authentication of users
   - access.py is the file to invoke this app

## How to run this project
   - From project root directory. hit python access.py

## Sample run
```
(access) anindya@anindya-ThinkPad-X1-Carbon-7th:~/practice/role_based_AC/access_control$ python access.py 
**************************************************
hi! you are logged in as admin
press 1 for login as another user
press 2 for create user
press 3 for edit role
Press anything else to quit!
Enter your choice: 1
Enter your email_id: a
Enter your password: 
**************************************************
hi! you are logged in as a
press 1 for login as another user
press 2 for view roles
press 3 for access resource
Press anything else to quit!
Enter your choice: 2
Available roles are ['RWD', 'R', 'W', 'D', 'RW', 'RD', 'WD']
**************************************************
hi! you are logged in as a
press 1 for login as another user
press 2 for view roles
press 3 for access resource
Press anything else to quit!
Enter your choice: 3
Enter resource name to access: CPU
Available access_types to choose are ['READ', 'WRITE', 'DELETE']
Enter access type: READ
You are allowed READ access to resource: CPU
**************************************************
hi! you are logged in as a
press 1 for login as another user
press 2 for view roles
press 3 for access resource
Press anything else to quit!
Enter your choice: 3
Enter resource name to access: CPU
Available access_types to choose are ['READ', 'WRITE', 'DELETE']
Enter access type: WRITE
[2021-05-17 02:37:20,200] [INFO] [user] [95] - Your role does not permit you WRITE access to resource CPU
**************************************************
hi! you are logged in as a
press 1 for login as another user
press 2 for view roles
press 3 for access resource
Press anything else to quit!
Enter your choice: 4
Thank you! Hope to see you again.
**************************************************
```
