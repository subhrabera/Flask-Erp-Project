from flask import Flask, render_template, session, redirect, url_for, request, flash, jsonify, make_response
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import pdfkit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/subhra/Desktop/ERP/database.db'

#Initialize essential objects
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    # active = db.Column(db.String(10),nullable=False,default=0)

# class Admin(UserMixin, db.Model):
#     __tablename__ = 'admins'
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(15), unique=True)
#     email = db.Column(db.String(50), unique=True)
#     password = db.Column(db.String(80))
#     passwordshow = db.Column(db.String(80))

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(15), unique=True)
    status = db.Column(db.Boolean, default=0) 
    created_on = db.Column(db.DateTime, server_default=db.func.now())

    def __init__(self, category_name):

        self.category_name = category_name

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), unique=True)
    ref_no = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False) 
    s_qty = db.Column(db.Float, nullable=False)
    unit = db.Column(db.Float, nullable=False)
    status = db.Column(db.Boolean, default=0)
    created_on = db.Column(db.DateTime, server_default=db.func.now())

    def __init__(self, name, ref_no,  price, s_qty, unit):

        self.name = name
        self.ref_no = ref_no
        self.price = price
        self.s_qty = s_qty
        self.unit = unit

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), unique=True)
    mobile_number = db.Column(db.Integer, nullable=False)
    gstin = db.Column(db.Integer, nullable=True)
    address = db.Column(db.String(150), nullable=False)
    activation = db.Column(db.Boolean, default=0)
    created_on = db.Column(db.DateTime, server_default=db.func.now())

    def __init__(self, name, mobile_number, gstin, address):

        self.name = name
        self.mobile_number = mobile_number
        self.gstin = gstin
        self.address = address

class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    category_name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    point = db.Column(db.Float, nullable=False)
    emp_name = db.Column(db.String(225), nullable=False)
    duration = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Boolean, default=0)
    created_on = db.Column(db.DateTime, server_default=db.func.now())

    def __init__(self, name, category_name, price, point, emp_name, duration, description):

        self.name = name
        self.category_name = category_name
        self.price = price
        self.point = point
        self.emp_name = emp_name
        self.duration = duration
        self.description = description

class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    speciality = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(80), nullable=False)
    from_hours = db.Column(db.String(255), nullable=False)
    to_hours = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Boolean, default=0)
    created_on = db.Column(db.DateTime, server_default=db.func.now())

    def __init__(self, name, speciality, email, from_hours, to_hours):

        self.name = name
        self.speciality = speciality
        self.email = email
        self.from_hours = from_hours
        self.to_hours = to_hours

class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    emp_name = db.Column(db.String(255), nullable=False)
    datepick = db.Column(db.DateTime, server_default=db.func.now())
    appointment_time = db.Column(db.String(255), nullable=False)
    internal_note = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Boolean, default=0)
    created_on = db.Column(db.DateTime, server_default=db.func.now())

    def __init__(self, name, emp_name, datepick, appointment_time, internal_note):

        self.name = name
        self.emp_name = emp_name
        self.datepick = datepick
        self.appointment_time = appointment_time
        self.internal_note = internal_note


class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(
        message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[
                           InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[
                             InputRequired(), Length(min=8, max=80)])

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('frontend/index.html')

# @app.route('/')
# def index():
#     return redirect(url_for('login'))

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(
            email=request.values.get('username')).first()
        if user:
            if check_password_hash(user.password, request.values.get('password')):
                login_user(user)
                return jsonify(success=True, msg="You have successfully logged in", url='dashboard')
            else:
                return jsonify(success=False, msg="Incorrect username or password")
        else:
            return jsonify(success=False, msg="Invalid username or password")
    return render_template('frontend/login.html')

@app.route('/register/', methods=['GET', 'POST'])
def register():
    # if request.method == 'POST':

    return render_template('frontend/register.html')

# @app.route('/userlogin/', methods=['GET', 'POST'])
# def userlogin():
#     if request.method == 'POST':
#         user = User.query.filter_by(
#             email=request.values.get('username')).first()
#         if user:
#             if check_password_hash(user.password, request.values.get('password')):
#                 login_user(user)
#                 print("hello")
#                 a = user.active
#                 print(a)
#                 print(type(a))
#                 b = 0
#                 print(b)
#                 if b == 0:
#                     print("hello2")
#                     return jsonify(success=True, msg="You have successfully logged in", url='userdashboard')
#                 else:
#                     return jsonify(success=True, msg="Wait for your Approval")
#             else:
#                 return jsonify(success=False, msg="Incorrect username or password")
#         else:
#             return jsonify(success=False, msg="Invalid username or password")
#     return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(
            form.password.data, method='sha256')
        new_user = User(username=form.username.data,
                        email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return '<h1>New user has been created!</h1>'
    return render_template('signup.html', form=form)

@app.route('/forgot_password/')
def forgotpassword():
    return render_template('frontend/forgot_password.html')

@app.route('/dashboard/')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)


