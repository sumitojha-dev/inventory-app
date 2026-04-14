import os
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ---------------- DATABASE ----------------
app.config["MONGO_URI"] = os.environ.get(
    "MONGO_URI",
    "mongodb+srv://inventoryuser:inventory123@cluster0.lsotepa.mongodb.net/?retryWrites=true&w=majority"
)
mongo = PyMongo(app)

# ---------------- AUTH ----------------

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    users = mongo.db.users

    if users.find_one({"email": data['email']}):
        return jsonify({"message": "User already exists"}), 400

    hashed_password = generate_password_hash(data['password'])

    users.insert_one({
        "username": data['username'],
        "email": data['email'],
        "password": hashed_password
    })

    return jsonify({"message": "User registered successfully"}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = mongo.db.users.find_one({"email": data['email']})

    if user and check_password_hash(user['password'], data['password']):
        return jsonify({
            "message": "Login successful",
            "user_id": str(user['_id']),
            "username": user['username']
        }), 200

    return jsonify({"message": "Invalid email or password"}), 401


# ---------------- PRODUCTS ----------------

@app.route('/products', methods=['POST'])
def add_product():
    data = request.json

    if int(data['quantity']) < 0:
        return jsonify({"message": "Quantity cannot be negative"}), 400

    product_id = mongo.db.products.insert_one({
        "name": data['name'],
        "price": float(data['price']),
        "quantity": int(data['quantity']),
        "category": data['category']
    }).inserted_id

    return jsonify({"message": "Product added", "id": str(product_id)}), 201


@app.route('/products', methods=['GET'])
def get_products():
    try:
        products = list(mongo.db.products.find())
        for p in products:
            p['_id'] = str(p['_id'])
        return jsonify(products), 200
    except:
        return jsonify([]), 200


@app.route('/products/<id>', methods=['DELETE'])
def delete_product(id):
    mongo.db.products.delete_one({'_id': ObjectId(id)})
    return jsonify({"message": "Product deleted"}), 200


# ---------------- ORDERS ----------------

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.json

    product = mongo.db.products.find_one({"_id": ObjectId(data['product_id'])})

    if not product:
        return jsonify({"message": "Product not found"}), 404

    if product['quantity'] < int(data['quantity']):
        return jsonify({"message": "Insufficient stock"}), 400

    new_quantity = product['quantity'] - int(data['quantity'])

    mongo.db.products.update_one(
        {"_id": ObjectId(data['product_id'])},
        {"$set": {"quantity": new_quantity}}
    )

    mongo.db.orders.insert_one({
        "product_name": product['name'],
        "quantity": int(data['quantity']),
        "total_price": product['price'] * int(data['quantity']),
        "date": datetime.now()
    })

    return jsonify({"message": "Order placed", "remaining_stock": new_quantity}), 201


@app.route('/orders', methods=['GET'])
def get_orders():
    orders = list(mongo.db.orders.find())

    for o in orders:
        o['_id'] = str(o['_id'])

    return jsonify(orders), 200


# ---------------- RUN ----------------

if __name__ == '__main__':
    app.run(debug=True)