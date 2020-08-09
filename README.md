
API Documentation
-----------------

- POST **/register**

    Register a new user.<br>
    The body must contain a JSON object that defines `username` and `password` fields.<br>
    On success a status code 201 is returned. The body of the response contains a JSON object with the newly added user. A `Location` header contains the URI of the new user.      <br>
    On failure status code 400 (bad request) is returned.<br>
    Notes:
    - The password is hashed before it is stored in the database. Once hashed, the original password is discarded.
    - In a production deployment secure HTTP must be used to protect the password in transit.

- GET **/api/users/<int:id>**

    Return a user.<br>
    On success a status code 200 is returned. The body of the response contains a JSON object with the requested user.<br>
    On failure status code 400 (bad request) is returned.

- GET **/login**

    Return an authentication token.<br>
    This request must be authenticated using a HTTP Basic Authentication header.<br>
    On success a JSON object is returned with a field `token` set to the authentication token for the user and a field `duration` set to the (approximate) number of seconds the        token is valid.<br>
    On failure status code 401 (unauthorized) is returned.

- GET **/api/resource**

    Return a protected resource.<br>
    This request must be authenticated using a HTTP Basic Authentication header. Instead of username and password, the client can provide a valid authentication token in the           username field. If using an authentication token the password field is not used and can be set to any value.<br>
    On success a JSON object with data for the authenticated user is returned.<br>
    On failure status code 401 (unauthorized) is returned.

Example
-------

Once the token expires it cannot be used anymore and the client needs to request a new one. Note that in this last example the password is arbitrarily set to `x`, since the password isn't used for token authentication.

An interesting side effect of this implementation is that it is possible to use an unexpired token as authentication to request a new token that extends the expiration time. This effectively allows the client to change from one token to the next and never need to send username and password after the initial token was obtained.


########################### - 10 PUNCTE
1.1.	POST /register
	first_name 
	last_name
	email
	password
	type
    CREATE A USER: http://127.0.0.1:5000/register WITH JSON : 
    {
    "first_n" : "neagu2",
    "last_n" : "stefan2",
    "username" : "mihai2",
    "password" : "abcd",
    "type_user": "1"

}
1.2. POST /login
	email
	password
    Basic_Auth must contain username and password!
	RETURNEAZA : token
                {
                  "duration": 1800,
                  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MSwiZXhwIjoxNTk2OTgxMzYyLjQzNjAxMzJ9.Ay03LNNsZqoXIM8cglyTt3BRRdZLbwS6vNQScTiiZFo"
                }
########################### - 15 PUNCTE
2.1. POST /book  (doar pentru Administratori)	ADAUGA O CARTE
	auth_token
	book_name
	book_author
	book_description
    Create a Book:
                {
                    "book_name" : "Pumnalul tainuit",
                    "book_author" : "Phillip Pullman",
                    "book_description" : "Materiile intunecate."
                }
	RETURNEAZA:	id, book_name, book_author, book_description
    RETURNEAZA : id, title, author, description, status, rating, reviews
                {
              "book_author": "Phillip Pullman",
              "book_description": "Materiile intunecate.",
              "book_name": "Pumnalul tainuit",
              "id": 2
                }
2.2. POST /books (doar pentru Administratori) ADAUGA CARTI IN BIBLIOTECA
	auth_token
	books
	RETURNEAZA: books - o lista de obiecte json
2.3. GET /book 
	auth_token (opțional) 
	id
    RETURNEAZA:
                {
                  "book": 2,
                  "book_author": "Phillip Pullman",
                  "book_description": "Materiile intunecate.",
                  "book_name": "Pumnalul tainuit",
                  "book_rating": 0,
                  "book_status": 0,
                  "book_text": null
                }
2.4. GET /books
	books
	RETURNEAZA :	ALL THE BOOKS: 
    CALL : http://127.0.0.1:5000/books2
                {
                  "books": [
                            {
                              "book_author": "Phillip Pullman2",
                              "book_description": "Materiile intunecate2.",
                              "book_name": "Pumnalul tainuit2",
                              "book_rating": 3,
                              "book_status": 0,
                              "book_text": "ceva nou de zis aici si functioneaza!",
                              "id": 1
                            },
                            {
                              "book_author": "Phillip Pullman",
                              "book_description": "Materiile intunecate.",
                              "book_name": "Pumnalul tainuit",
                              "book_rating": 1,
                              "book_status": 0,
                              "book_text": "ceva nou de zis aici!",
                              "id": 2
                            }
                    ]
                }
########################### - 65 PUNCTE
3.1. POST /transaction
	auth_token (opțional) 
	book_id
	borrow_time
    CALL http://127.0.0.1:5000/transaction :
    {
    "book_id" : 2,
    "borrow_time" : 11
    }
	RETURNEAZA : id, "Mesaj de succes"
                {
                  "Succes": "Succes, transaction created for book with id: 2",
                  "transaction_id": 2
                }
Atenție! Un utilizator este limitat la maximum 5 tranzacții într-un moment de timp.
3.2. GET /transaction
	auth_token (opțional)
	transaction_id
	RETURNEAZA : book_id, borrow_time, remaining_time, number_of_extensions, status
                {
                  "book_id": 2,
                  "borrow_time": 11,
                  "number_of_extensions": 0,
                  "remaining_time": 9,
                  "status": 0
                }
Dacă o tranzacție cu id-ul specificat nu există, un mesaj de eroare corespunzător va fi returnat.
3.3. GET /transactions	RETURNEAZA TOATE TRANZACTIILE
	number_of_extensions
	RETURNEAZA : transaction_id, book_id, book_name, status(ALL TRANSACTIONS)

3.4. POST /extend
	auth_token (opțional)
	transaction_id
	extend_time
    CALL http://127.0.0.1:5000/extend2 :
                {
                    "id" : 2,
                    "extend_time" : 1
                }
	RETURNEAZA : "succes"
                {
                  "Succes": "Succes, transaction extended with 1 days.",
                  "transaction_id": 2,
                  "transaction_number_of_extensions": 1
                }

3.5. POST /return
	auth_token (opțional)
	transaction_id
    CALL http://127.0.0.1:5000/return :
                    {
                        "id" : 2
                    }
	RETURNEAZA : "succes" sau mesaje de eroare
                {
                    "Succes": "Succes, return transaction created."
                }
3.6. GET /returns (doar pentru Administratori)
	auth_token (opțional)
	*return_requests - un obiect JSON ce va conține cererile de returnare
	RETURNEAZA : id, transaction_id (ALL TRANSACTIONS, return_id included)

3.7. POST /return/end (doar pentru Administratori)
	auth_token (opțional)
	return_id - id-ul cererii de returnare	
    CALL http://127.0.0.1:5000/return/end 
	RETURNEAZA : "succes" 
                {
                    "Succes": "A review has been DELETED."
                }

3.8. POST /review
	auth_token (opțional)
	book_id
	rating
	text
    CALL http://127.0.0.1:5000/review :
                {
                    "book_id" : 1,
                    "book_rating" : 3,
                    "book_text" : "ceva nou de zis aici si functioneaza!"
                }
	RETURNEAZA : "succes" 
                {
                  "Succes": "A review has been added.",
                  "id": 1,
                  "rating": 3,
                  "text": "ceva nou de zis aici si functioneaza!"
                }
###########################
4.    FORMATARE - 10 PUNCTE
###########################
5.    BONUS - Implemendare db - 20 PUNCTE
