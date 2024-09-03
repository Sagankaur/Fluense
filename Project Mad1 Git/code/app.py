from flask import Flask
from application.database import db

app=None
def create_app():
    app = Flask(__name__) #__name__ is to refer to any given name of this file
    app.debug= True
    app.config['SQLALCHEMY_DATABASE_URI']= "sqlite:///fsdata.sqlite3"


    db.init_app(app)
    with app.app_context():
        import application.controllers   # Import routes
        db.create_all()
    #app.app_context().push()    
    return app

app = create_app()

#from application.controllers import *

if __name__=='__main__':
    app.run()