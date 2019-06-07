# IMPORT START

import os
from flask import Flask, render_template, redirect, request, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

# IMPORT END

# APP START
app = Flask(__name__)
app.config["MONGO_DBNAME"] = 'the_book_stop'
app.config["MONGO_URI"] = 'mongodb+srv://root:r00tUser@alphacluster-lqak4.mongodb.net/the_book_stop?retryWrites=true'

mongo = PyMongo(app)

# APP ROUTING START 

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html", genres=mongo.db.genres.find())

@app.route('/sign_up', methods=['POST'])
def sign_up():
    users = mongo.db.users
    users.insert_one(request.form.to_dict())
    return redirect(url_for('index'))
    
@app.route('/library')
def library():
    
    books = mongo.db.books.find()
    authors = mongo.db.authors.find()
    
    # For each author in each book create a new author document in 'Authors'
    updated_books = []

    # For each book document in the_book_stop.books
    for book in books:
        
        print(book)
        # Create a variable equal to the author_id of each book
        author_id = book['author_id'] # '5abcdef75903764hgd'
        # author_ids = book['author_ids'] # '[5abcdef75903764hgd, 5abcdef75903764hgd, 5abcdef75903764hgd]'
        
        
        # Create a variable that creates an author_name key in each book
        # if the _id in each author equals author_id in book.
        author_name = [ author['author_name'] for author in authors if author['_id'] == ObjectId(author_id)][0]
        print(author_name)
        book['author_name'] = author_name
        
        if book['likes'] == []:
            book['likes'] = 0;
        if book['dislikes'] == []:
            book['dislikes'] = 0;
        
        print(book)
        
        updated_books.append(book)
    return render_template("library.html", books=updated_books)
    
@app.route('/leave_review/<book_id>')
def leave_review(book_id):
    the_book = mongo.db.books.find_one({'_id': ObjectId(book_id)})
    all_reviews = mongo.db.book.reviews.find()
    return render_template('leave_review.html', book=the_book, reviews=all_reviews)
    
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

@app.route('/library_search', methods=['POST'])
def library_searched():
    if request.method == 'POST':
        x = request.form['search']
    else:
        return redirect(url_for('library'))
        
    return render_template("library_searched.html", search=mongo.db.books.find({ "title": x }))
    
@app.route('/insert_book')
def insert_book():
    _genres=mongo.db.genres.find()
    genre_list = [genre for genre in _genres]
    return render_template('insert_book.html', genres = genre_list)
    
@app.route('/submit_book', methods=['POST'])
def submit_book():
    books = mongo.db.books
    
    # Create new author in Authors
    new_author = mongo.db.authors.insert_one({'author_name': request.form.to_dict()['author_name']})
    author_id = new_author.inserted_id
    book = {
        'title': request.form.to_dict()['title'],
        'genre': request.form.to_dict()['genre'],
        'pages': request.form.to_dict()['pages'],
        'reviews': [],
        'likes': [],
        'dislikes': [],
        'author_id': author_id
    }
    new_book = books.insert_one(book)
    #print(new_book.inserted_id)
    
    return redirect(url_for('library'))
    
# APP ROUTING END

#APP ENVIRONMENT START

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
            
#APP ENVIRONMENT END
            
# APP END