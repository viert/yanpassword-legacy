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

  def cmdloop(self):
    try: cmd.Cmd.cmdloop(self)
    except KeyboardInterrupt:
      print
      self.cmdloop()

  def do_list(self, arg):
    """list:
  lists all services stored in db"""
    services = db.list()
    for service in services:
      print service

  def do_ls(self, arg):
    """list:
  lists all services stored in db"""
    self.do_list(arg)

  def do_get(self, arg):
    """get:
  shows service data
  Usage: get|cat <servicename>"""
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
    """delete:
  remove service's data from database
  Usage: delete|rm <servicename>"""
    if arg.strip() == "":
      print "Usage: delete|rm <servicename>"
      return
    service = db.delete(arg)
  
  def do_rm(self, arg):
    """delete:
  remove service's data from database
  Usage: delete|rm <servicename>"""
    self.do_delete(arg)

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
    """get:
  shows service data
  Usage: get|cat <servicename>"""
    self.do_get(arg)

  def do_EOF(self, arg):
    """exit:
  exits program"""
    sys.stdout.write("\nReally exit (y/n)? ")
    if sys.stdin.readline().strip().lower() == "y":
      sys.exit()

  def do_exit(self, arg):
    """exit:
  exits program"""
    self.do_EOF(arg)

  def do_edit(self, arg):
    """set:
  set service's data
  Usage: set|edit <servicename>"""
    self.do_set(arg)

  def do_set(self, arg):
    """set:
  set service's data
  Usage: set|edit <servicename>"""
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
    """save:
  encrypts and saves db to yandex.disk"""
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
