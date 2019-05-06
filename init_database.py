#!/usr/bin/env python

import sqlite3
import os

s=input("Warn: This will drop the database (of training data inventory)! Type 'Yes' if you are sure to do that.\n")
if(s != "Yes"):
    print("you didn't re-generate the database")
    exit(0)

if(not os.path.isdir("instance")):
    os.mkdir("instance")

conn = sqlite3.connect("instance/data.db")
with open("schema.sql", "r") as f:
    conn.executescript(f.read())
    conn.commit()
    print("instance/data.db is re-generated")
