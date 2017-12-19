#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
 OpenPGP HKP Protocol compliant server according
   to IETF Memo drafted by D. Shaw March 2003
'''
from flask import Flask, request, render_template, abort, \
     session, g, redirect, url_for, flash
from contextlib import closing
import os
import sqlite3
import gnupg
from pprint import pprint

app = Flask(__name__)
app.config.from_pyfile('hkpconfig.cfg', silent=False)

@app.route('/keytest')
def key_test():
  value = request.args.get('key')
  return value

@app.route('/test')
def test():
  return return_error(403, 'Forbidden')

# '404 Not found' response
@app.errorhandler(404)
def error_404(error):
  if os.path.isfile('static/404.html'):
    return app.send_static_file('404.html'), 404
  else:
    return return_error(404, 'Not found')

# '501 Not implemented' response
@app.route('/501', methods=['GET'])
def error_501():
  return return_error(501, 'Not implemented')

# generic error handling
def return_error(status, response):
  error_msg = '%d - %s' % (status, response)
  return render_template(
    'error.html',
    title=error_msg,
    header=error_msg
  ), status

# search page
@app.route('/', methods=['GET','POST'])
def do_search():
  return render_template('search.html',
    title='Search Keys',
    header='Welcome'
  )

# /pks/lookup
@app.route('/pks/lookup', methods=['GET'])
def lookup():
  op = request.args.get('op')
  if op == None:
    return do_search()
  search = request.args.get('search')
  if search == None:
    return return_error(420, 'No search specified')
  if search == '':
    return return_error(420, 'Empty search')
  if op == 'get':
    return lookup_get(search)
  elif op == 'index':
    return lookup_index(search)
  elif op == 'vindex':
    return lookup_vindex(search)
  #elif op == 'x-<none>':
    #return 'placeholder for custom operations'
  else:
    return return_error(420, 'Invalid operation')

# lookup operations
def lookup_get(search):
  key = query_db('SELECT type,length,algo,keyid,cdate,expire FROM keys WHERE keyid = ?', (search,))
  if len(key) < 1:
    return return_error(404, 'Key not found')
  userids = get_userids(search)
  return render_template('result.html',
    title='search results',
    header='Search Results',
    key=key,
    userids=userids
  )
def lookup_index(search):
  return error_501()
def lookup_vindex(search):
  return error_501()

# /pks/add
@app.route('/pks/add', methods=['POST'])
def add_key():
  # make sure keyid is not already in database
  return error_501()

@app.route('/about', methods=['GET'])
def about_page():
  fh = open('VERSION')
  version = fh.read()
  fh.close()
  fh = open('LICENSE')
  license = fh.read()
  fh.close()
  message = 'HKP-Server v%s' % version
  return render_template('about.html',
    title='About HKP-Server',
    header=message,
    license=license
  )

# submit a key
# validate uploaded key
# save key to keyring and add to db

# sql database
def connect_db():
    return sqlite3.connect('flaskr.db')

def init_db():
  with closing(connect_db()) as db:
    with app.open_resource('schema.sql', mode='r') as f:
      cur = db.cursor()
      cur.executescript(f.read())
      slurp_keys(cur)
    db.commit()

def query_db(query, args=(), one=False):
  cur = g.db.cursor()
  cur.execute(query, args)
  rows = cur.fetchall()
  return rows

def slurp_keys(cur):
  gpg = gnupg.GPG(gnupghome=app.config['HKP_STORE'])
  raw_keys = gpg.list_keys()
  for k in raw_keys:
    cur.execute(
      'INSERT INTO keys (type,length,algo,keyid,cdate,expire) VALUES (?,?,?,?,?,?)',
      (k['type'],k['length'],k['algo'],k['keyid'],k['date'],k['expires'])
    )
    for uid in k['uids']:
      cur.execute('INSERT INTO userids (keyid,userid) VALUES (?,?)', (k['keyid'],uid))

# build userid list
def get_userids(keyid):
  cur = g.db.cursor()
  cur.execute('SELECT userid FROM userids WHERE keyid = ?', (keyid,))
  uids = []
  for row in cur.fetchall():
    uids.append(row)
  return uids

@app.before_request
def before_request():
  g.db = connect_db()
  g.db.row_factory = sqlite3.Row

@app.teardown_request
def teardown_request(exception):
  db = getattr(g, 'db', None)
  if db is not None:
    db.close()

if __name__ == '__main__':
  init_db()
  app.run(host=app.config['HKP_SERVER'], port=app.config['HKP_PORT'], debug=True)
