from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename
import array as arr
import os
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Blueprint, request, render_template, \
    jsonify, g, session, redirect, make_response

PATH = os.getcwd()
UPLOAD_FOLDER = "/uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookIt.db'
db = SQLAlchemy(app)



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class Book(db.Model):
    book_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    edition = db.Column(db.Integer, nullable=False, default=1)
    sale = db.Column(db.Integer, nullable=False, default=0)
    price = db.Column(db.Float, nullable=False, default=25)
    total_number = db.Column(db.Integer, nullable=False)
    author = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)

    subTotal = 0
    curAmount = 0

    # photo_path = db.Column(db.String(100), nullable=False, default="")
    # photo should exist as a column as well

    def __repr__(self):
        return '<Book %r>' % self.book_id


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), default="test User", nullable=False)
    password = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(50), default="Sogutozu St. TOBB ETU, Ankara Turkey", nullable=False)
    phone = db.Column(db.String(50), default="+905067350522", nullable=False)
    email = db.Column(db.String(50), default="testuser@testaccount.com", nullable=False)

    def __repr__(self):
        return '<User %r>' % self.user_id


class UserOrder(db.Model):
    user_order_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False)

    userID = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<UserOrder %r>' % self.user_order_id


class Order(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    amount = db.Column(db.Float, nullable=False)

    userID = db.Column(db.Integer, nullable=False)
    bookID = db.Column(db.Integer, nullable=False)

    userOrderID = db.Column(db.Integer, nullable=False)

    book_name = db.Column(db.String(100), nullable=True)
    subtotal = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return '<Order %r>' % self.order_id


@app.route('/<int:user_id>/userPage/', methods=['POST', 'GET'])
def userPage(user_id):
    user = User.query.get_or_404(user_id)

    orders = Order.query.order_by(Order.order_id).all()

    return render_template('userPage.html', user=user, orders=orders)

@app.route('/lastOrders/<int:user_id>/', methods=['POST', 'GET'])
def lastOrders(user_id):
    order=Order.query.filter(Order.userID == user_id).all()

    for orderX in order:
    	print(orderX.book_name)

    user = User.query.get_or_404(user_id)

    return render_template('lastOrders.html', orders=order ,user=user )

@app.route('/<int:user_id>/', methods=['POST', 'GET'])
def index_user(user_id):
    
    books = Book.query.order_by(Book.book_id).all()
    user = User.query.get_or_404(user_id)

    cart = carts[user.username]

    return render_template('indexUser.html', booksCart=cart, books=books, user=user)


@app.route('/admin', methods=['POST', 'GET'])
def index_admin():
    if request.method == 'POST':
        book_name = request.form['name']
        book_edition = request.form['edition']
        book_sale = request.form['sale']
        book_price = request.form['price']
        book_total_number = request.form['total_number']
        book_author = request.form['author']
        book_category = request.form['category']

        # file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        # if file and allowed_file(file.filename):
        #    filename = secure_filename(file.filename)
        #    file.save(os.path.join(PATH + UPLOAD_FOLDER, filename))
        #    Book_photo_path = os.path.join(PATH + UPLOAD_FOLDER, filename)
        # else:
        #    Book_photo_path = ""

        new_book = Book(name=book_name, edition=book_edition, sale=book_sale, price=book_price,
                        total_number=book_total_number, author=book_author, category=book_category)
        
        try:
            db.session.add(new_book)
            db.session.commit()
            return redirect('/admin')
        except:
            return 'There was an issue adding your Book'

    else:
        books = Book.query.order_by(Book.book_id).all()
        return render_template('indexAdmin.html', books=books)


@app.route('/delete/<int:book_id>')
def delete(book_id):
    book_to_delete = Book.query.get_or_404(book_id)

    print(book_to_delete.book_id)
    try:
        db.session.delete(book_to_delete)
        db.session.commit()
        return redirect('/admin')
    except:
        return 'There was a problem deleting that Book'


@app.route('/<int:user_id>/add/<int:book_id>')
def add(user_id, book_id):
    global carts

    books = Book.query.order_by(Book.book_id).all()
    user = User.query.get_or_404(user_id)
    booktoAdd = Book.query.get_or_404(book_id)

    cart = carts[user.username]
    control = 1

    if (len(cart) > 0):
        for book in cart:
            if (book.book_id == book_id):
                book.curAmount = book.curAmount + 1
                control = 0
                break
        if (control == 1):
            booktoAdd.curAmount = booktoAdd.curAmount + 1
            cart.append(booktoAdd)
    elif (len(cart) == 0):
        booktoAdd.curAmount = booktoAdd.curAmount + 1
        cart.append(booktoAdd)

    try:

        return index_user(user.user_id)
    # return render_template('indexUser.html', booksCart= cart, books=books, user=user)

    except:
        return 'There was a problem adding that Book'


@app.route('/<user_id>/remove/<int:book_id>')
def remove(user_id, book_id):
    books = Book.query.order_by(Book.book_id).all()
    user = User.query.get_or_404(user_id)

    global carts

    cart = carts[user.username]

    booktoRemove = Book.query.get_or_404(book_id)

    if (len(cart) > 0):
        for book in cart:
            if (book.book_id == book_id):
                # book.curAmount = 0
                cart.remove(book)
                break
    elif (len(cart) == 0):
        try:
            # db.session.delete(book_to_delete)
            # db.session.commit()
            return render_template('indexUser.html', booksCart=cart, books=books, user=user)
        except:
            return 'There was a problem removing that Book'

    try:
        # db.session.delete(book_to_delete)
        # db.session.commit()
        return render_template('indexUser.html', booksCart=cart, books=books, user=user)
    except:
        return 'There was a problem removing that Book'


@app.route('/update/<int:book_id>', methods=['GET', 'POST'])
def update(book_id):
    if request.method == 'POST':
        book = Book.query.get_or_404(book_id)
        book_name = request.form['name']
        book_edition = request.form['edition']
        book_sale = request.form['sale']
        book_price = request.form['price']
        book_total_number = request.form['total_number']
        book_author = request.form['author']
        book_category = request.form['category']

        try:

            book.name = book_name
            book.edition = book_edition
            book.sale = book_sale
            book.price = book_price
            book.total_number = book_total_number
            book.author = book_author
            book.category = book.category
            db.session.commit()
            return redirect('/admin')
        except:
            return 'There was an issue updating that Book'
    else:
        book = Book.query.get_or_404(book_id)
        tempUser = User(username="userAdmin", email="admin@admin.com", password="admin", name="Admin")
        return render_template('update.html', book=book, user=tempUser)


@app.route('/updateUser/<int:user_id>', methods=['GET', 'POST'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user_username = request.form['name']
        user_address = request.form['address']
        user_email = request.form['email']
        user_phone = request.form['phone']

        change = 0

        if user_username != "":
            user.name = user_username
            change = 1
        if user_email != "":
            user.email = user_email
            change = 1
        if user_phone != "":
            user.phone = user_phone
            change = 1
        if user_address != "":
            user.address = user_address
            change = 1

        try:

            if change == 1:
                db.session.add(user)
                db.session.commit()

            return index_user(user.user_id)
        except:
            return 'There was an issue updating that user'
    else:
        return render_template('userSettings.html', user=user)


@app.route('/<user_id>/payment', methods=['GET'])
def payment(user_id):
    done = 0

    global carts

    user = User.query.get_or_404(user_id)
    cart = carts[user.username]

    for book in cart:
        book.subTotal = book.curAmount * book.price

    total = 0
    for book in cart:
        total += book.subTotal

    try:
        return render_template('Order Page.html', books=cart, user=user, total=total, done=done)
    except:
        return 'There was a problem proceeding to payment that Book'


@app.route('/<user_id>/payment', methods=['POST'])
def payment_done(user_id):
    done = 1
    global carts

    user = User.query.get_or_404(user_id)
    cart = carts[user.username]

    for book in cart:
        book.subTotal = book.curAmount * book.price

    total = 0
    for book in cart:
        total += book.subTotal

    user_order = UserOrder(total_amount=total, userID=user.user_id)

    try:
        db.session.add(user_order)
        db.session.commit()
    except:
        return 'There was a problem adding that UserOrder'

    for book in cart:
        order = Order(amount=book.curAmount, bookID=book.book_id, userID=user.user_id,
                      userOrderID=user_order.user_order_id, book_name=book.name, subtotal=book.subTotal)

        try:
            db.session.add(order)
            db.session.commit()
            book.sale += book.curAmount
            book.total_number -= book.curAmount
            db.session.add(book)
            db.session.commit()
        except:
            return 'There was a problem adding that Order'

    user_address = request.form['address']
    user_email = request.form['email']
    user_phone = request.form['phone']

    change = 0

    if user_email != "":
        user.email = user_email
        change = 1
    if user_phone != "":
        user.phone = user_phone
        change = 1
    if user_address != "":
        user.address = user_address
        change = 1

    try:
        if change == 1:
            db.session.add(user)
            db.session.commit()

        carts[user.username] = []
        return render_template('Order Page.html', books=cart, user=user, total=total, done=done)
    except:
        return 'There was a problem proceeding to payment that Book'


@app.route('/<user_id>/search', methods=['GET', 'POST'])
def search_results(user_id):
    if request.method == 'POST':
        search_string = request.form['search']
        searchBox = request.form.getlist('searchBox')

        global carts

        if (search_string == ""):

            books = Book.query.order_by(Book.book_id).all()
            user = User.query.get_or_404(user_id)
            cart = carts[user.username]
            return render_template('indexUser.html', booksCart=cart, books=books, user=user)
        else:

            if (len(searchBox) == 0):
                return redirect('/')
            elif (len(searchBox) == 1):
                if (searchBox[0] == "1"):
                    Books1 = Book.query.filter(Book.name.like(search_string + "%")).all()
                    BooksFinal = Books1
                elif (searchBox[0] == "2"):
                    Books2 = Book.query.filter(Book.author.like(search_string + "%")).all()
                    BooksFinal = Books2
                elif (searchBox[0] == "3"):
                    Books3 = Book.query.filter(Book.category.like(search_string + "%")).all()
                    BooksFinal = Books3
            elif (len(searchBox) == 2):
                if (searchBox[0] == "1" and searchBox[1] == "2"):
                    Books1 = Book.query.filter(Book.name.like(search_string + "%")).all()
                    Books2 = Book.query.filter(Book.author.like(search_string + "%")).all()
                    BooksFinal = Books1 + Books2
                if (searchBox[0] == "1" and searchBox[1] == "3"):
                    Books1 = Book.query.filter(Book.name.like(search_string + "%")).all()
                    Books3 = Book.query.filter(Book.category.like(search_string + "%")).all()
                    BooksFinal = Books1 + Books3
                if (searchBox[0] == "2" and searchBox[1] == "3"):
                    Books3 = Book.query.filter(Book.author.like(search_string + "%")).all()
                    Books2 = Book.query.filter(Book.category.like(search_string + "%")).all()
                    BooksFinal = Books2 + Books3
            elif (len(searchBox) == 3):
                Books1 = Book.query.filter(Book.name.like(search_string + "%")).all()
                Books2 = Book.query.filter(Book.author.like(search_string + "%")).all()
                Books3 = Book.query.filter(Book.category.like(search_string + "%")).all()
                BooksFinal = Books1 + Books2 + Books3

            books = BooksFinal

        user = User.query.get_or_404(user_id)
        cart = carts[user.username]

        return render_template('indexUser.html', booksCart=cart, books=books, user=user)


@app.route('/searchAdmin', methods=['GET', 'POST'])
def search_results_admin():
    if request.method == 'POST':
        search_string = request.form['search']
        searchBox = request.form.getlist('searchBox')

        if (search_string == ""):

            books = Book.query.order_by(Book.book_id).all()
            return render_template('indexAdmin.html', books=books)
        else:

            if (len(searchBox) == 0):
                return redirect('/')
            elif (len(searchBox) == 1):
                if (searchBox[0] == "1"):
                    Books1 = Book.query.filter(Book.name.like(search_string + "%")).all()
                    BooksFinal = Books1
                elif (searchBox[0] == "2"):
                    Books2 = Book.query.filter(Book.author.like(search_string + "%")).all()
                    BooksFinal = Books2
                elif (searchBox[0] == "3"):
                    Books3 = Book.query.filter(Book.category.like(search_string + "%")).all()
                    BooksFinal = Books3
            elif (len(searchBox) == 2):
                if (searchBox[0] == "1" and searchBox[1] == "2"):
                    Books1 = Book.query.filter(Book.name.like(search_string + "%")).all()
                    Books2 = Book.query.filter(Book.author.like(search_string + "%")).all()
                    BooksFinal = Books1 + Books2
                if (searchBox[0] == "1" and searchBox[1] == "3"):
                    Books1 = Book.query.filter(Book.name.like(search_string + "%")).all()
                    Books3 = Book.query.filter(Book.category.like(search_string + "%")).all()
                    BooksFinal = Books1 + Books3
                if (searchBox[0] == "2" and searchBox[1] == "3"):
                    Books3 = Book.query.filter(Book.author.like(search_string + "%")).all()
                    Books2 = Book.query.filter(Book.category.like(search_string + "%")).all()
                    BooksFinal = Books2 + Books3
            elif (len(searchBox) == 3):
                Books1 = Book.query.filter(Book.name.like(search_string + "%")).all()
                Books2 = Book.query.filter(Book.author.like(search_string + "%")).all()
                Books3 = Book.query.filter(Book.category.like(search_string + "%")).all()
                BooksFinal = Books1 + Books2 + Books3

            books = BooksFinal

        return render_template('indexAdmin.html', books=books)


# Set the route and accepted methods
@app.route('/login', methods=['GET'])
def login_page():
    return render_template('Login.html')


@app.route('/register', methods=['GET'])
def register_page():
    return render_template('Register.html')


@app.route('/login', methods=['POST'])
def login():
    data = request.form
    username = data['username']
    password = data['password']

    user = User.query.filter_by(username=username).first()

    if not user:
        return make_response('User not found', 401)
    if (password == user.password):
        return index_user(user.user_id)
        # return index_user(user.user_id)
    else:
        return make_response('Password is incorrect', 401)


# endpoint to create new user
@app.route('/signup', methods=['POST'])
def add_user():
    global carts

    cart = []

    data = request.form
    username = data['username']
    email = data['email']
    password = data['password']

    name = data['name']
    hashed_password = generate_password_hash(password, method='sha256')
    new_user = User(username=username, email=email, password=password, name=name)

    carts[new_user.username] = cart

    db.session.add(new_user)
    db.session.commit()

    return redirect('/login')


if __name__ == "__main__":
    users = User.query.order_by(User.user_id).all()
    carts = {}

    for user in users:
    	username = user.username
    	carts[username] = []
    

    app.run(debug=True)


