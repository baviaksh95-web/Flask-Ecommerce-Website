from extensions import db
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin # Default implementation of authentication methods  

# To create hashed password this line of code
from werkzeug.security import generate_password_hash,check_password_hash


#db.Model is a database collection in the form of tables
class User(db.Model, UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(100),unique=True,nullable=False)
    email = db.Column(db.String(120),unique=True,nullable=False)
    mobile = db.Column(db.String(20),unique=True,nullable=False)
    password = db.Column(db.String(250),nullable=False) # store hashed password

    
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Product(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    product_name = db.Column(db.String(150),unique=True,nullable=False)
    description = db.Column(db.Text)
    product_price = db.Column(db.Float,nullable = False)
    product_image = db.Column(db.String(200))      # Filename of product image
    category = db.Column(db.String(50))

    def __repr__(self):
        return f'<Product {self.product_name}>'

class Cart(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer, default=1)
    product = db.relationship('Product', backref='cart_items')
    def __repr__(self):
        return f'<User {self.product_id}>'




    



