# access_control
It is a command line app that let's you  manage and view users, set roles, and grant access to resources

This document outlines the following aspects:
1. Assumptions made for this project
2. How to setup this project
3. How to run this project

Assumptions
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

How to setup this project
   - Create a python3.7 virtualenv and activate it
   - pip install -r requirements.txt (only one package to install - docopt for reading command line args)
   - db.py takes care of db related tasks
   - auth.py takes care of authentication of users
   - access.py is the file to invoke this app

How to run this project
   - From project root directory. hit python access.py
