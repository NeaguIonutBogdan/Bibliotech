#!/usr/bin/env python
import os
import json
import time
from flask import Flask, abort, request, jsonify, g, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemySchema 
from sqlalchemy.orm import relationship
from sqlalchemy import update
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

class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(db.Integer, primary_key=True)
    borrow_time = db.Column(db.Integer)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    # book_name = db.Column(db.String(32), db.ForeignKey('book.book_name'))
    # book_id_Book = relationship("Book", foreign_keys=[book_id])
    # book_name_Book = relationship("Book", foreign_keys=[book_name])
    transaction_extend_time  =db.Column(db.Integer, default=0)
    transaction_return_id  =db.Column(db.Integer, default=0)
    transaction_number_of_extensions= db.Column(db.Integer, default=0)
    transaction_status = db.Column(db.Integer, default=0)
    def __repr__(self):
        result = f'({self.id}, {self.borrow_time}, {self.book_id})'
    # def __init__(self,id, borrow_time, book_id, transaction_extend_time, transaction_number_of_extensions, transaction_status):
    #     self.id=id
    #     self.borrow_time=borrow_time
    #     self.book_id=book_id
    #     self.transaction_extend_time=transaction_extend_time
    #     self.transaction_number_of_extensions=transaction_number_of_extensions
    #     self.transaction_status=transaction_status



class TransactionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Transaction
        load_instance = True

class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True)
    book_name = db.Column(db.String(32), unique=False,  index=True)
    book_author = db.Column(db.String(32),  unique=False, index=True)
    book_description = db.Column(db.String(32), unique=False, index=True)
    book_status = db.Column(db.Integer, default=0)
    book_rating = db.Column(db.Integer, default=0)
    book_text = db.Column(db.String(32))
    posts = db.relationship('Transaction', backref='author', lazy='dynamic')
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

#   1.1
@app.route('/register', methods=['POST'])#api/users
def new_user():
    first_name = request.json.get('first_n')
    last_name = request.json.get('last_n')
    username = request.json.get('username')
    password = request.json.get('password')
    type_user = request.json.get('type_user')
    if first_name is None :
        return jsonify({"message": "No first_name data provided"}), 400    # missing arguments:
    if last_name is None:
        return jsonify({"message": "No last_name data provided"}), 400    # missing arguments:
    if username is None:
        return jsonify({"message": "No username data provided"}), 400    # missing arguments:
    if password is None:
        return jsonify({"message": "No password data provided"}), 400    # missing arguments:
    if type_user is None:
        return jsonify({"message": "No type_user data provided"}), 400    # missing arguments:
    if User.query.filter_by(username=username).first() is not None:
        return jsonify({"message": "The uses exists in DB"}), 400    # existing user
    user = User(first_name=first_name, last_name=last_name, username=username, type_user=type_user)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return (jsonify({'id': user.id ,'username': user.username, 'first_name': user.first_name, 'last name': user.last_name, 'type_user': type_user}), 201,
            {'Location': url_for('get_user', id=user.id, _external=True)})

#   check if authtoken works with id
@app.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})

#   1.2
@app.route('/login')#api/token
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 1800})

#   check if authtoken works
@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.username})

#   2.1
@app.route('/book', methods=['POST'])   #de pus @auth
def new_book():
    book_name = request.json.get('book_name')
    book_author = request.json.get('book_author')
    book_description = request.json.get('book_description')

    if book_name is None:
            return jsonify({"message": "No book_name data provided"}), 400       # missing arguments:
    if book_author is None:
        return jsonify({"message": "No book_author data provided"}), 400         # missing arguments:
    if book_description is None:
        return jsonify({"message": "No book_description data provided"}), 400    # missing arguments:
    if Book.query.filter_by(book_name=book_name).first() is not None:
        return jsonify({"message": "The book_name exists in DB"}), 400           # existing user

    book = Book(book_name=book_name, book_author=book_author, book_description=book_description)
    db.session.add(book)
    db.session.commit()
    return (jsonify({'id': book.id ,'book_name': book.book_name, 'book_author': book.book_author, 'book_description': book.book_description}), 201,
               {'Location': url_for('get_user', id=book.id, _external=True)})

