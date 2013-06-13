#!/usr/bin/env python

import tempfile
import httplib2
import base64

class UnauthorizedError(Exception):
  def __init__(self, value):
    self.value = value
    
  def __str__(self):
    return repr(self.value)

class Store(object):
  
  REMOTEURL = "https://webdav.yandex.ru"
  REMOTEPATH = "/.yanpassword"
  REMOTEFILE = "/cryptdb.enc"
  
  def __init__(self, login, password):
    self.token = "Basic " + base64.b64encode(login + ":" + password)
    self.tmpfile = tempfile.NamedTemporaryFile()
    self.http = httplib2.Http()
    self.prepare()
    
  def prepare(self):
    resp = self.http.request(self.REMOTEURL + self.REMOTEPATH, method="PROPFIND", headers={"Authorization" : self.token, "Depth" : "1"})
    if resp[0]["status"] == "401":
      raise UnauthorizedError("Wrong login or password")
    if resp[0]["status"] == "404":
      print "Remote directory not found, creating"
      resp = self.http.request(self.REMOTEURL + self.REMOTEPATH, method="MKCOL", headers={"Authorization" : self.token})
  
  def load(self):
    resp = self.http.request(self.REMOTEURL + self.REMOTEPATH + self.REMOTEFILE, method="GET", headers={"Authorization" : self.token})
    if resp[0]["status"] == "404":
      print "Remote file not found"
      return resp[0]
    else:
      f = file(self.tmpfile.name, "w")
      f.write(resp[1])
      f.close()
      return resp[0]
    
  def save(self):
    f = file(self.tmpfile.name)
    data = f.read()
    f.close()
    resp = self.http.request(self.REMOTEURL + self.REMOTEPATH + self.REMOTEFILE, method="PROPFIND", headers={"Authorization" : self.token})
    if resp[0]["status"] != "404":
      print "Creating backup"
      resp = self.http.request(self.REMOTEURL + self.REMOTEPATH + self.REMOTEFILE, method="MOVE", headers={"Authorization" : self.token, "Destination" : self.REMOTEPATH + self.REMOTEFILE + ".backup"})
      if resp[0]["status"] != "201":
        print "Error creating backup, file was not saved"
        return resp[0]
    print "Saving file"
    resp = self.http.request(self.REMOTEURL + self.REMOTEPATH + self.REMOTEFILE, method="PUT", headers={"Authorization" : self.token, "Content-Type" : "application/binary"}, body=data)
    if resp[0]["status"] != "201":
      print "Error saving file"
    else:
      print "File saved successfully"
    return resp[0]
