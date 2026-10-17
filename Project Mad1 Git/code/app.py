import os
import secrets

from flask import Flask
from application.database import db

app=None
def create_app():
    app = Flask(__name__) #__name__ is to refer to any given name of this file
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        "FLUENSE_DATABASE_URL",
        "sqlite:///fsdata.sqlite3",
    )
    app.config['SECRET_KEY'] = os.getenv("FLUENSE_SECRET_KEY") or secrets.token_hex(32)
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, "static", "uploads")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    with app.app_context():
        import application.controllers   # Import routes
        db.create_all()
    #app.app_context().push()    
    return app

app = create_app()

#from application.controllers import *

if __name__=='__main__':
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("FLUENSE_PORT", "5000")),
        debug=os.getenv("FLUENSE_DEBUG", "").lower() in {"1", "true", "yes"},
    )
