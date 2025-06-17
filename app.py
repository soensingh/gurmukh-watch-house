from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS

# MySQL Config (replace with your own)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'sswsj234okm'
app.config['MYSQL_DB'] = 'gurmukh_watch'

mysql = MySQL(app)

@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    confirm = request.form['confirm']

    if password != confirm:
        return jsonify({'error': 'Passwords do not match'}), 400

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'User registered successfully'}), 200

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
    user = cur.fetchone()
    cur.close()

    if user:
        print("User found:", user)
        return jsonify({
            'message': 'Login successful',
            'id': user[0],   # assuming user[0] = id
            'name': user[1]
        }), 200

    else:
        return jsonify({'error': 'Invalid email or password'}), 401

@app.route('/api/watches', methods=['GET'])
def get_watches():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, description, price, image_url FROM watches")
    data = cur.fetchall()
    cur.close()

    watches = []
    for row in data:
        watches.append({
            'id': row[0],
            'name': row[1],
            'description': row[2],
            'price': row[3],
            'image': row[4]
        })

    return jsonify(watches)

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    data = request.json
    user_id = data.get('user_id')  # Get user ID from request
    watch_id = data.get('watch_id')

    if not user_id or not watch_id:
        return jsonify({"error": "Missing user_id or watch_id"}), 400

    cur = mysql.connection.cursor()
    
    # Check if the item is already in the cart
    cur.execute("SELECT id, quantity FROM cart WHERE user_id = %s AND watch_id = %s", (user_id, watch_id))
    existing_item = cur.fetchone()

    if existing_item:
        new_quantity = existing_item[1] + 1
        cur.execute("UPDATE cart SET quantity = %s WHERE id = %s", (new_quantity, existing_item[0]))
    else:
        cur.execute("INSERT INTO cart (user_id, watch_id, quantity) VALUES (%s, %s, 1)", (user_id, watch_id))

    mysql.connection.commit()
    cur.close()
    return jsonify({"message": "Item added to cart"}), 200

@app.route('/api/cart/<int:user_id>', methods=['GET'])
def get_cart(user_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT c.id, w.name, w.description, w.price, w.image_url, c.quantity
        FROM cart c
        JOIN watches w ON c.watch_id = w.id
        WHERE c.user_id = %s
    """, (user_id,))
    
    cart_items = cur.fetchall()
    cur.close()

    cart_data = [
        {
            "cart_id": item[0],
            "name": item[1],
            "description": item[2],
            "price": item[3],
            "image": item[4],
            "quantity": item[5]
        }
        for item in cart_items
    ]

    return jsonify(cart_data)

@app.route('/api/cart/delete', methods=['POST'])
def delete_from_cart():
    data = request.json
    cart_id = data.get('cart_id')

    if not cart_id:
        return jsonify({"error": "Missing cart_id"}), 400

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM cart WHERE id = %s", (cart_id,))
    mysql.connection.commit()
    cur.close()

    return jsonify({"message": "Item removed from cart"}), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)
