#!/usr/bin/env python

import sqlite3

class PassDB(object):
  def __init__(self, filename):
    self.filename = filename
    self.conn = sqlite3.connect(self.filename)
    c = self.conn.execute("SELECT name FROM sqlite_master WHERE NAME = 'passwords'")
    if c.fetchone() is None:
      c = self.conn.execute("CREATE TABLE passwords(service varchar(30), login varchar(30), password varchar(70), comment text)")
  
  def list(self):
    c = self.conn.execute("SELECT service FROM passwords ORDER BY service")
    services = []
    for i in c.fetchall():
      services.append(i[0])
    return services
  
  def get(self, service):
    c = self.conn.execute("SELECT service, login, password, comment FROM passwords WHERE service = '" + service + "'")
    r = c.fetchone()
    if r is None: return None
    service = {}
    service["service"] = r[0]
    service["login"] = r[1]
    service["password"] = r[2]
    service["comment"] = r[3]
    return service
  
  def set(self, service, login, password, comment):
    c = self.conn.execute("SELECT service FROM passwords WHERE service = '" + service + "'")
    if c.fetchone() is None:
      c = self.conn.execute("INSERT INTO passwords (service, login, password, comment) VALUES('" + service +"', '" + login +"', '" + password + "', '" + comment +"')")
    else:
      c = self.conn.execute("UPDATE passwords SET login = '" + login + "', password = '" + password + "', comment = '" + comment + "' WHERE service = '" + service + "'")
    self.conn.commit()
  
  def delete(self, service):
    c = self.conn.execute("DELETE FROM passwords WHERE service = '" + service + "'")
    self.conn.commit()
