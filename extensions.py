from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialize SQLAlchemy
db = SQLAlchemy() # ORM  Access

# Initialize LoginManager
login_manager = LoginManager() # Login Access 