@app.route('/logout/')
@login_required  # decorator
def logout():
    logout_user()
    return redirect(url_for('login'))

# start sales part
@app.route("/customers/")
@login_required
def customers():
    all_data = Customer.query.all()
    return render_template("sales/customers.html", customers=all_data, name=current_user.username)


@app.route('/insert', methods=['POST'])
@login_required
def insert():
    if request.method == 'POST':
        name = request.form['name']
        mobile_number = request.form['mobile_number']
        gstin = request.form['gstin']
        address = request.form['address']
        my_data = Customer(name, mobile_number, gstin, address)
        db.session.add(my_data)
        db.session.commit()
        flash("Customer Inserted Successfully")
        return redirect(url_for('customers'))


@app.route("/customers/update/", methods=["POST", "GET"])
@login_required
def update():
    customer = Customer.query.filter_by(id=request.args.get('id')).first()
    # print(customer)
    customer.name = request.form.get("name")
    customer.mobile_number = request.form.get("mobile_number")
    customer.gstin = request.form.get("gstin")
    customer.address = request.form.get("address")
    db.session.commit()
    return redirect(url_for('customers'))

@app.route("/customers/activation/", methods=["POST", "GET"])
@login_required
def customeractivation():
    customer = Customer.query.filter_by(id=request.args.get('id')).first()
    if customer.activation:
        customer.activation = False
        db.session.commit()
    else:
        customer.activation = True
        db.session.commit()
    return redirect(url_for('customers'))

@app.route("/sales-order/")
@login_required
def stock():
    all_data = Product.query.all()
    customer = Customer.query.all()
    return render_template("sales/sales-order.html", products=all_data, customers=customer, name=current_user.username)

# start inventory part
@app.route("/category/")
@login_required
def category():
    all_data = Category.query.all()
    return render_template("inventory/category.html", category=all_data, name=current_user.username)

@app.route("/categoryinsert", methods=['POST'])
@login_required
def categoryinsert():
    if request.method == 'POST':
        category_name = request.form['category_name']
        my_data = Category(category_name)
        db.session.add(my_data)
        db.session.commit()
        flash("Category Inserted Successfully")
        return redirect(url_for('category'))

@app.route("/category/update/", methods=["POST", "GET"])
@login_required
def categoryupdate():
    category = Category.query.filter_by(id=request.args.get('id')).first()
    category.category_name = request.form.get("category_name")
    db.session.commit()
    return redirect(url_for('category'))

@app.route("/category/status/", methods=["POST", "GET"])
@login_required
def categorydelete():
    category = Category.query.filter_by(id=request.args.get('id')).first()
    if category.status:
        category.status = False
        db.session.commit()
    else:
        category.status = True
        db.session.commit()
    return redirect(url_for('category'))

@app.route("/products/")
@login_required
def products():
    all_data = Product.query.all()
    return render_template("inventory/products.html", products=all_data, name=current_user.username)

@app.route('/productinsert', methods=['POST'])
@login_required
def productinsert():
    if request.method == 'POST':
        name = request.form['name']
        ref_no = request.form['ref_no']
        price = request.form['price']
        s_qty = request.form['s_qty']
        unit = request.form['unit']
        my_data = Product(name, ref_no, price, s_qty, unit)
        db.session.add(my_data)
        db.session.commit()
        flash("Product Inserted Successfully")
        return redirect(url_for('products'))

