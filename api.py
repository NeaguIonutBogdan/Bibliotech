#!/usr/bin/env python
import os
import json
import time
from flask import Flask, abort, request, jsonify, g, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemySchema 
# from conf import ma
# from your_orm import Model, Column, Integer, String, DateTime
from flask_httpauth import HTTPBasicAuth
from sqlalchemy.ext.declarative import DeclarativeMeta
import jwt
from werkzeug.security import generate_password_hash, check_password_hash

# initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

# extensions
db = SQLAlchemy(app)
ma = Marshmallow(app)
auth = HTTPBasicAuth()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(32),  unique=False,  index=True)
    last_name = db.Column(db.String(32),  unique=False, index=True)
    username = db.Column(db.String(32), unique=False, index=True)
    password_hash = db.Column(db.String(64))
    type_user =db.Column(db.String(64))

    def hash_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expires_in=600):
        return jwt.encode(
            {'id': self.id, 'exp': time.time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_auth_token(token):
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'],
                              algorithms=['HS256'])
        except:
            return
        return User.query.get(data['id'])

class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True)
    book_name = db.Column(db.String(32),  unique=False,  index=True)
    book_author = db.Column(db.String(32),  unique=False, index=True)
    book_description = db.Column(db.String(32), unique=False, index=True)
    
    def as_dict(self):
    #    return {c.name: getattr(self, c.book_name) for c in self.__table__.columns}
        return {'id': self.id,'book_name':self.book_name, 'book_author':self.book_author, 'book_description':self.book_description}

    def __repr__(self):
        # result = {'id': self.id,'book_name':{self.book_name}, 'book_author':{self.book_author}, 'book_description':{self.book_description}}
        result = f'({self.id}, {self.book_name}, {self.book_author},{self.book_description})'

        return result
        # return jsonify(Book=item.serialize)
        # return (jsonify({'id': self.id ,'book_name': self.book_name, 'book_author': self.book_author, 'book_description': self.book_description}))

class BookSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Book
        load_instance = True

# class BookSchema(Resource):
#     def get(self):
#       shares = db.session.query(Book).all()
#       result = photos_share_schema.dump(shares)
#       return jsonify(result.data)

# user_schema = UserSchema()
# users_schema = BookSchema (many=True)

@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.route('/register', methods=['POST'])#api/users
def new_user():
    first_name = request.json.get('first_n')
    last_name = request.json.get('last_n')
    username = request.json.get('username')
    password = request.json.get('password')
    type_user = request.json.get('type_user')
    if username is None or password is None or first_name  is None or last_name  is None or type_user  is None:
        abort(400)    # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        abort(400)    # existing user
    user = User(first_name=first_name, last_name=last_name, username=username, type_user=type_user)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return (jsonify({'id': user.id ,'username': user.username, 'first_name': user.first_name, 'last name': user.last_name, 'type_user': type_user}), 201,
            {'Location': url_for('get_user', id=user.id, _external=True)})


@app.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})


@app.route('/login')#api/token
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 1800})


@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.username})

@app.route('/book', methods=['POST'])
def new_book():
    book_name = request.json.get('book_name')
    book_author = request.json.get('book_author')
    book_description = request.json.get('book_description')
    if book_name is None or book_author is None or book_description  is None:
        abort(400)    # missing arguments
  
    book = Book(book_name=book_name, book_author=book_author, book_description=book_description)
    db.session.add(book)
    db.session.commit()
    # if book_name == book.book_name:
    #     abort(400)
    return (jsonify({'id': book.id ,'book_name': book.book_name, 'book_author': book.book_author, 'book_description': book.book_description}), 201,
               {'Location': url_for('get_user', id=book.id, _external=True)})

@app.route('/book/<int:id>', methods=['GET'])
def api_book(id):
    book = Book.query.get(id)
    if not book:
        abort(400)
    return jsonify({'book': book.id, 'book_name': book.book_name, 'book_author': book.book_author, 'book_description': book.book_description})


@app.route('/books2', methods=['GET'])
def index():
    book = Book.query.all()
    book_schema = BookSchema(many=True)
    output = book_schema.dump(book)
    return jsonify({'books' : output})

@app.route('/books', methods=['GET'])
# @auth.login_required
def api_all_books():
    book = Book.query.all()
    if not book:
        abort(400)
    return book.__repr__()
    # return b
    # for b in book:
    #     return ({b.id, b.b.book_name, b.book_author, b.book_description})
    # return jsonify(book.__repr__())
    # return jsonify({'book': book.id, 'book_name': book.book_name, 'book_author': book.book_author, 'book_description': book.book_description})

    # result = {
    #         "book_name": book.book_name,
    #         "book_author":  book.book_author,
    #         "book_description": book.book_description
    #     }

    # python_dictionary = json.loads(book) 
    # json_string=json.dumps(python_dictionary)
    # return json_string

if __name__ == '__main__':
    if not os.path.exists('db.sqlite'):
        db.create_all()
    app.run(debug=True)
    