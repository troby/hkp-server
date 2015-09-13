#!/usr/bin/env python2.7
import gnupg
from pprint import pprint
import sqlite3

gpg = gnupg.GPG(gnupghome='key_store')
raw_keys = gpg.list_keys()
db = sqlite3.connect('test.db')
cur = db.cursor()

'''
raw_keys is a dict:
[{'algo': u'1',
  'date': u'1440843280',
  'dummy': u'',
  'expires': u'1756203280',
  'fingerprint': u'C35256C67AD9ACF114D974E973AA81C18E981117',
  'keyid': u'73AA81C18E981117',
  'length': u'4096',
  'ownertrust': u'-',
  'subkeys': [[u'A4C426E89CFCAF9D', u'e']],
  'trust': u'-',
  'type': u'pub',
  'uids': [u'repoman (repo backups) <repoman@darkstar>']}]
'''
def show_raw():
  for k in raw_keys:
    print '%s' % k['keyid']
    for id in k['uids']:
      print '%s' % id
    print '\n'

def add_uid(key_dict):
  keyid = key_dict['keyid']
  for userid in key_dict['uids']:
    cur.execute('INSERT INTO userids (keyid,userid) VALUES (?,?)', (keyid,userid))

def show_uids():
  cur.execute('select * from userids')
  uids = cur.fetchall()
  pprint(uids)

def show_keys():
  cur.execute('select * from keys')
  keys = cur.fetchall()
  cur.execute('select * from userids')
  userids = cur.fetchall()
  return (keys, userids)

def slurp_keys(raw_keys):
  for k in raw_keys:
    cur.execute(
      'INSERT INTO keys (type,length,algo,keyid,cdate,expire) values (?,?,?,?,?,?)',
      (k['type'],k['length'],k['algo'],k['keyid'],k['date'],k['expires'])
    )
    for uid in k['uids']:
      cur.execute('INSERT INTO userids (keyid,userid) VALUES (?,?)', (k['keyid'],uid))
