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
    return render_template("library.html", books=mongo.db.books.find())
    
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
    books.insert_one(request.form.to_dict())
    return redirect(url_for('insert_book'))
    
    
# APP ROUTING END

#APP ENVIRONMENT START

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
            
#APP ENVIRONMENT END
            
# APP END