import os
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ---------------------------------------------------------
# 1. DATABASE CONFIGURATION
# ---------------------------------------------------------
# Replace the URI with your MongoDB Atlas connection string
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
mongo = PyMongo(app)

# ---------------------------------------------------------
# 2. USER AUTHENTICATION
# ---------------------------------------------------------

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    users = mongo.db.users
    
    # Check if user already exists
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

# ---------------------------------------------------------
# 3. PRODUCT MANAGEMENT
# ---------------------------------------------------------

@app.route('/products', methods=['POST'])
def add_product():
    data = request.json
    # Validation: Ensure quantity isn't negative
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
    products = list(mongo.db.products.find())
    for p in products:
        p['_id'] = str(p['_id'])
    return jsonify(products), 200

@app.route('/products/<id>', methods=['PUT'])
def update_product(id):
    data = request.json
    mongo.db.products.update_one(
        {'_id': ObjectId(id)},
        {'$set': data}
    )
    return jsonify({"message": "Product updated"}), 200

@app.route('/products/<id>', methods=['DELETE'])
def delete_product(id):
    mongo.db.products.delete_one({'_id': ObjectId(id)})
    return jsonify({"message": "Product deleted"}), 200

# ---------------------------------------------------------
# 4. ORDER & INVENTORY MANAGEMENT
# ---------------------------------------------------------

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.json
    product_id = data['product_id']
    order_quantity = int(data['quantity'])
    
    product = mongo.db.products.find_one({"_id": ObjectId(product_id)})
    
    if not product:
        return jsonify({"message": "Product not found"}), 404
    
    # Logic: Prevent stock from going below zero
    if product['quantity'] < order_quantity:
        return jsonify({"message": "Insufficient stock!"}), 400
    
    # Update Inventory
    new_quantity = product['quantity'] - order_quantity
    mongo.db.products.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": {"quantity": new_quantity}}
    )
    
    # Record Order History
    order_data = {
        "product_name": product['name'],
        "quantity": order_quantity,
        "total_price": product['price'] * order_quantity,
        "date": datetime.now()
    }
    mongo.db.orders.insert_one(order_data)
    
    return jsonify({"message": "Order placed successfully", "remaining_stock": new_quantity}), 201

@app.route('/orders', methods=['GET'])
def get_order_history():
    orders = list(mongo.db.orders.find().sort("date", -1))
    for o in orders:
        o['_id'] = str(o['_id'])
    return jsonify(orders), 200

# ---------------------------------------------------------
# 5. DEPLOYMENT CONFIG
# ---------------------------------------------------------

if __name__ == '__main__':
    # Use environment variables for Port (required for Render/Heroku)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)