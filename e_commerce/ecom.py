from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost/ecomerce'  # Mettez votre propre URL de connexion PostgreSQL
db = SQLAlchemy(app)

# Modèles SQLAlchemy
class Product(db.Model):
    __tablename__ = 'products'  # Nom de la table dans la base de données
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    category = db.Column(db.String(100))
    stock_quantity = db.Column(db.Integer, nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': str(self.price),  # Convertir en chaîne pour la sérialisation JSON
            'category': self.category,
            'stock_quantity': self.stock_quantity
        }


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='pending')

    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'order_date': self.order_date.isoformat(),  # Format ISO 8601 pour la date
            'status': self.status
        }





class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'quantity': self.quantity
        }



class CartItem(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'quantity': self.quantity
        }


@app.route('/')
def index():
    return send_from_directory('front-end', 'index.html')

# Routes pour les produits
@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([product.serialize() for product in products])

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404
    return jsonify(product.serialize())

@app.route('/products', methods=['POST'])
def create_product():
    data = request.json
    if 'name' not in data or 'price' not in data:
        return jsonify({'error': 'Name and price are required'}), 400

    name = data.get('name')
    price = data.get('price')
    description = data.get('description')
    category = data.get('category')
    stock_quantity = data.get('stock_quantity')

    try:
        new_product = Product(name=name, price=price, description=description, category=category, stock_quantity=stock_quantity)
        db.session.add(new_product)
        db.session.commit()
        return jsonify({'message': 'Product created successfully'}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404
    data = request.json
    product.name = data.get('name', product.name)
    product.description = data.get('description', product.description)
    product.price = data.get('price', product.price)
    product.category = data.get('category', product.category)
    product.stock_quantity = data.get('stock_quantity', product.stock_quantity)
    db.session.commit()
    return jsonify(product.serialize())

@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted'}), 204

# Routes pour les commandes
from flask import request, jsonify

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.json
    if 'user_id' not in data or 'items' not in data:
        return jsonify({'error': 'User ID and items are required'}), 400

    try:
        # Créer une nouvelle commande
        new_order = Order(user_id=data['user_id'])
        db.session.add(new_order)
        db.session.commit()

        # Enregistrer les détails des produits commandés
        for item in data['items']:
            order_item = OrderItem(order_id=new_order.id, product_id=item['product_id'], quantity=item['quantity'])
            db.session.add(order_item)
        db.session.commit()

        return jsonify({'message': 'Order created successfully'}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/orders/<int:user_id>', methods=['GET'])
def get_user_orders(user_id):
    orders = Order.query.filter_by(user_id=user_id).all()
    return jsonify([order.serialize() for order in orders])

# Routes pour les paniers
@app.route('/cart/<int:user_id>', methods=['POST'])
def add_to_cart(user_id):
    data = request.json
    product_id = data.get('product_id')
    quantity = data.get('quantity')

    if not product_id or not quantity:
        return jsonify({'error': 'Product ID and quantity are required'}), 400

    cart_item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
    db.session.add(cart_item)
    db.session.commit()

    return jsonify({'message': 'Product added to cart'}), 201

@app.route('/cart/<int:user_id>', methods=['GET'])
def get_cart(user_id):
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    return jsonify([item.serialize() for item in cart_items])

@app.route('/cart/<int:user_id>/item/<int:product_id>', methods=['DELETE'])
def remove_from_cart(user_id, product_id):
    cart_item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    if not cart_item:
        return jsonify({'message': 'Item not found in cart'}), 404
    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'message': 'Product removed from cart'}), 204

if __name__ == '__main__':
    app.run(debug=True)