#   2.3
@app.route('/book/<int:id>', methods=['GET'])  #de pus @auth
def api_book(id):
    book = Book.query.get(id)
    if not book:
        return jsonify({"message": "The book does not exist in DB"}), 400           # book does not exist in DB
    else:
        return jsonify({'book': book.id, 'book_name': book.book_name, 'book_author': book.book_author, 'book_description': book.book_description, \
                        'book_status': book.book_status, 'book_rating': book.book_rating, 'book_text': book.book_text})

#   post books adauga mai multe carti de facut
#   2.2
@app.route('/books', methods=['POST'])   #de pus @auth
def new_books():
    books = {}

    # book_name = request.json.get('book_name')
    # book_author = request.json.get('book_author')
    # book_description = request.json.get('book_description')
    for book in books:
        book_name = request.json.get('book_name')
        book_author = request.json.get('book_author')
        book_description = request.json.get('book_description')
        book = Book(book_name=book_name, book_author=book_author, book_description=book_description)

    # if book_name is None:
    #         return jsonify({"message": "No book_name data provided"}), 400       # missing arguments:
    # if book_author is None:
    #     return jsonify({"message": "No book_author data provided"}), 400         # missing arguments:
    # if book_description is None:
    #     return jsonify({"message": "No book_description data provided"}), 400    # missing arguments:
    # if Book.query.filter_by(book_name=book_name).first() is not None:
    #     return jsonify({"message": "The book_name exists in DB"}), 400           # existing user

    # book = Book(book_name=book_name, book_author=book_author, book_description=book_description)
        books={book, book}
        db.session.add(book)
        db.session.commit()

    book = Book.query.all()
    book_schema = BookSchema(many=True)
    output = book_schema.dump(book)
    return (jsonify({'books': output }), 200)   
    # return (jsonify({'id': books.id ,'book_name': books.book_name, 'book_author': books.book_author, 'book_description': books.book_description}), 201,
    #         {'Location': url_for('get_user', id=books.id, _external=True)})
#   2.4
@app.route('/books2', methods=['GET'])  #de pus @auth
def index():
    book = Book.query.all()
    book_schema = BookSchema(many=True)
    output = book_schema.dump(book)
    if output is None:
        return jsonify({"message": "There are no books in DB"}), 400           # no books in DB
    else:
        return jsonify({'books' : output})

@app.route('/bookssssss', methods=['GET'])
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

#   3.1
@app.route('/transaction', methods=['POST'])   #de pus @authenticate                #IMPRUMUTA O CARTE
def new_transaction():
    book_id = request.json.get('book_id')
    borrow_time = request.json.get('borrow_time')
    if book_id is None:
        return jsonify({"message": "No book_id data provided"}), 400    # missing arguments:
    if borrow_time is None:
        return jsonify({"message": "No borrow_time data provided"}), 400    # missing arguments:
    if borrow_time in range(1, 21):
        transaction = Transaction(book_id=book_id, borrow_time=borrow_time)
        db.session.add(transaction)
        db.session.commit()
        return (jsonify({'Succes':'Succes, transaction created for book with id: '+ str(transaction.book_id),'transaction_id': transaction.id }), 201,
            {'Location': url_for('get_user', id=transaction.id, _external=True)})
    else:
         return (jsonify({'Error':'No book available. '}), 404)

#   3.2
@app.route('/transaction/<int:id>', methods=['GET'])
def geet_transaction_id(id):
    transaction = Transaction.query.get(id)
    remaining_time=20-transaction.borrow_time
    if transaction is None:
        return jsonify({"message": "No transaction_id  data provided"}), 400    # missing arguments:
    if transaction.id is None:
        return jsonify({"message": "Transaction id is not valid"}), 400    # id is not valid:
    return jsonify({'book_id': transaction.book_id, 'borrow_time': transaction.borrow_time, 'remaining_time': remaining_time, \
                    'number_of_extensions': transaction.transaction_number_of_extensions, 'status': transaction.transaction_status})

#   3.3
@app.route('/transactions', methods=['GET'])  #de pus @auth
def all_transactions():
    transaction = Transaction.query.all()
    transactions_schema = TransactionSchema(many=True)
    output = transactions_schema.dump(transaction)

    book = Book.query.all()
    transactions_schema = BookSchema(many=True)
    output2 = transactions_schema.dump(book)
    result = output + output2
    if result is None:
        return jsonify({'Error' : "There is no transaction in DB."})
    else:
        return jsonify({'transactions' : result})

