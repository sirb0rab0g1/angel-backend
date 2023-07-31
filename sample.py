from flask import Flask, request, jsonify
from flask_cors import CORS

import pymysql

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://192.168.116.1:3000", "http://192.168.0.160:3000"]}})

db_config = {
    'host': 'localhost',
    'user': 'root',
    'database': 'helpdesk'
}

# http://localhost/phpmyadmin
# for database


# Create a connection to the database
connection = pymysql.connect(**db_config)

@app.route('/users', methods=['GET'])
def get_users():
    # Create a cursor
    cursor = connection.cursor()

    try:
        # Execute the query
        cursor.execute("SELECT * FROM users")
        
        # Fetch all the rows
        rows = cursor.fetchall()

        # Convert the rows to a list of dictionaries
        users = []
        for row in rows:
            print(row)
            user = {
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'username': row[3],
                'password': row[4],
            }
            users.append(user)

        return jsonify(users)

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()

@app.route('/register', methods=['POST'])
def register_user():
    user_data = request.get_json()
    cursor = connection.cursor()

    try:
        cursor.execute("INSERT INTO users (first_name, last_name, username, password, role) VALUES (%s, %s, %s,%s,%s)",
                   (user_data['first_name'], user_data['last_name'], user_data['username'], user_data['password'], user_data['role']))
        connection.commit()

        return jsonify({'data': 'Successfully registered'})

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()        

@app.route('/login', methods=['POST'])
def login():
    user_data = request.get_json()
    cursor = connection.cursor()
    try:
        print('em here')
        print('usernamme', user_data['username'])
        print('password', user_data['password'])

        # validation
        query = "SELECT * FROM users WHERE username=%s AND password=%s"
        cursor.execute(query, (user_data['username'], user_data['password']))
        result = cursor.fetchall()

        users = []
        for row in result:
            print(row)
            user = {
                'id': row[0],
                'first_name': row[1],
                'last_name': row[2],
                'username': row[3],
                'password': row[4],
                'role': row[5]
            }
            users.append(user)

        return jsonify({'data': users})

    except Exception as e:
        # Handle the exception
        return jsonify({'error': 'Incorrect Username or Password'}), 500

    finally:
        # Close the cursor
        cursor.close()  

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)