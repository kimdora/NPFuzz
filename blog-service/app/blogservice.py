#!/usr/bin/python
from flask import Blueprint, jsonify, request
from json import loads as json_decode
from functools import wraps
from hashlib import sha1
from sqlite3 import connect as sqlite3_connect
from re import match

hash = lambda x: sha1(x.encode('utf-8') + b'salt_is_salty').hexdigest()[10:30]
dbconn = lambda: sqlite3_connect('blog.db')

BlogService = Blueprint('blogservice', __name__)

def check_id_exists(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    if '_id' not in kwargs or not kwargs['_id'].isdigit():
      return jsonify({'error': 1, 'message': 'invalid id'}), 400
    _id = int(kwargs['_id'])

    with dbconn() as db:
      c = db.cursor()
      c.execute('SELECT 1 FROM post WHERE id=? LIMIT 1;', (_id, ))
      if len(c.fetchall()) == 0:
        return jsonify({'error': 1, 'message': 'post not found'}), 404

    return f(*args, **kwargs)
  return decorated_function

@BlogService.route('/posts/', methods=['GET'])
def show_posts():
  posts = []
  with dbconn() as db:
    c = db.cursor()
    r = c.execute('SELECT body FROM post ORDER BY id DESC;')
    for post in r:
      posts.append({'body': post[0]})
  return jsonify({'error': 0, 'posts': posts})

@BlogService.route('/posts/', methods=['POST'])
def new_post():
  if request.content_type == 'application/json':
    data = json_decode(request.data)
  else:
    return jsonify({'error': 1, 'message': 'invalid content type'}), 400

  if 'body' not in data or not isinstance(data['body'], str):
    return jsonify({'error': 1, 'message': 'invalid content'}), 400
  _body = data['body']

  new_id = -1
  with dbconn() as db:
    c = db.cursor()
    c.execute('INSERT INTO post (body) VALUES(?)', (_body, ))
    db.commit()
    new_id = c.lastrowid
  return jsonify({'error': 0, 'id': new_id}), 201

@BlogService.route('/posts/<_id>', methods=['DELETE'])
@check_id_exists
def delete_post(_id):
  with dbconn() as db:
    c = db.cursor()
    c.execute('DELETE FROM post WHERE id=?;', (_id, ))
    db.commit()
  return jsonify({'error': 0})

@BlogService.route('/posts/<_id>', methods=['GET'])
@check_id_exists
def show_post(_id):
  with dbconn() as db:
    c = db.cursor()
    c.execute('SELECT body FROM post WHERE id=?;', (_id, ))
    post = c.fetchone()
    return jsonify({'error': 0, 'post': {'body': post[0], 'checksum': hash(post[0])}})
  return jsonify({'error': 1, 'message': 'unknown error'}), 500 # should not be reach

@BlogService.route('/posts/<_id>', methods=['PUT'])
@check_id_exists
def update_post(_id):
  if request.content_type == 'application/json':
    data = json_decode(request.data)
  else:
    return jsonify({'error': 1, 'message': 'invalid content type'}), 400

  if 'body' not in data or not isinstance(data['body'], str):
    return jsonify({'error': 1, 'message': 'invalid content'}), 400
  _body = data['body']

  if 'checksum' not in data or not isinstance(data['checksum'], str)\
    or match('^[0-9a-f]{20}$', data['checksum']) == None:
    return jsonify({'error': 1, 'message': 'invalid checksum'}), 400
  _checksum = data['checksum']

  with dbconn() as db:
    c = db.cursor()
    c.execute('SELECT body FROM post WHERE id=?;', (_id, ))
    post = c.fetchone()
    if hash(post[0]) == _checksum:
      c.execute('UPDATE post SET body=? WHERE id=?;', (_body, _id))
      if c.rowcount != 1:
        return jsonify({'error': 1, 'message': 'update error'}), 500 # should not be reach
    else:
      return jsonify({'error': 1, 'message': 'invalid checksum'}), 400
  return jsonify({'error': 0}), 201

