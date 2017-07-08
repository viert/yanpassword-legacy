#!/usr/bin/env python

import tempfile
import requests
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
    self.prepare()
    
  def prepare(self):
    resp = requests.request("PROPFIND", self.REMOTEURL + self.REMOTEPATH, 
                             headers={"Authorization" : self.token, "Depth" : "1"})
    if resp.status_code == 401:
      raise UnauthorizedError("Wrong login or password")
    if resp.status_code == 404:
      print "Remote directory not found, creating"
      resp = requests.request("MKCOL", self.REMOTEURL + self.REMOTEPATH, headers={"Authorization" : self.token})
  
  def load(self):
    resp = requests.get(self.REMOTEURL + self.REMOTEPATH + self.REMOTEFILE, headers={"Authorization" : self.token})
    if resp.status_code == 404:
      print "Remote file not found"
      return resp
    else:
      f = file(self.tmpfile.name, "w")
      f.write(resp.content)
      f.close()
      return resp
    
  def save(self):
    f = file(self.tmpfile.name)
    data = f.read()
    f.close()
    resp = requests.request("PROPFIND", self.REMOTEURL + self.REMOTEPATH + self.REMOTEFILE, headers={"Authorization" : self.token, "Depth" : "1"})
    if resp.status_code != 404:
      print "Creating backup"
      resp = requests.request("MOVE", self.REMOTEURL + self.REMOTEPATH + self.REMOTEFILE, headers={"Authorization" : self.token, "Destination" : self.REMOTEPATH + self.REMOTEFILE + ".backup"})
      if resp.status_code != 201:
        print "Error creating backup, file was not saved"
        return resp
    print "Saving file"
    resp = requests.put(self.REMOTEURL + self.REMOTEPATH + self.REMOTEFILE, headers={"Authorization" : self.token, "Content-Type" : "application/binary"}, data=data)
    if resp.status_code != 201:
      print "Error saving file"
    else:
      print "File saved successfully"
    return resp
