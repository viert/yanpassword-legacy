#!/usr/bin/env python

from store import Store
from passdb import PassDB
import crypter
import getpass
import sys
import tempfile
import hashlib

PROMPT = "\nYanPwd> "
store = None
db = None

while True:
  sys.stdout.write("\nYandex login: ")
  ylogin = sys.stdin.readline().strip()
  ypass = getpass.getpass(prompt="Password: ")
  
  try:
    store = Store(ylogin, ypass)
    break
  except:
    print "Authorization error, wrong login or password?"

print "Loading CryptDB file"
dbfile = tempfile.NamedTemporaryFile()

r = store.load()
if r["status"] == "200":
  while True:
    cdbpass = getpass.getpass("Enter CryptDB password: ")
    key = hashlib.sha256(cdbpass).digest()
    crypter.decrypt_file(key, store.tmpfile.name, dbfile.name)
    try:
      db = PassDB(dbfile.name)
      break
    except:
      print "CryptDB file is invalid, wrong password?"
elif r["status"] == "404":
  print "Remote CryptDB file not found, creating"
  db = PassDB(dbfile.name)
elif r["status"] == "403":
  print "Error loading CryptDB file, probably Yandex.Disk is not activated for your account. Visit disk.yandex.com to activate"
  exit(2)
else:
  print "Error loading CryptDB file"
  print r
  exit(255)

# Command-Line Loop
while True:
  sys.stdout.write(PROMPT)
  comm = sys.stdin.readline()
  if len(comm) == 0:
    sys.stdout.write("\nReally exit? ")
    if sys.stdin.readline().strip().lower() == "y":
      exit(0)
  else:
    args = comm.strip().split()
    cmd = args[0]
    if cmd == 'list':
      services = db.list()
      for service in services:
        print service
    elif cmd == 'get':
      if len(args) != 2:
        print "Usage: get <servicename>"
        continue
      service = db.get(args[1])
      print "Service: " + service["service"]
      print "Login: " + service["login"]
      print "Password: " + service["password"]
      print "Comment: " + service["comment"]
    elif cmd == 'set':
      if len(args) != 2:
        print "Usage: set <servicename>"
        continue
      print
      sys.stdout.write("Login: ")
      login = sys.stdin.readline().strip()
      sys.stdout.write("Password: ")
      password = sys.stdin.readline().strip()
      sys.stdout.write("Comment: ")
      comment = sys.stdin.readline().strip()
      db.set(args[1], login, password, comment)
    elif cmd == 'delete':
      if len(args) != 2:
        print "Usage: delete <servicename>"
        continue
      service = db.delete(args[1])
    elif cmd == 'exit':
      exit(0)
    elif cmd == 'save':
      cdbpass = getpass.getpass(prompt='Enter password to encrypt file: ')
      cdbpasschk = getpass.getpass(prompt='And one more time the same please: ')
      if cdbpass != cdbpasschk:
        print "Passwords do not match, file saving aborted"
        continue
      key = hashlib.sha256(cdbpass).digest()
      crypter.encrypt_file(key, dbfile.name, store.tmpfile.name)
      store.save()
      
