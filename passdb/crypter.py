#!/usr/bin/env python

import sys
try:
  from Crypto.Cipher import AES
except ImportError:
  # MacOSX / Win32 workaround
  import crypto
  sys.modules['Crypto'] = crypto
  from crypto.Cipher import AES
import os
import struct
import random
import hashlib
from pbkdf2 import pbkdf2_hex

SIGNATURE = "~ypcryptdb2.0"
PBKDF2_ITERATIONS = 400
PBKDF2_KEYLENGTH = 16

def random_salt(length=16):
  return ''.join(chr(random.randint(0, 0xFF)) for i in range(length))

def encrypt_file(password, in_filename, out_filename=None, chunksize=64*1024):
  if not out_filename: out_filename = in_filename + '.enc'

  psalt = random_salt()
  key = pbkdf2_hex(password, psalt, PBKDF2_ITERATIONS, PBKDF2_KEYLENGTH)
  
  iv = random_salt()

  encryptor = AES.new(key, AES.MODE_CBC, iv)
  filesize = os.path.getsize(in_filename)

  with open(in_filename, 'rb') as infile:
    with open(out_filename, 'wb') as outfile:
      outfile.write(SIGNATURE)
      outfile.write(struct.pack('<Q', filesize))
      outfile.write(psalt)
      outfile.write(iv)
      while True:
        chunk = infile.read(chunksize)
        if len(chunk) == 0:
          break
        elif len(chunk) % 16 != 0:
          chunk += ' ' * (16 - len(chunk) % 16)
        outfile.write(encryptor.encrypt(chunk))

def decrypt_file(password, in_filename, out_filename=None, chunksize=24*1024):
  if not out_filename:
    out_filename = os.path.splitext(in_filename)[0]

  with open(in_filename, 'rb') as infile:
    signature = infile.read(len(SIGNATURE))
    if signature != SIGNATURE:
      return legacy_decrypt_file(password, in_filename, out_filename, chunksize)

  with open(in_filename, 'rb') as infile:
    # signature skip
    infile.read(len(SIGNATURE))
    
    origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
    psalt = infile.read(16)
    key = pbkdf2_hex(password, psalt, PBKDF2_ITERATIONS, PBKDF2_KEYLENGTH)
    
    iv = infile.read(16)
    
    decryptor = AES.new(key, AES.MODE_CBC, iv)

    with open(out_filename, 'wb') as outfile:
      while True:
        chunk = infile.read(chunksize)
        if len(chunk) == 0:
          break
        outfile.write(decryptor.decrypt(chunk))

      outfile.truncate(origsize)

def legacy_encrypt_file(password, in_filename, out_filename=None, chunksize=64*1024):
  if not out_filename:
    out_filename = in_filename + '.enc'

  key = hashlib.sha256(password).digest()

  iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
  encryptor = AES.new(key, AES.MODE_CBC, iv)
  filesize = os.path.getsize(in_filename)

  with open(in_filename, 'rb') as infile:
    with open(out_filename, 'wb') as outfile:
      outfile.write(struct.pack('<Q', filesize))
      outfile.write(iv)

      while True:
        chunk = infile.read(chunksize)
        if len(chunk) == 0:
          break
        elif len(chunk) % 16 != 0:
          chunk += ' ' * (16 - len(chunk) % 16)
        outfile.write(encryptor.encrypt(chunk))

def legacy_decrypt_file(password, in_filename, out_filename=None, chunksize=24*1024):
  if not out_filename:
    out_filename = os.path.splitext(in_filename)[0]

  key = hashlib.sha256(password).digest()

  with open(in_filename, 'rb') as infile:
    origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
    iv = infile.read(16)
    decryptor = AES.new(key, AES.MODE_CBC, iv)

    with open(out_filename, 'wb') as outfile:
      while True:
        chunk = infile.read(chunksize)
        if len(chunk) == 0:
          break
        outfile.write(decryptor.decrypt(chunk))

      outfile.truncate(origsize)


if __name__ == '__main__':
  print "Testing..."

  sys.stdout.write("Creating file ... ")
  with open('abcde', 'wb') as srcfile:
    srcfile.write("abcde!\n")
  print 'done'

  print 'File contents:'
  with open('abcde', 'rb') as srcfile:
    print "====="
    sys.stdout.write(srcfile.read())
    print "====="

  print 'Encrypting with password "abcdepass"'
  encrypt_file('abcdepass', 'abcde')
  print 'Encrypted file contents in hex:'
  with open('abcde.enc', 'rb') as encfile:
    print "====="
    sys.stdout.write(encfile.read().encode('hex'))
    print
    print "====="

  os.unlink('abcde')
  print 'Decrypting...'
  decrypt_file('abcdepass', 'abcde.enc')
  print 'Decrypted file contents:'
  with open('abcde', 'rb') as srcfile:
    print "====="
    sys.stdout.write(srcfile.read())
    print "====="

  print 'Legacy encrypting with password "abcdepass"'
  legacy_encrypt_file('abcdepass', 'abcde')
  print 'Encrypted file contents in hex:'
  with open('abcde.enc', 'rb') as encfile:
    print "====="
    sys.stdout.write(encfile.read().encode('hex'))
    print
    print "====="

  os.unlink('abcde')
  print 'Decrypting...'
  decrypt_file('abcdepass', 'abcde.enc')
  print 'Decrypted file contents:'
  with open('abcde', 'rb') as srcfile:
    print "====="
    sys.stdout.write(srcfile.read())
    print "====="


