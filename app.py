from flask import Flask, request, jsonify
from flask_cors import CORS

import pymysql
from twilio.rest import Client

#twilio account
#email: kentoyfueconcillo@gmail.comm
#pass: @K0angleader1234567890

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://192.168.116.1:3000", "http://192.168.0.160:3000"]}})

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
    query = "SELECT * FROM concern WHERE name_reported LIKE %s AND requested_by_user_id=%s"
    search_value = f"%{user_data['search']}%"  # This will be something like "%12345%"
    cursor.execute(query, (search_value, user_data['user_id']))
    
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
        }
        concern.append(user)

    return jsonify(concern)

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

@app.route('/get-notification', methods=['POST'])
def get_notification():
    user_data = request.get_json()
    cursor = connection.cursor()

    # Execute the query
    query = "SELECT * FROM notification WHERE requested_by_user_id=%s"
    cursor.execute(query, (user_data['id']))
    
    try:
        # Fetch all the rows
        rows = cursor.fetchall()

        # Convert the rows to a list of dictionaries
        concern = []
        for row in rows:
            user = {
                'id': row[0],
                'modify_by_user': row[1],
                'description': row[2],
                'status': row[3],
                'requested_by_user_id': row[4]
            }
            concern.append(user)

        return jsonify(concern)
    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()

############### ADMIN ###################
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
        query = "SELECT * FROM concern WHERE name_reported LIKE %s"
        search_value = f"%{user_data['search']}%"  # This will be something like "%12345%"
        cursor.execute(query, (search_value))
        
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
                'requested_by_user': {'first_name': userc[1], 'last_name': userc[2]}
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
        query = "UPDATE concern SET requested_by_user_id=%s, name_reported=%s, schedule_hearing=%s, reason=%s WHERE id=%s"
        cursor.execute(query, (user_data['requested_by_user_id'], user_data['name_reported'], user_data['schedule_hearing'], user_data['reason'], user_data['id']))
        connection.commit()

        #insert notification
        cursor.execute("INSERT INTO notification (modify_by_user, description, status, requested_by_user_id) VALUES (%s, %s, %s, %s)",
                   (user_data['modify_by_user'], user_data['description'], user_data['status'], user_data['requested_by_user_id']))
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

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)