#   3.4
@app.route('/extend2', methods=['POST'])   #de pus @auth
def new_extend2():
    transaction_id = request.json.get('id')
    transaction_extend_time = request.json.get('extend_time')

    if transaction_id is None:
        return jsonify({"message": "No transaction_id data provided"}), 400    # missing arguments:
    if transaction_extend_time is None:
        return jsonify({"message": "No extend_time data provided"}), 400    # missing arguments:

    if transaction_extend_time in range (1,6) :
        update_transaction = Transaction.query.filter_by(id=transaction_id).first()
        update_transaction.transaction_extend_time=transaction_extend_time
        update_transaction.transaction_number_of_extensions += 1
        db.session.commit()
        if update_transaction.transaction_number_of_extensions >= 2:
            return (jsonify({'Error':'Error, transaction exceeded 2.'}), 400)
        else:
            return (jsonify({'Succes':'Succes, transaction extended with ' + str(update_transaction.transaction_extend_time) + \
                ' days.','transaction_id': update_transaction.id , 'transaction_number_of_extensions': update_transaction.transaction_number_of_extensions }), 201,
                {'Location': url_for('get_user', id=update_transaction.id, _external=True)})
    else:
        abort(400)

#   3.5
@app.route('/return', methods=['POST'])   #de pus @auth
def return_transaction():
    transaction_id = request.json.get('id')

    if transaction_id is None:
        return jsonify({"Error": "No transaction_id data provided"}), 400    # missing arguments:

    return_book_transaction = Transaction.query.filter_by(id=transaction_id).first()
    return_transaction = return_book_transaction.borrow_time + return_book_transaction.transaction_extend_time

    if return_transaction <= 20:
        return_book_transaction.transaction_return_id += 1
        return (jsonify({'Succes':'Succes, return transaction created.'}), 201)
    elif return_transaction >= 20:
        return_book_transaction.transaction_return_id += 1
        return (jsonify({'Error':'FIRST, borrow_time has been exceeded.'+ return_book_transaction.transaction_id}), 201)

    else:
        abort(400)
#   3.6
@app.route('/returns', methods=['GET'])  #de pus @auth
def get_all_returns():
    transaction = Transaction.query.all()
    transactions_schema = TransactionSchema(many=True)
    output = transactions_schema.dump(transaction)

    if output is None:
        return jsonify({'Error' : "There is no books to return in DB."}), 400
    else:
        return jsonify({'transactions' : output}),  200

#   3.7
@app.route('/return/end', methods = ['POST'])
def return_and_delete():
    return_id = request.json.get('return_id')
    if return_id is None:
        return jsonify({"message": "No return_id data provided"}), 400    # missing arguments:

    return_end = Transaction.query.filter_by(id=return_id).first() 

    db.session.delete(return_end)
    db.session.commit()
 
    return jsonify({'Succes': 'A review has been DELETED.'}), 200

#   3.8
@app.route('/review', methods=['POST'] )    #de pus @auth
def book_review():
    book_id = request.json.get('book_id')
    book_rating = request.json.get('book_rating')
    book_text = request.json.get('book_text')

    if book_id is None:
        return jsonify({"message": "No book_id data provided"}), 400    # missing arguments:
    if book_rating is None:
        return jsonify({"message": "No book_rating data provided"}), 400    # missing arguments:
    if book_text is None:
        return jsonify({"message": "No book_text data provided"}), 400    # missing arguments:

    update = Book.query.filter_by(id=book_id).first()

    update.book_rating=book_rating
    update.book_text=book_text

    db.session.commit()

    if update is None:
        return jsonify({'Error' : "There is no update to be made."})
    else:
        return (jsonify({'Succes': 'A review has been added.', 'id': update.id ,'rating': update.book_rating, 'text': update.book_text}), 201,
                {'Location': url_for('get_user', id=update.id, _external=True)})

if __name__ == '__main__':
    if not os.path.exists('db.sqlite'):
        db.create_all()
    app.run(debug=True)
    