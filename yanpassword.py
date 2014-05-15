#!/usr/bin/env python

from yadisk.store import Store
from passdb.passdb import PassDB
from passdb import crypter
import getpass
import sys
import tempfile
import cmd
import os
import re

CONFIG = os.path.join(os.getenv('HOME'), '.yanpassword.conf')
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
    sys.stdout.write("\nReally exit (Y/n)? ")
    answer = sys.stdin.readline().strip().lower()
    if answer in [ "y", "" ]:
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
    crypter.encrypt_file(cdbpass, dbfile.name, store.tmpfile.name)
    store.save()


if __name__ == "__main__":

  ylogin, ypass = None, None

  if os.path.exists(CONFIG) and os.path.isfile(CONFIG):
    pattern = re.compile("(user|password)\s*=\s*(.+)")
    with open(CONFIG) as cfg:
      for line in cfg:
        line = line.strip()
        line = re.sub(r'\s*#.*$', '', line)
        match = pattern.match(line)
        if match is None: continue
        if match.groups()[0] == "user":
          ylogin = match.groups()[1]
        elif match.groups()[0] == "password":
          ypass = match.groups()[1]
      if not ypass is None:
        mode = os.stat(CONFIG).st_mode
        if mode & 63 != 0:
          print "Storing password in config file is insecure. At least change your config file permissions to 0600"
          sys.exit(255)

  while True:
    if ylogin is None:
      sys.stdout.write("\nYandex login: ")
      ylogin = sys.stdin.readline().strip()
    else:
      print "Using yandex login '%s'" % ylogin
    if ypass is None:
      ypass = getpass.getpass(prompt="Password: ")

    try:
      store = Store(ylogin, ypass)
      break
    except:
      print "Authorization error, wrong login or password?"
      ylogin, ypass = None, None

  print "Loading CryptDB file"
  dbfile = tempfile.NamedTemporaryFile()

  r = store.load()
  if r["status"] == "200":
    while True:
      cdbpass = getpass.getpass("Enter CryptDB password: ")
      crypter.decrypt_file(cdbpass, store.tmpfile.name, dbfile.name)
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
