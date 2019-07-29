import os
from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import bcrypt
import urllib.request
import json
import textwrap

# APP START
app = Flask(__name__)
app.config["MONGO_DBNAME"] = 'the_book_stop'
app.config["MONGO_URI"] = 'mongodb+srv://root:r00tUser@alphacluster-lqak4.mongodb.net/the_book_stop?retryWrites=true'
mongo = PyMongo(app)

# Google Books API
BASE_API_LINK = 'https://www.googleapis.com/books/v1/volumes?q=title:'

# APP ROUTING START 
# Index
@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template("index.html", genres = mongo.db.genres.find())
    
# Library
@app.route('/library')
def library():
    books = mongo.db.books.find()
    authors = mongo.db.authors.find()
    
    author_ids = []
    updated_books = []
    updated_authors = []
    
    # As mongo cursers cannot be iterated over twice
    # I will create a duplicate books and author dictionary.

    for author in authors:
        updated_authors.append(author)
    for book in books:
        
        # Create a new key/value pair in each book for author_name
        # by looking up the author_id and matching it to the author_name
        # of the selected author_id.
        
        book_title = book['title']
        author_id = book['author_id']
        author_name = ''
        for author in updated_authors:
            if author['_id'] == ObjectId(author_id):
                author_name = author['author_name']
        book['author_name'] = author_name
        
        
        # Using the googlebooks API search for each book and retrieve
        # a thumbnail of the book.
        
        google_api_title = book_title.replace(' ', '+')
        book_isbn_num = book['isbn_num']
        with urllib.request.urlopen(BASE_API_LINK + google_api_title) as f:
            text = f.read()
        decoded_text = text.decode("utf-8")
        obj = json.loads(decoded_text) # deserializes decoded_text to a Python object
        google_book_obj = obj["items"][0]
        book_href = google_book_obj['volumeInfo']
        if 'imageLinks' in book_href:
            book['href'] = book_href['imageLinks']['thumbnail']
        
        # Append book to new book dictionary.
        updated_books.append(book)
    
    return render_template("library.html", books=updated_books, genres=mongo.db.genres.find())

# Search Library
@app.route('/library_search', methods=['POST', 'GET'])
def library_searched():
    books = mongo.db.books
    genres = mongo.db.genres
    authors = mongo.db.authors
    
    updated_books = []
    updated_authors = []
    searched_result = []
    
    # duplicate code from library()
    
    for author in authors.find():
        updated_authors.append(author)
    for book in books.find():
        author_id = book['author_id']
        author_name = ''
        
        for author in updated_authors:
            if author['_id'] == ObjectId(author_id):
                author_name = author['author_name']
        book['author_name'] = author_name 
        
        
        # GOOGLE BOOKS API
        book_title = book['title']
        google_api_title = book_title.replace(' ', '+')
        book_isbn_num = book['isbn_num']
        with urllib.request.urlopen(BASE_API_LINK + google_api_title) as f:
            text = f.read()
        decoded_text = text.decode("utf-8")
        obj = json.loads(decoded_text) # deserializes decoded_text to a Python object
        google_book_obj = obj["items"][0]
        book_href = google_book_obj['volumeInfo']
        if 'imageLinks' in book_href:
            book['href'] = book_href['imageLinks']['thumbnail']
    
        updated_books.append(book)
    
    if request.method == 'POST':
        if request.form['type_search'] == 'book':
            book_title = request.form['search']
            for book in updated_books:
                if book['title'] == book_title:
                    searched_result.append(book)
            return render_template("library_searched.html", result = searched_result)
        elif request.form['type_search'] == 'genre':
            book_genre = request.form['search']
            for book in updated_books:
                if book['genre'] == book_genre:
                    searched_result.append(book)
            return render_template("library_searched.html", result = searched_result)
        elif request.form['type_search'] == 'author':
            book_author = request.form['search']
            for book in updated_books:
                if book['author_name'] == book_author:
                    searched_result.append(book)
            return render_template("library_searched.html", result = searched_result)
    else:
        return render_template("library.html", books=updated_books, genres=mongo.db.genres.find())
        
    return render_template("library_searched.html")
    
# Inserting book
@app.route('/insert_book')
def insert_book():
    _genres=mongo.db.genres.find()
    genre_list = [genre for genre in _genres]
    return render_template('insert_book.html', genres = genre_list)
    
# Submitting book insert
@app.route('/submit_book', methods=['POST'])
def submit_book():
    books = mongo.db.books
    authors = mongo.db.authors
    
    # Create new author in mongo.db.authors
    new_author = authors.insert_one({'author_name': request.form.to_dict()['author_name']})
    author_id = new_author.inserted_id
    
    # Create new book in mongo.db.books
    book = {
        'title': request.form.to_dict()['title'],
        'genre': request.form.to_dict()['genre'],
        'pages': request.form.to_dict()['pages'],
        'reviews': [],
        'likes': [],
        'dislikes': [],
        'author_id': str(ObjectId(author_id)),
        'isbn_num': request.form.to_dict()['isbn_num']
    }
    new_book = books.insert_one(book)
    
    return redirect(url_for('library'))

