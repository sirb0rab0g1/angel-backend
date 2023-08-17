from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, send

import pymysql
from twilio.rest import Client

#twilio account
#email: kentoyfueconcillo@gmail.comm
#pass: @K0angleader1234567890

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000"]}})
socketio = SocketIO(app, logger=True, engineio_logger=True, cors_allowed_origins="*")

#http://localhost/phpmyadmin

#database
db_config = {
    'host': 'localhost',
    'user': 'root',
    'database': 'helpdesk'
}
connection = pymysql.connect(**db_config)
cursor = connection.cursor()

#twilio
account_sid = 'AC512d82f1fab10c761596c05accedb537'
auth_token = 'f7b5bf0e78ec1258e41e8b1171683bb6'
client = Client(account_sid, auth_token)

############### SOCKETS ###################

# @socketio.on('message')
# def handle_message(message):
#     print('Received message:', message)
#     send('Message received: ' + message, broadcast=True)

@socketio.on('message')
def handle_message(data):
    print(data)
    channel = data.get('channel', 'default')
    message = data.get('message', '')
    send({'channel': channel, 'message': message}, broadcast=True)


@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

############### USERS ###################
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

    query = "SELECT * FROM concern WHERE requested_by_user_id=%s"
    cursor.execute(query, (user_data['id']))
    
    try:
        # Fetch all the rows
        rows = cursor.fetchall()

        # Convert the rows to a list of dictionaries
        concern = []
        for row in rows:
            user = {
                'id': row[0],
                'requested_by_user_id': row[1],
                'name_reported': row[2],
                'reason': row[3],
                'schedule_hearing': row[4],
                'title': row[5]
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

    # Execute the query
    query = "SELECT * FROM concern WHERE name_reported LIKE %s OR title LIKE %s AND requested_by_user_id=%s"
    search_value = f"%{user_data['search']}%"  # This will be something like "%12345%"
    cursor.execute(query, (search_value, search_value, user_data['user_id']))
    
    # Fetch all the rows
    rows = cursor.fetchall()

    # Convert the rows to a list of dictionaries
    concern = []
    for row in rows:
        user = {
            'id': row[0],
            'requested_by_user_id': row[1],
            'name_reported': row[2],
            'reason': row[3],
            'schedule_hearing': row[4],
            'title': row[5],
        }
        concern.append(user)

    return jsonify(concern)

@app.route('/report-user', methods=['POST'])
def report_user():
    user_data = request.get_json()
    cursor = connection.cursor()

    try:
        cursor.execute("INSERT INTO concern (requested_by_user_id, name_reported, reason, title) VALUES (%s, %s, %s, %s)",
                   (user_data['requested_by_user_id'], user_data['name_reported'], user_data['reason'], user_data['title']))
        connection.commit()

        return jsonify({'data': 'Successfully registered'})

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()         

@app.route('/get-notification', methods=['POST'])
def get_notification():
    user_data = request.get_json()
    cursor = connection.cursor()

    # Execute the query
    # query = "SELECT MAX(id) AS max_id, modify_by_user, title, description, status, requested_by_user_id, scheduled_date, title, is_read FROM notification WHERE requested_by_user_id=%s GROUP BY title ORDER BY id DESC"
    query = "SELECT n.* FROM notification n JOIN (SELECT title, MAX(id) AS max_id FROM notification WHERE requested_by_user_id=%s GROUP BY title) max_ids ON n.title = max_ids.title AND n.id = max_ids.max_id WHERE n.requested_by_user_id=%s ORDER BY n.id DESC"
    cursor.execute(query, (user_data['id'], user_data['id']))
    rows = cursor.fetchall()

    # Convert the rows to a list of dictionaries
    concern = []
    for row in rows:
        user = {
            'id': row[0],
            'modify_by_user': row[1],
            'description': row[2],
            'status': row[3],
            'requested_by_user_id': row[4],
            'scheduled_date': row[5],
            'title': row[6],
            'is_read': row[7]
        }
        concern.append(user)

    return jsonify(concern)

@app.route('/update-notification', methods=['POST'])
def update_notification():
    user_data = request.get_json()
    cursor = connection.cursor()

    # Execute the query
    
    query = "UPDATE notification SET modify_by_user=%s, description=%s, status=%s, requested_by_user_id=%s, scheduled_date=%s, title=%s, is_read=%s  WHERE id=%s"
    cursor.execute(query, (user_data['modify_by_user'], user_data['description'], user_data['status'], user_data['requested_by_user_id'], user_data['scheduled_date'], user_data['title'], user_data['is_read'], user_data['id']))
    connection.commit()

    return jsonify({'data': 'Successfully update'})

############### ADMIN ###################
@app.route('/get-all-concerns-count', methods=['GET'])
def get_all_concerns_count():
    cursor = connection.cursor()

    # Execute the query
    query = "SELECT COUNT(*) FROM concern"
    cursor.execute(query)
    
    # Fetch the result
    result = cursor.fetchone()

    return jsonify({'data': result})

@app.route('/get-all-users-count', methods=['GET'])
def get_all_users_count():
    cursor = connection.cursor()

    # Execute the query
    query = "SELECT COUNT(*) FROM users WHERE role = 'user'"
    cursor.execute(query)
    
    # Fetch the result
    result = cursor.fetchone()

    return jsonify({'data': result})

@app.route('/get-all-barangays-count', methods=['GET'])
def get_all_barangays_count():
    cursor = connection.cursor()

    # Execute the query
    query = "SELECT COUNT(*) FROM barangays"
    cursor.execute(query)
    
    # Fetch the result
    result = cursor.fetchone()

    return jsonify({'data': result})


@app.route('/get-all-concerns', methods=['GET'])
def get_all_concerns():
    cursor = connection.cursor()
    cursors = connection.cursor()

    # Execute the query
    query = "SELECT * FROM concern"
    cursor.execute(query,)
    
    # Fetch all the rows
    rows = cursor.fetchall()

    # Convert the rows to a list of dictionaries
    concern = []
    for row in rows:
        querys = "SELECT * FROM users WHERE id=%s"
        cursors.execute(querys, (int(row[1])))
        userc = cursors.fetchall()[0]
        user = {
            'id': row[0],
            'requested_by_user_id': row[1],
            'name_reported': row[2],
            'reason': row[3],
            'schedule_hearing': row[4],
            'requested_by_user': {'first_name': userc[1], 'last_name': userc[2]},
            'title': row[5],
        }
        concern.append(user)

    return jsonify(concern)

@app.route('/search-admin-concerns', methods=['POST'])
def search_admin_concerns():
    user_data = request.get_json()
    cursor = connection.cursor()
    cursors = connection.cursor()

    try:
        # Execute the query
        query = "SELECT * FROM concern WHERE name_reported LIKE %s OR title LIKE %s"
        search_value = f"%{user_data['search']}%"  # This will be something like "%12345%"
        cursor.execute(query, (search_value, search_value))
        
        # Fetch all the rows
        rows = cursor.fetchall()

        # Convert the rows to a list of dictionaries
        concern = []
        for row in rows:
            querys = "SELECT * FROM users WHERE id=%s"
            cursors.execute(querys, (int(row[1])))
            userc = cursors.fetchall()[0]
            user = {
                'id': row[0],
                'requested_by_user_id': row[1],
                'name_reported': row[2],
                'reason': row[3],
                'schedule_hearing': row[4],
                'requested_by_user': {'first_name': userc[1], 'last_name': userc[2]},
                'title': row[5]
            }
            concern.append(user)

        return jsonify(concern)

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()

@app.route('/create-barangay', methods=['POST'])
def create_barangay():
    user_data = request.get_json()
    cursor = connection.cursor()

    try:
        cursor.execute("INSERT INTO barangays (barangay) VALUES (%s)",
                   (user_data['barangay']))
        connection.commit()

        return jsonify({'data': 'Successfully registered'})

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()

@app.route('/get-all-barangay', methods=['GET'])
def get_all_barangay():
    cursor = connection.cursor()

    try:
        # Execute the query
        query = "SELECT * FROM barangays"
        cursor.execute(query)
        
        # Fetch all the rows
        rows = cursor.fetchall()

        # Convert the rows to a list of dictionaries
        concern = []
        for row in rows:
            user = {
                'id': row[0],
                'barangay': row[1]
            }
            concern.append(user)

        return jsonify(concern)

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()

@app.route('/get-users-in-barangay', methods=['POST'])
def get_users_in_barangay(): 
    user_data = request.get_json()
    cursor = connection.cursor()

    try:
        # Execute the query
        query = "SELECT * FROM users WHERE barangay=%s"
        cursor.execute(query, (user_data['barangay']))
        
        # Fetch all the rows
        rows = cursor.fetchall()

        # Convert the rows to a list of dictionaries
        users = []
        for row in rows:
            user = {
                'id': row[0],
                'first_name': row[1],
                'last_name': row[2],
                'username': row[3],
                'password': row[4],
                'role': row[5],
                'barangay': row[6],
                'age': row[7],
                'gender': row[8],
                'phone_number': row[9]
            }
            users.append(user)

        return jsonify(users)

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()


@app.route('/search-barangay', methods=['POST'])
def search_barangay():
    user_data = request.get_json()
    cursor = connection.cursor()

    try:
        # Execute the query
        query = "SELECT * FROM barangays WHERE barangay LIKE %s"
        search_value = f"%{user_data['barangay']}%"
        cursor.execute(query, (search_value))
        
        # Fetch all the rows
        rows = cursor.fetchall()

        # Convert the rows to a list of dictionaries
        concern = []
        for row in rows:
            user = {
                'id': row[0],
                'barangay': row[1]
            }
            concern.append(user)

        return jsonify(concern)

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()

@app.route('/send-sms', methods=['POST'])
def send_sms():
    user_data = request.get_json()
    message = client.messages.create(
        body='Hello, this is a test SMS from Python!',
        from_='+17622499008',  # Replace with your Twilio phone number
        to='+63' + user_data['to_phone']    # Replace with the recipient's phone number
    )
    return jsonify({'data': 'Message Successfully sent'})

@app.route('/update-report-user', methods=['POST'])
def update_report_user():
    user_data = request.get_json()
    cursor = connection.cursor()

    cursor_notification = connection.cursor()

    try:
        # update status
        query = "UPDATE concern SET requested_by_user_id=%s, name_reported=%s, schedule_hearing=%s, reason=%s, title=%s WHERE id=%s"
        cursor.execute(query, (user_data['requested_by_user_id'], user_data['name_reported'], user_data['schedule_hearing'], user_data['reason'], user_data['title'], user_data['id']))
        connection.commit()

        #insert notification
        cursor.execute("INSERT INTO notification (modify_by_user, description, status, requested_by_user_id, scheduled_date, title, is_read) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                   (user_data['modify_by_user'], user_data['description'], user_data['status'], user_data['requested_by_user_id'], user_data['schedule_hearing'], user_data['title'], user_data['is_read']))
        connection.commit()

        return jsonify({'data': 'Successfully update'})

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close() 

############### AUTHS ###################

@app.route('/register', methods=['POST'])
def register_user():
    user_data = request.get_json()
    cursor = connection.cursor()

    try:
        cursor.execute("INSERT INTO users (first_name, last_name, username, password, role, barangay, age, gender, phone_number) VALUES (%s, %s, %s,%s,%s,%s,%s,%s,%s)",
                   (user_data['first_name'], user_data['last_name'], user_data['username'], user_data['password'], user_data['role'], user_data['barangay'], user_data['age'], user_data['gender'], user_data['phone_number']))
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
            user = {
                'id': row[0],
                'first_name': row[1],
                'last_name': row[2],
                'username': row[3],
                'password': row[4],
                'role': row[5]
            }
            users.append(user)

        if len(users) > 0:
            return jsonify({'data': users})
        else:
            return jsonify({'error': 'Incorrect Username or Password'}), 500

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()  

@app.route('/')
def index():
    return 'Index Page'

# Run the Flask application
if __name__ == '__main__':
    # app.run(debug=True)
    socketio.run(app, debug=True)

