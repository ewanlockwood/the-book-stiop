import os
from flask import Flask, render_template, redirect, request, url_for, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import bcrypt


# APP START
app = Flask(__name__)
app.config["MONGO_DBNAME"] = 'the_book_stop'
app.config["MONGO_URI"] = 'mongodb+srv://root:r00tUser@alphacluster-lqak4.mongodb.net/the_book_stop?retryWrites=true'

mongo = PyMongo(app)

# APP ROUTING START 

# Index
@app.route('/')
@app.route('/index')
def index():
    if 'username' in session:
        print(session['username'])
    return render_template("index.html", genres=mongo.db.genres.find())
    
# Library
@app.route('/library')
def library():
    print('hello')
    books = mongo.db.books.find()
    authors = mongo.db.authors.find()
    author_ids = []
    updated_books = []
    # METHOD 1: Copy books into new array then manipulate that array
    # METHOS 2: 
    
    # If author['_id'] == book['author_id'] book['author_name'] == author['author_name']
    updated_authors = []
    for author in authors:
        updated_authors.append(author)
    
    # print(updated_authors)
    
    for book in books:
        author_id = book['author_id']
        author_name = ''
        
        for author in updated_authors:
            if author['_id'] == ObjectId(author_id):
                author_name = author['author_name']
                
        book['author_name'] = author_name # 'Napoleon Hill'
        
        total_likes = 0
    
        updated_books.append(book)
        
        
    # print(updated_books)
    return render_template("library.html", books=updated_books)

# Search Library
@app.route('/library_search', methods=['POST'])
def library_searched():
    if request.method == 'POST':
        x = request.form['search']
    else:
        return redirect(url_for('library'))
        
    return render_template("library_searched.html", search=mongo.db.books.find({ "title": x }))
    
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
    
    # Create new author in Authors
    new_author = authors.insert_one({'author_name': request.form.to_dict()['author_name']})
    author_id = new_author.inserted_id
    book = {
        'title': request.form.to_dict()['title'],
        'genre': request.form.to_dict()['genre'],
        'pages': request.form.to_dict()['pages'],
        'reviews': [],
        'likes': [],
        'dislikes': [],
        'author_id': str(ObjectId(author_id))
    }
    new_book = books.insert_one(book)
    #print(new_book.inserted_id)
    
    return redirect(url_for('library'))

# Book Review
@app.route('/leave_review/<book_id>')
def leave_review(book_id):
    the_book = mongo.db.books.find_one({'_id': ObjectId(book_id)})
    all_reviews = mongo.db.book.reviews.find()
    return render_template('leave_review.html', book=the_book, reviews=all_reviews)

# Submit book review
@app.route('/submit_review/<book_id>', methods=['POST'])
def submit_review(book_id):
    
    # Find a book whom's '_id' == ObjectId(book_id) and pu
    mongo.db.books.find_one_and_update(
        {"_id": ObjectId(book_id)}, 
        {"$push": {"reviews": request.form.to_dict()['reviews']} }
    )
    
    for book in mongo.db.books.find():
        print(book)
        
    return redirect(url_for('library'))

# User register
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'username' : request.form.to_dict()['username']})
        
        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            fav_genre = request.form.to_dict()['genre']
            users.insert_one({'username' : request.form.to_dict()['username'], 'password' : hashpass, 'favourite_genre' : fav_genre })
            session['username'] = request.form.to_dict()['username']
            return redirect(url_for('index'))
            
            
        return ' That username already exists!'
        
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
    
    return 'Invalid username/password combination'
    
    ###
    # if request.method == "POST":
    #     username = request.form.to_dict()['username']
    #     password = request.form.to_dict()['password']
    #     the_user = mongo.db.users.find_one({'username' : username, 'password': password}, {'_id': 1})
    #     user_id = the_user['_id']
    #     the_user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    #     return redirect(url_for('user', user_id = user_id ))
    # else:
    #     return render_template(url_for('library'))

# User page
@app.route('/user/<user_id>')
def user(user_id):
    if 'username' in session:
        the_user = mongo.db.users.find_one({'username': user_id })
        genres = mongo.db.genres.find()
        return render_template('user.html', user=the_user, genres=genres)
    else:
        return render_template('index.html')

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
    return render_template('index.html')


#APP ENVIRONMENT START

if __name__ == '__main__':
    app.secret_key = 'testkey'
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
            
#APP ENVIRONMENT END