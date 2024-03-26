from flask import Flask
from flask import redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db1 = SQLAlchemy(app)
def to_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0 

app.jinja_env.filters['to_int'] = to_int

class Category(db1.Model):
  id = db1.Column(db1.Integer, primary_key=True, autoincrement=True)
  name = db1.Column(db1.String(100), unique=True, nullable=False)
  products = db1.relationship('Product', backref='category', lazy=True, cascade='all, delete-orphan',)

class Product(db1.Model):
  id = db1.Column(db1.Integer, primary_key=True, autoincrement=True)
  name = db1.Column(db1.String(100), nullable=False)
  scale = db1.Column(db1.String(100), nullable=False)
  std_qty = db1.Column(db1.Integer, nullable=False)
  price = db1.Column(db1.Float, nullable=False)
  stock = db1.Column(db1.Integer, nullable=False)
  category_id = db1.Column(db1.Integer,
                          db1.ForeignKey('category.id'),
                          nullable=False)
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/user_login')
def user_login():
  return render_template('user_login.html')

@app.route('/manager_login')
def manager_login():
  return render_template('manager_login.html')

@app.route('/user_dashboard', methods= ['GET','POST'])
def user_dashboard():
  categories = Category.query.all()
  products = Product.query.all()

  return render_template('user_dashboard.html',
                         categories=categories,
                         pr=products, type=type)
@app.route('/user_dashboard_with_forms', methods=['GET','POST'])
def user_dashboard_with_forms():
  categories= Category.query.all()
  products= Product.query.all()
  num_products=request.form.get('num_products')
    
  return render_template('user_dashboard_with_forms.html', num_products=num_products, categories=categories,
                         pr=products, type=type)

@app.route('/add_category', methods=['POST'])
def add_category():
  category_name = request.form.get('category_name')
  new_category = Category(name=category_name)
  db1.session.add(new_category)
  db1.session.commit()
  return redirect(url_for('manager_dashboard'))

@app.route('/add_product', methods=['POST'])
def add_product():
  name = request.form.get('product_name')
  scale = request.form.get('product_scale')
  q = request.form.get('product_qty')
  p = request.form.get('product_price')
  s = request.form.get('product_stock')
  c_id = request.form.get('product_cat_id')
  new_product = Product(name=name,
                        scale=scale,
                        std_qty=q,
                        price=p,
                        stock=s,
                        category_id=c_id)
  db1.session.add(new_product)
  db1.session.commit()
  return redirect(url_for('manager_dashboard'))

@app.route('/delete_product', methods=['POST'])
def delete_product():
  id=request.form.get('product_id')
  product = Product.query.get_or_404(id)

  db1.session.delete(product)
  db1.session.commit()
  return redirect(url_for('manager_dashboard'))
@app.route('/delete_category', methods=['POST'])
def delete_category():
  id=request.form.get('category_id')
  category = Category.query.get_or_404(id)

  db1.session.delete(category)
  db1.session.commit()
  return redirect(url_for('manager_dashboard'))


@app.route('/manager_dashboard', methods=['GET','POST'])
def manager_dashboard():
  categories = Category.query.all()
  products = Product.query.all()
  return render_template('manager_dashboard.html',
                         categories=categories,
                         pr=products)

@app.route('/cart', methods=['GET','POST'])
def cart():
    selected_products = []
    total_cost = 0.0
    num_products = int(request.form.get('no:of:products'))
    
    for i in range(0, num_products + 1):
        product_id = request.form.get(f'product_id{i}')
        required_qty = request.form.get(f'required_qty{i}')
        product = Product.query.get(product_id)
        
        if product:
            required_qty = float(required_qty)
            product.price = float(product.price)
            selected_products.append({
                'name': product.name,
                'req_qty': required_qty,
                'scale' : product.scale,
                'std_qty' : product.std_qty,
                'price': product.price,
                'subtotal': required_qty * product.price
            })
            total_cost += selected_products[-1]['subtotal']

    return render_template('cart.html',
                           selected_products=selected_products,
                           total_cost=total_cost)

if __name__ == '__main__':
  with app.app_context():
    db1.create_all()
  app.run(debug=True, port=8081)
