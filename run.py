import os
import json
import urllib.request

from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import bcrypt
import textwrap


# APP START
# Congfiguration of MongoDB with PyMongo.
app = Flask(__name__)
app.config["MONGO_DBNAME"] = 'the_book_stop'
app.config["MONGO_URI"] = 'mongodb+srv://root:r00tUser@alphacluster-lqak4.mongodb.net/the_book_stop?retryWrites=true'
mongo = PyMongo(app)


# Global Google Books API Constant.
BASE_API_LINK = 'https://www.googleapis.com/books/v1/volumes?q=title:'


@app.route('/', methods=['POST', 'GET'])
def index():
    """Render index.html and return a list of all genres in the database"""
    
    return render_template("index.html", genres=mongo.db.genres.find())


def duplicated_code():
    """Re-usable code for accessing all books and authors.
    
    Function name no fixed, dont know what to call it at this moment.
    """
    author_ids = []
    updated_books = []
    updated_authors = []
    
    for author in mongo.db.authors.find():
        updated_authors.append(author)
    for book in mongo.db.books.find():
        
        # Create a new key/value pair in each book for author_name
        # by looking up the author_id and matching it to the author_name
        # of the selected author_id.
        
        book_title = book['title']
        author_id = book['author_id']
        
        for author in updated_authors:
            if author['_id'] == ObjectId(author_id):
                book['author_name'] = author['author_name']
        
        
        # Using the googlebooks API search for each book and retrieve
        # a thumbnail of the book.
        
        google_api_title = book_title.replace(' ', '+')
        book_isbn_num = book['isbn_num']
        with urllib.request.urlopen(BASE_API_LINK + google_api_title) as f:
            text = f.read()
        decoded_text = text.decode("utf-8")
        obj = json.loads(decoded_text) 
        google_book_obj = obj["items"][0]
        book_href = google_book_obj['volumeInfo']
        if 'imageLinks' in book_href:
            book['href'] = book_href['imageLinks']['thumbnail']
        
        # Append book to new book dictionary.
        updated_books.append(book)
        
    return updated_books
        
        
@app.route('/library')
def library():
    """Renders library.html."""
    
    return render_template("library.html", books=duplicated_code(), genres=mongo.db.genres.find())
    
    
@app.route('/library_search', methods=['POST', 'GET'])
def library_searched():
    """Get results from the form and render matched results in library_searched.html."""

    searched_result = []
    
    updated_books = duplicated_code()

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
        return render_template("library_searched.html")
    

@app.route('/insert_book', methods=['POST', 'GET'])
def insert_book():
    """Get all genres and retrieve form data insert new book into database."""
    

    if request.method == 'POST':
        new_author = mongo.db.authors.insert_one({
                'author_name': request.form.to_dict()['author_name']
            })
        
        author_id = new_author.inserted_id
        
        # Create new book in mongo.db.books
        new_book = mongo.db.books.insert_one({
            'title': request.form.to_dict()['title'],
            'genre': request.form.to_dict()['genre'],
            'pages': request.form.to_dict()['pages'],
            'reviews': [],
            'likes': [],
            'dislikes': [],
            'author_id': str(ObjectId(author_id)),
            'isbn_num': request.form.to_dict()['isbn_num']
        })
        
        return redirect(url_for('library'))
        
    return render_template('insert_book.html', 
            genres=[genre for genre in mongo.db.genres.find()])
    

@app.route('/leave_review/<book_id>', methods=['POST', 'GET'])
def leave_review(book_id):
    """Find a book, return all reviews and update the book review with form data."""
    
    if request.method == 'POST':
        mongo.db.books.find_one_and_update(
            {"_id": ObjectId(book_id)}, 
            {"$push": {"reviews": request.form.to_dict()['reviews']} }
        )
        return redirect(url_for('library'))
    
    else:
        return render_template('leave_review.html', 
            book=mongo.db.books.find_one({'_id': ObjectId(book_id)}),
                                        reviews=mongo.db.books.reviews.find())
        
    

@app.route('/add_collection/<book_id>')
def add_collection(book_id):
    """Add a book to user's book collection."""
    
    if 'username' in session:
        mongo.db.users.update_one(
            {'username' : session['username'] },
            { '$push' : { 'book_collection' : ObjectId(book_id) } }
        )
    flash('A book was just added to your collection!')
    
    return redirect(url_for('library'))
    
    
@app.route('/remove_collection/<book_id>')
def remove_collection(book_id):
    """Remove a book to user's book collection."""
     
    if 'username' in session:
        mongo.db.users.update_one(
            {'username' : session['username']},
            {'$pull' : {'book_collection': ObjectId(book_id)}}
        )
        
        return redirect(url_for('user', user_id=session['username']))  


@app.route('/register', methods=['POST', 'GET'])
def register():
    """Register user into database."""
    
    if request.method == 'POST':
        existing_user = mongo.db.users.find_one({'username' : request.form['username']})
        password = request.form['password']
        username = request.form['username']
        
        if password == '' or username == '':
            error = 'Please enter a username and password'
            return render_template('index.html', 
                                    genres=mongo.db.genres.find(), 
                                    error=error)
                                    
        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            fav_genre = request.form['genre']
            mongo.db.users.insert_one({
                'username' : request.form['username'], 
                'password' : hashpass, 
                'favourite_genre' : fav_genre,
                'book_collection' : []
            })
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        else:
            flash('This username already exists!')

    return render_template('register.html', genres=mongo.db.genres.find())


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Match form data with user database data and if match log in"""
    
    username = request.form['username']
    login_user = mongo.db.users.find_one({'username' : username})
    
    if login_user:
        if bcrypt.checkpw(request.form['password'].encode('utf-8'), 
                        login_user['password']):
            session['username'] = request.form.to_dict()['username']
            user_id = login_user['username']
            return redirect(url_for('user', user_id = user_id ))
        else:
            flash('Invalid username/password combination!')
            return render_template('register.html', genres=mongo.db.genres.find())
    else:
        flash('Invalid username/password combination!')
        
    return render_template('register.html', genres=mongo.db.genres.find())


@app.route('/user/<user_id>', methods=['GET', 'POST'])
def user(user_id):
    """Display all data in the user collection in the database."""
    
    if request.method == 'GET':
        if 'username' in session:
            the_user = mongo.db.users.find_one({'username': user_id })
            updated_books = duplicated_code()
                
            user_book_collection = [] 
            for book in the_user['book_collection']:
                book_id = book
            
                for book in updated_books:
                    if book['_id'] == book_id:
                        user_book_collection.append(book)
                        
            return render_template('user.html', user=the_user, genres=mongo.db.genres.find(), user_book_collection = user_book_collection)
        else:
            return render_template("index.html", genres=mongo.db.genres.find())
    elif request.method == 'POST':
        mongo.db.users.update_one( {"username": user_id }, 
        { '$set': { 'favourite_genre' : request.form.get('new_genre') } })
        return redirect(url_for('user', user_id=user_id))


@app.route('/end_session')
def end_session():
    """End session."""
    
    session.clear()
    return render_template("index.html", genres=mongo.db.genres.find())
    

@app.errorhandler(404)
def error_page(e):
    """Handle 404 by rendering error-page.html."""
    
    return render_template('error-page.html'), 404


# App Environment
if __name__ == '__main__':
    app.secret_key = 'testkey'
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)