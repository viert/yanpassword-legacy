#!/usr/bin/env python

from store import Store
from passdb import PassDB
import crypter
import getpass
import sys
import tempfile
import hashlib
import cmd

store = None
db = None

class CmdLine(cmd.Cmd):

  prompt = "YanPwd> "
  
  def do_list(self, arg):
    services = db.list()
    for service in services:
      print service

  def do_ls(self, arg):
    self.do_list(arg)

  def do_get(self, arg):
    if arg.strip() == "":
      print "Usage: get|cat <servicename>"
      return
    service = db.get(arg)
    if service is None:
      print "Service '" + arg + "' not found"
      return
    print
    print "Service:  " + service["service"]
    print "Login:    " + service["login"]
    print "Password: " + service["password"]
    print "Comment:  " + service["comment"]
    print

  def do_delete(self, arg):
    if arg.strip() == "":
      print "Usage: delete|rm <servicename>"
      return
    service = db.delete(arg)

  def complete_get(self, text, line, begidx, endidx):
    vocab = db.list()
    opts = [x for x in vocab if x.startswith(text)]
    return opts

  def complete_cat(self, text, line, begidx, endidx):
    return self.complete_get(text, line, begidx, endidx)
  
  def complete_rm(self, text, line, begidx, endidx):
    return self.complete_get(text, line, begidx, endidx)
  
  def complete_delete(self, text, line, begidx, endidx):
    return self.complete_get(text, line, begidx, endidx)

  def do_cat(self, arg):
    self.get(arg)

  def do_EOF(self, arg):
    sys.stdout.write("\nReally exit (y/n)? ")
    if sys.stdin.readline().strip().lower() == "y":
      sys.exit()

  def do_exit(self, arg):
    self.do_EOF(arg)

  def do_set(self, arg):
    if arg.strip() == "":
      print "Usage: set|edit <servicename>"
      return
    print
    sys.stdout.write("Login: ")
    login = sys.stdin.readline().strip()
    sys.stdout.write("Password: ")
    password = sys.stdin.readline().strip()
    sys.stdout.write("Comment: ")
    comment = sys.stdin.readline().strip()
    db.set(arg, login, password, comment)
    print "DON'T FORGET TO *save*, otherwise data will be lost"
    print

  def do_save(self, arg):
    cdbpass = getpass.getpass(prompt='Enter password to encrypt file: ')
    cdbpasschk = getpass.getpass(prompt='And one more time the same please: ')
    if cdbpass != cdbpasschk:
      print "Passwords do not match, file saving aborted"
      return
    key = hashlib.sha256(cdbpass).digest()
    crypter.encrypt_file(key, dbfile.name, store.tmpfile.name)
    store.save()


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

cli = CmdLine()
cli.cmdloop()
exit(0)

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
    cmd = args[0].lower()
    if cmd == 'list' or cmd == 'ls':
      services = db.list()
      for service in services:
        print service
    elif cmd == 'get' or cmd == 'cat':
      if len(args) != 2:
        print "Usage: get|cat <servicename>"
        continue
      service = db.get(args[1])
      print
      print "Service: " + service["service"]
      print "Login: " + service["login"]
      print "Password: " + service["password"]
      print "Comment: " + service["comment"]
    elif cmd == '?' or cmd == 'help':
      print """
Usage:

      list                  lists all services stored in db
      get <servicename>     shows service data
      set <servicename>     creates new or modifies existing service
      delete <servicename>  deletes service from db
      help                  shows this message
      save                  encrypts and saves db to yandex.disk
      exit                  exits yanpassword"""
    elif cmd == 'set' or cmd == 'edit':
      if len(args) != 2:
        print "Usage: set|edit <servicename>"
        continue
      print
      sys.stdout.write("Login: ")
      login = sys.stdin.readline().strip()
      sys.stdout.write("Password: ")
      password = sys.stdin.readline().strip()
      sys.stdout.write("Comment: ")
      comment = sys.stdin.readline().strip()
      db.set(args[1], login, password, comment)
      print "DON'T FORGET TO *save*, otherwise data will be lost"

    elif cmd == 'delete' or cmd == 'rm':
      if len(args) != 2:
        print "Usage: delete|rm <servicename>"
        continue
      service = db.delete(args[1])
    elif cmd == 'exit' or cmd == 'quit':
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
    else:
      print "Syntax error. Use help command to list available commands"
