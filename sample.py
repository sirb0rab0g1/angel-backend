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

@app.route('/get-concerns', methods=['POST'])
def get_concerns():
    user_data = request.get_json()
    cursor = connection.cursor()
    print(user_data)

    try:
        # Execute the query
        query = "SELECT * FROM concern WHERE requested_by_user_id=%s"
        cursor.execute(query, (user_data['id']))
        
        # Fetch all the rows
        rows = cursor.fetchall()
        print('hello', rows)

        # Convert the rows to a list of dictionaries
        concern = []
        for row in rows:
            print(row)
            user = {
                'id': row[0],
                'requested_by_user_id': row[1],
                'name_reported': row[2],
                'reason': row[3],
                'schedule_hearing': row[4],
            }
            concern.append(user)

        return jsonify(concern)

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()

@app.route('/search-concerns', methods=['POST'])
def search_concerns():
    user_data = request.get_json()
    cursor = connection.cursor()

    try:
        # Execute the query
        query = "SELECT * FROM concern WHERE name_reported LIKE %s"
        search_value = f"%{user_data['search']}%"  # This will be something like "%12345%"
        cursor.execute(query, (search_value,))
        
        # Fetch all the rows
        rows = cursor.fetchall()
        print('hello', rows)

        # Convert the rows to a list of dictionaries
        concern = []
        for row in rows:
            print(row)
            user = {
                'id': row[0],
                'requested_by_user_id': row[1],
                'name_reported': row[2],
                'reason': row[3],
                'schedule_hearing': row[4],
            }
            concern.append(user)

        return jsonify(concern)

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

@app.route('/report-user', methods=['POST'])
def report_user():
    user_data = request.get_json()
    cursor = connection.cursor()

    try:
        cursor.execute("INSERT INTO concern (requested_by_user_id, name_reported, reason) VALUES (%s, %s, %s)",
                   (user_data['requested_by_user_id'], user_data['name_reported'], user_data['reason']))
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