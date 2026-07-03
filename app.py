import requests
from flask_login import login_user, logout_user, current_user, login_required
from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import login_user
from extensions import db, login_manager
from models import User,Product,Cart
from config import Config

app = Flask(__name__)

#Config
app.config.from_object(Config)

# Initialise extensions
db.init_app(app)
login_manager.init_app(app)

login_manager.login_view = "login"  # where to redirect if login required
login_manager.login_message_category = "info"

# Add User Loader Function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username = username ).first() #filter_by is a keyword argument in SQLAlchemy
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            login_error = "Invalid Username or Password"
            return render_template('login.html',login_error = login_error)
            
    return render_template("login.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
    
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        mobile = request.form['mobile'].strip()
        password = request.form['password']
        confirm_password = request.form.get('confirm_password', '')

        errors = []

        # Validate email format
        email_pattern = r'^[^@\s]+@[^@\s]+\.[^@\s]+$'
        if not re.match(email_pattern, email):
            errors.append("Please enter a valid email address with @ and a domain, e.g. user@gmail.com.")

        # Validate mobile number format
        if not re.match(r'^\d{10}$', mobile):
            errors.append("Mobile number must be exactly 10 digits.")

        # Validate password strength
        password_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z\d]).{8,}$'
        if password != confirm_password:
            errors.append("Password and confirm password must match.")
        if not re.match(password_pattern, password):
            errors.append("Password must be at least 8 characters long and include 1 uppercase letter, 1 lowercase letter, 1 number, and 1 special character.")

        # Check for existing email and mobile only
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            errors.append("Email already exists.")

        existing_mobile = User.query.filter_by(mobile=mobile).first()
        if existing_mobile:
            errors.append("Mobile number already exists.")

        if errors:
            return render_template('register.html', register_errors=errors, form_data={
                'username': username,
                'email': email,
                'mobile': mobile
            })

        # Create new user
        new_user = User(
            username = username,
            email = email,
            mobile = mobile,
        )
    
        # Password should be hashed for security, calling function set_password in models
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))

    return render_template('register.html')

@app.route('/category/<category_name>')
def category(category_name):
    products = Product.query.filter_by(category=category_name).all()
    return render_template('category.html',products=products,category=category_name)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        product_name = request.form['product_name']
        description = request.form['description']
        product_price = float(request.form['product_price'])
        category = request.form['category']
        product_image = request.form['product_image']

        new_product = Product(
            product_name=product_name,
            description=description,
            product_price=product_price,
            product_image=product_image,
            category=category
        )
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('products'))
    return render_template('add_product.html')

@app.route('/product')
def products():
    products = Product.query.all()
    return render_template("product.html", products=products)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template("product_detail.html", product=product)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    cart_item = Cart.query.filter_by(product_id=product_id).first()
    if cart_item:
        cart_item.quantity += 1
    else:
        new_item = Cart(product_id = product_id, quantity = 1)
        db.session.add(new_item)
    db.session.commit()
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:item_id>')
def remove_from_cart(item_id):
    item = Cart.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('cart'))

@app.route('/increase_quantity/<int:item_id>')
def increase_quantity(item_id):
    item = Cart.query.get_or_404(item_id)
    item.quantity += 1
    db.session.commit()
    return redirect(url_for('cart'))

@app.route('/decrease_quantity/<int:item_id>')
def decrease_quantity(item_id):
    item = Cart.query.get_or_404(item_id)
    if item.quantity > 1:
        item.quantity -= 1
    else:
        db.session.delete(item)

    db.session.commit()
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    items = Cart.query.all()
    return render_template('cart.html', items=items)


@app.route('/search')
def search():
    query = request.args.get('query')

    if query:
        products = Product.query.filter(
            Product.product_name.ilike(f"%{query}%")
        ).all()
    else:
        products = []

    return render_template("search.html", products = products, query = query)

with app.app_context():
    products = Product.query.all()
    print(products)

if __name__=="__main__":
    app.run(debug=True)