@app.route("/product/update/", methods=["POST", "GET"])
@login_required
def productupdate():
    product = Product.query.filter_by(id=request.args.get('id')).first()
    product.name = request.form.get("name")
    product.ref_no = request.form.get("ref_no")
    product.price = request.form.get("price")
    product.s_qty = request.form.get("s_qty")
    product.unit = request.form.get("unit")
    db.session.commit()
    return redirect(url_for('products'))

@app.route("/product/status/", methods=["POST", "GET"])
@login_required
def productdelete():
    product = Product.query.filter_by(id=request.args.get('id')).first()
    if product.status:
        product.status = False
        db.session.commit()
    else:
        product.status = True
        db.session.commit()
    return redirect(url_for('products'))

@app.route("/services/")
@login_required
def services():
    all_service = Service.query.all()
    all_data = Category.query.all()
    emp = Employee.query.all()
    return render_template("inventory/services.html",service=all_service, category=all_data, employee=emp, name=current_user.username)

@app.route('/serviceinsert', methods=['POST'])
@login_required
def serviceinsert():
    if request.method == 'POST':
        name = request.form['name']
        category_name = request.form['category_name']
        price = request.form['price']
        point = request.form['point']
        emp_name = request.form['emp_name']
        duration = request.form['duration']
        description = request.form['description']
        my_data = Service(name, category_name, price, point, emp_name, duration, description)
        db.session.add(my_data)
        db.session.commit()
        flash("Service Inserted Successfully")
        return redirect(url_for('services'))

@app.route("/service/update/", methods=["POST", "GET"])
@login_required
def serviceupdate():
    service = Service.query.filter_by(id=request.args.get('id')).first()
    service.name = request.form.get("name")
    service.category_name = request.form.get("category_name")
    service.price = request.form.get("price")
    service.point = request.form.get("point")
    service.emp_name = request.form.get("emp_name")
    service.duration = request.form.get("duration")
    service.description = request.form.get("description")
    db.session.commit()
    return redirect(url_for('services'))

@app.route("/service/status/", methods=["POST", "GET"])
@login_required
def servicedelete():
    service = Service.query.filter_by(id=request.args.get('id')).first()
    if service.status:
        service.status = False
        db.session.commit()
    else:
        service.status = True
        db.session.commit()
    return redirect(url_for('services'))

@app.route("/invoice-cal", methods=["POST"])
@login_required
def getdata():
    print("hello")
    customer = request.form.get('customer')
    customer = Customer.query.filter_by(id=customer).first()
    print(customer)
    data = {'success' : True,'address' : str(customer.address)}
    return jsonify(data)

@app.route("/invoicing/")
@login_required
def invoicing():
    all_data = Product.query.all()
    # orders = Orders.query.all()
    return render_template("sales/invoicing.html",products=all_data, name=current_user.username)

@app.route("/invoicing/create/")
@login_required
def create_invoice():
    all_data = Customer.query.all()
    services = Service.query.all()
    return render_template("sales/create_invoice.html", customers=all_data, services=services, name=current_user.username)

@app.route("/invoicing/edit/")
@login_required
def edit_invoice():
    return render_template("sales/edit_invoice.html")

@app.route("/invoicing/view/")
@login_required
def view_invoice():
    return render_template("sales/invoice_view.html")

# @app.route("/invoicing/delete/")
# @login_required
# def view_invoice():
#     return render_template("sales/invoice-view.html")

@app.route("/payments/")
@login_required
def payment():
    return render_template("sales/payments.html")

@app.route("/employee/")
@login_required
def employee():
    all_data = Employee.query.all()
    return render_template("employee.html", employee=all_data, name=current_user.username)
    # return render_template("employee.html")

