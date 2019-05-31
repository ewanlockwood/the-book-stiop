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
    
# APP ROUTING END

#APP ENVIRONMENT START

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
            
#APP ENVIRONMENT END
            
# APP END