# Book Review
@app.route('/leave_review/<book_id>')
def leave_review(book_id):
    the_book = mongo.db.books.find_one({'_id': ObjectId(book_id)})
    all_reviews = mongo.db.book.reviews.find()
    
    return render_template('leave_review.html', book=the_book, reviews=all_reviews)
    
# Add Book to Collection
@app.route('/add_collection/<book_id>')
def add_collection(book_id):
    if 'username' in session:
        users = mongo.db.users
        users.update_one(
            {'username' : session['username'] },
            { '$push' : { 'book_collection' : ObjectId(book_id) } }
        )
    flash('A book was just added to your collection!')
    
    return redirect(url_for('library'))
    
@app.route('/remove_collection/<book_id>')
def remove_collection(book_id):
    if 'username' in session:
        users = mongo.db.users
        
        users.update_one(
            {'username' : session['username']},
            {'$pull' : {'book_collection': ObjectId(book_id)}}
        )
    
    return redirect(url_for('user', user_id = session['username']))  

# Submit book review
@app.route('/submit_review/<book_id>', methods=['POST'])
def submit_review(book_id):
    
    # Find a book whom's '_id' == ObjectId(book_id) and push new review to reviews array
    mongo.db.books.find_one_and_update(
        {"_id": ObjectId(book_id)}, 
        {"$push": {"reviews": request.form.to_dict()['reviews']} }
    )
    
    return redirect(url_for('library'))

# User register
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'username' : request.form.to_dict()['username']})
        password = request.form.to_dict()['password']
        username = request.form.to_dict()['username']
        
        if password == '' or username == '':
            error = 'Please enter a username and password'
            return render_template('index.html', genres = mongo.db.genres.find(), error = error)
        elif existing_user is None:
            hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            fav_genre = request.form.to_dict()['genre']
            users.insert_one({
                'username' : request.form.to_dict()['username'], 
                'password' : hashpass, 
                'favourite_genre' : fav_genre,
                'book_collection' : []
            })
            session['username'] = request.form.to_dict()['username']
            return redirect(url_for('index'))
        flash('This username already exists!')

    return render_template('register.html', genres = mongo.db.genres.find())

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    users = mongo.db.users
    username = request.form.to_dict()['username']
    login_user = users.find_one({'username' : username})
    
    if login_user:
        if bcrypt.hashpw(request.form.to_dict()['password'].encode('utf-8'), login_user['password']) == login_user['password']:
            session['username'] = request.form.to_dict()['username']
            user_id = login_user['username']
            return redirect(url_for('user', user_id = user_id ))
        else:
            flash('Invalid username/password combination!')
            return render_template('register.html', genres = mongo.db.genres.find())
    else:
        flash('Invalid username/password combination!')
        
    return render_template('register.html', genres = mongo.db.genres.find())

# User page
@app.route('/user/<user_id>')
def user(user_id):
    if 'username' in session:
        books = mongo.db.books.find()
        the_user = mongo.db.users.find_one({'username': user_id })
        updated_books = []
        books = mongo.db.books.find()
        authors = mongo.db.authors.find()
        author_ids = []
        
        updated_authors = []
        for author in authors:
            updated_authors.append(author)
        for book in books:
            author_id = book['author_id']
            author_name = ''
            
            book_title = book['title']
            
            google_api_title = book_title.replace(' ', '+')
            # print(google_api_title)
            
            book_isbn_num = book['isbn_num']
            
            with urllib.request.urlopen(BASE_API_LINK + google_api_title) as f:
                text = f.read()
            
            decoded_text = text.decode("utf-8")
            obj = json.loads(decoded_text) # deserializes decoded_text to a Python object
            google_book_obj = obj["items"][0]
            book_href = google_book_obj['volumeInfo']
            
            if 'imageLinks' in book_href:
                book['href'] = book_href['imageLinks']['thumbnail']
        
            for author in updated_authors:
                if author['_id'] == ObjectId(author_id):
                    author_name = author['author_name']
                
            book['author_name'] = author_name
    
            updated_books.append(book)
            
        user_book_collection = [] 
        for book in the_user['book_collection']:
            book_id = book
        
            for book in updated_books:
                if book['_id'] == book_id:
                    user_book_collection.append(book)
                    
        genres = mongo.db.genres.find()
        return render_template('user.html', user=the_user, genres=genres, user_book_collection = user_book_collection)
    else:
        return render_template("index.html", genres = mongo.db.genres.find())

# Update user profile button
@app.route('/update_profile/<user_id>', methods=['POST'])
def update_profile(user_id):
        users = mongo.db.users
        users.update_one( {"username": user_id }, 
        { '$set': { 'favourite_genre' : request.form.get('new_genre') } })
        return redirect(url_for('user', user_id = user_id))

# Log out function
@app.route('/end_session')
def end_session():
    session.clear()
    return render_template("index.html", genres = mongo.db.genres.find())
    
# 404 error page
@app.errorhandler(404)
def error_page(e):
    return render_template('error-page.html'), 404

# App Environment
if __name__ == '__main__':
    app.secret_key = 'testkey'
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)