@app.route('/employeeinsert', methods=['POST'])
@login_required
def employeeinsert():
    if request.method == 'POST':
        name = request.form['name']
        speciality = request.form['speciality']
        email = request.form['email']
        from_hours = request.form['from_hours']
        to_hours = request.form['to_hours']
        my_data = Employee(name, speciality, email, from_hours, to_hours)
        db.session.add(my_data)
        db.session.commit()
        flash("Employee Inserted Successfully")
        return redirect(url_for('employee'))

@app.route("/employee/update/", methods=["POST", "GET"])
@login_required
def employeeupdate():
    employee = Employee.query.filter_by(id=request.args.get('id')).first()
    employee.name = request.form.get("name")
    employee.speciality = request.form.get("speciality")
    employee.email = request.form.get("email")
    employee.from_hours = request.form.get("from_hours")
    employee.to_hours = request.form.get("to_hours")
    db.session.commit()
    return redirect(url_for('employee'))

@app.route("/employee/status/", methods=["POST", "GET"])
@login_required
def employeedelete():
    employee = Employee.query.filter_by(id=request.args.get('id')).first()
    if employee.status:
        employee.status = False
        db.session.commit()
    else:
        employee.status = True
        db.session.commit()
    return redirect(url_for('employee'))

@app.route("/Appointment/")
@login_required
def appointment():
    return render_template("Appointment.html")

if __name__ == '__main__':
    app.run(debug=True)


# extra calculation 
# @app.route("/getorder")
# @login_required
# def get_order():
#     if current_user.is_authenticated:
#         customer_id = current_user.id
#         invoice = secrets.token_hex(5)
#         try:
#             order = CustomerOrder(invoice=invoice, customer_id=customer_id, orders=session['Shoppingcart'])
#             db.session.add(order)
#             db.session.commit()
#             session.pop('Shoppingcart')
#             flash('Your order has been sent successfully', 'success')
#             return redirect(url_for('orders', invoice=invoice))
#         except Exception as e:
#             print(e)
#             flash('Some thing went wrong while get order', 'danger')
#             return redirect(url_for('getCart'))

# @app.route("/orders/<invoice>")
# @login_required
# def orders(invoice):
#     if current_user.is_authenticated:
#         grandTotal = 0
#         subTotal = 0
#         customer_id = current_user.id
#         customer = Register.query.filter_by(id=customer_id).first()
#         orders = CustomerOrder.query.filter_by(customer_id=customer_id).order_by(CustomerOrder.id.des()).first()
#         for _key, product in orders.orders.items():
#             discount = (product['discount']/100) * float(product['price'])
#             subTotal += float(product['price']) * int(product['quantity'])
#             subTotal = discount
#             tax = ("%.2f" % (.06 * float(subTotal)))
#             grandTotal = float("%.2f" % (1.06 * subTotal))
#     else:
#         return redirect(url_for('customerLogin'))
#     return render_template('customer/order.html', invoice=invoice, tax=tax, subTotal=subTotal, grandTotal=grandTotal, customer=customer, orders=orders)   

# @app.route("/get_pdf/<invoice>", methods=['POST'])
# @login_required
# def get_pdf(invoice):
#     if current_user.is_authenticated:
#         grandTotal = 0
#         subTotal = 0
#         customer_id = current_user.id
#         if request.method == "POST":
#             customer = Register.query.filter_by(id=customer_id).first()
#             orders = CustomerOrder.query.filter_by(customer_id=customer_id).order_by(CustomerOrder.id.des()).first()
#             for _key, product in orders.orders.items():
#                 discount = (product['discount']/100) * float(product['price'])
#                 subTotal += float(product['price']) * int(product['quantity'])
#                 subTotal = discount
#                 tax = ("%.2f" % (.06 * float(subTotal)))
#                 grandTotal = float("%.2f" % (1.06 * subTotal))
    
#             rendered = render_template('customer/pdf.html', invoice=invoice, tax=tax, grandTotal=grandTotal, customer=customer, orders=orders)
#             pdf = pdfkit.from_string(rendered, False)
#             response = make_response(pdf)
#             response.headers['content-Type']='application/pdf'
#             response.headers['content-Disposition']='atteched; filename='+invoice+'.pdf'
#             return response
#     return request(url_for('orders'))
        
