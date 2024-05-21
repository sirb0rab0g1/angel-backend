from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, send

import pymysql
from twilio.rest import Client

import requests

#twilio account

import sys, requests
from urllib.parse import urlencode

from user_agents import parse
import hashlib


app = Flask(__name__, static_url_path='/static')
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "http://192.168.100.147:3000", "http://192.168.100.186:3000", "http://20.189.115.250", "http://barangaytresdemayo.online"]}})
socketio = SocketIO(app, logger=True, engineio_logger=True, cors_allowed_origins=["http://localhost:3000", "http://192.168.100.186:3000", "http://192.168.1.16:3000", "http://20.189.115.250", "http://barangaytresdemayo.online"])
#http://localhost/phpmyadmin

#database
db_config = {
    'host': 'localhost',
    'user': 'root',
    'database': 'helpdesk',
    #for deployment
    'password': 'p@ssw0rd12345'
}
connection = pymysql.connect(**db_config)
cursor = connection.cursor()

#twilio
account_sid = 'AC512d82f1fab10c761596c05accedb537'
auth_token = 'f7b5bf0e78ec1258e41e8b1171683bb6'
client = Client(account_sid, auth_token)

# uploading
import os
UPLOAD_FOLDER = 'static/uploads/events'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

############### SOCKETS ###################
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


############### UPLOAD IMAGE ###################
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    
    file = request.files['file']
    eventid = request.form['eventid']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)

        query = "UPDATE events SET image=%s  WHERE id=%s"
        cursor.execute(query, (filename, eventid))
        connection.commit()

        return jsonify({'success': True, 'filename': filename})

@app.route('/api/announcement-upload', methods=['POST'])
def announcement_upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    
    file = request.files['file']
    announcementid = request.form['announcementid']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)

        query = "UPDATE announcemets SET image=%s  WHERE id=%s"
        cursor.execute(query, (filename, announcementid))
        connection.commit()

        return jsonify({'success': True, 'filename': filename})


@app.route('/api/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

############### USERS ###################
@app.route('/api/users', methods=['GET'])
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

@app.route('/api/get-concerns', methods=['POST'])
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
                'title': row[5],
                'status': row[7],
                'dateapproved': row[8]
            }
            concern.append(user)

        return jsonify(concern)
    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()

@app.route('/api/search-concerns', methods=['POST'])
def search_concerns():
    user_data = request.get_json()
    cursor = connection.cursor()
    print('user data', user_data['user_id'])

    # Execute the query
    query = "SELECT * FROM concern WHERE (name_reported LIKE %s OR title LIKE %s) AND requested_by_user_id=%s"
    search_value = f"%{user_data['search']}%"  # This will be something like "%12345%"
    cursor.execute(query, (search_value, search_value, user_data['user_id']))
    print(query)
    
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
            'status': row[7],
            'dateapproved': row[8]
        }
        concern.append(user)

    return jsonify(concern)

@app.route('/api/report-user', methods=['POST'])
def report_user():
    user_data = request.get_json()
    cursor = connection.cursor()

    try:
        cursor.execute("INSERT INTO concern (requested_by_user_id, name_reported, reason, title, query_by_user, status, dateapproved) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                   (user_data['requested_by_user_id'], user_data['name_reported'], user_data['reason'], user_data['title'], user_data['query_by_user'], user_data['status'], user_data['dateapproved']))
        connection.commit()

        return jsonify({'data': 'Successfully registered'})

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()         

@app.route('/api/get-notification', methods=['POST'])
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

@app.route('/api/update-notification', methods=['POST'])
def update_notification():
    user_data = request.get_json()
    cursor = connection.cursor()

    # Execute the query
    
    query = "UPDATE notification SET modify_by_user=%s, description=%s, status=%s, requested_by_user_id=%s, scheduled_date=%s, title=%s, is_read=%s  WHERE id=%s"
    cursor.execute(query, (user_data['modify_by_user'], user_data['description'], user_data['status'], user_data['requested_by_user_id'], user_data['scheduled_date'], user_data['title'], user_data['is_read'], user_data['id']))
    connection.commit()

    return jsonify({'data': 'Successfully update'})

@app.route('/api/request-document', methods=['POST'])
def request_document():
    user_data = request.get_json()
    cursor = connection.cursor()

    try:
        cursor.execute("INSERT INTO document (requested_by_id, service, reason, status, description, dateresponse) VALUES (%s, %s, %s, %s, %s, %s)",
                   (user_data['requested_by_id'], user_data['service'], user_data['reason'], user_data['status'], user_data['description'], user_data['dateresponse']))
        connection.commit()

        return jsonify({'data': 'Successfully registered'})

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()   

@app.route('/api/get-all-request-document', methods=['POST'])
def get_all_request_document():
    user_data = request.get_json()
    cursor = connection.cursor()
    cursors = connection.cursor()

    try:
        # Execute the query
        query = "SELECT * FROM document WHERE 1=1"  # Always true to start with
        params = []

        if user_data['requested_by_id'] is not None:
            query += " AND requested_by_id=%s"
            params.append(user_data['requested_by_id'])

        if user_data['service'] is not None:
            query += " AND service LIKE %s"
            params.append(f"%{user_data['service']}%")

        query += " ORDER BY id DESC"
            
        cursor.execute(query, params)
        
        # Fetch all the rows
        rows = cursor.fetchall()

        # Convert the rows to a list of dictionaries
        concern = []
        for row in rows:
            querys = "SELECT * FROM users WHERE id=%s"
            #cursors.execute(querys, (int(row[1])))
            cursors.execute(querys, (row[1],))
            userc = cursors.fetchone()
            print(userc)

            if not userc:
                continue  # Skip this document if the user is not found

            user = {
                'id': row[0],
                'requested_by_id': row[1],
                'service': row[2],
                'reason': row[3],
                'status': row[4],
                'description': row[5],
                'requested_by_user': {'first_name': userc[1], 'last_name': userc[2]},
                'age': userc[7],
                'dateresponse': row[6]

            }
            concern.append(user)

        return jsonify(concern)

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()
        cursors.close()


@app.route('/api/update-request-document', methods=['POST'])
def update_request_document():
    user_data = request.get_json()
    cursor = connection.cursor()

    # Execute the query
    
    query = "UPDATE document SET requested_by_id=%s, service=%s, reason=%s, status=%s, description=%s, dateresponse=%s WHERE id=%s"
    cursor.execute(query, (user_data['requested_by_id'], user_data['service'], user_data['reason'], user_data['status'], user_data['description'], user_data['dateresponse'], user_data['id']))
    connection.commit()

    return jsonify({'data': 'Successfully update'})      

############### ADMIN ###################
@app.route('/api/get-all-concerns-count', methods=['GET'])
def get_all_concerns_count():
    cursor = connection.cursor()

    # Execute the query
    query = "SELECT COUNT(*) FROM events"
    cursor.execute(query)
    
    # Fetch the result
    result = cursor.fetchone()

    return jsonify({'data': result})

@app.route('/api/get-all-users-count', methods=['GET'])
def get_all_users_count():
    cursor = connection.cursor()

    # Execute the query
    query = "SELECT COUNT(*) FROM announcemets"
    cursor.execute(query)
    
    # Fetch the result
    result = cursor.fetchone()

    return jsonify({'data': result})

@app.route('/api/get-all-barangays-count', methods=['GET'])
def get_all_barangays_count():
    cursor = connection.cursor()

    # Execute the query
    query = "SELECT COUNT(*) FROM barangays"
    cursor.execute(query)
    
    # Fetch the result
    result = cursor.fetchone()

    return jsonify({'data': result})


@app.route('/api/get-all-concerns', methods=['GET'])
def get_all_concerns():
    cursor = connection.cursor()
    cursors = connection.cursor()

    query = "SELECT * FROM contactus ORDER BY id DESC"
    cursor.execute(query,)

    rows = cursor.fetchall()
    concern = []
    for row in rows:
        print(row)
        user = {
            'id': row[0],
            'name': row[1],
            'mobilenumber': row[2],
            'email': row[3],
            'message': row[4],
            'date': row[5]
        }
        concern.append(user)

    return jsonify(concern)

@app.route('/api/get-all-concerns-original', methods=['GET'])
def get_all_concerns_original():
    cursor = connection.cursor()
    cursors = connection.cursor()

    query = "SELECT * FROM concern"
    cursor.execute(query,)

    rows = cursor.fetchall()
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
            'title': row[5],
            'query_by_user': row[6],
            'requested_by_user': {'first_name': userc[1], 'last_name': userc[2]},
            'status': row[7],
            'dateapproved': row[8]
        }
        concern.append(user)

    return jsonify(concern)

@app.route('/api/search-admin-contactus', methods=['POST'])
def search_admin_contactus():
    user_data = request.get_json()
    cursor = connection.cursor()
    cursors = connection.cursor()

    try:
        query = "SELECT * FROM contactus WHERE name LIKE %s OR mobilenumber LIKE %s ORDER BY id DESC"
        search_value = f"%{user_data['search']}%"
        cursor.execute(query, (search_value, search_value))

        rows = cursor.fetchall()
        concern = []
        for row in rows:
            print(row)
            user = {
                'id': row[0],
                'name': row[1],
                'mobilenumber': row[2],
                'email': row[3],
                'message': row[4],
                'date': row[5]
            }
            concern.append(user)

        return jsonify(concern)

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()

@app.route('/api/search-admin-concerns', methods=['POST'])
def search_admin_concerns():
    user_data = request.get_json()
    cursor = connection.cursor()
    cursors = connection.cursor()

    try:
        # Execute the query
        query = "SELECT * FROM concern WHERE name_reported LIKE %s OR title LIKE %s "
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
                'title': row[5],
                'query_by_user': row[6],
                'status': row[7],
                'dateapproved': row[8]
            }
            concern.append(user)

        # query = "SELECT * FROM contactus WHERE name LIKE %s OR mobilenumber LIKE %s ORDER BY id DESC"
        # search_value = f"%{user_data['search']}%"
        # cursor.execute(query, (search_value, search_value))

        # rows = cursor.fetchall()
        # concern = []
        # for row in rows:
        #     print(row)
        #     user = {
        #         'id': row[0],
        #         'name': row[1],
        #         'mobilenumber': row[2],
        #         'email': row[3],
        #         'message': row[4],
        #         'date': row[5]
        #     }
        #     concern.append(user)

        return jsonify(concern)

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()

@app.route('/api/create-barangay', methods=['POST'])
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

@app.route('/api/update-barangay', methods=['POST'])
def update_barangay():
    user_data = request.get_json()
    cursor = connection.cursor()

    try:
        query = "UPDATE barangays SET barangay=%s WHERE id=%s"
        cursor.execute(query, (user_data['barangay'], user_data['id']))
        connection.commit()

        return jsonify({'data': 'Successfully Update'})

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()

@app.route('/api/delete-barangay', methods=['POST'])
def delete_barangay():
    user_data = request.get_json()
    cursor = connection.cursor()

    try:
        # Execute the query
        query = "DELETE FROM barangays WHERE id=%s"
        cursor.execute(query, (user_data['id'],))
        
        # Commit the transaction
        connection.commit()

        return jsonify({'message': 'Service deleted successfully'})

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()

@app.route('/api/get-all-barangay', methods=['GET'])
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

@app.route('/api/get-users-in-barangay', methods=['POST'])
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


@app.route('/api/search-barangay', methods=['POST'])
def search_barangay():
    user_data = request.get_json()
    cursor = connection.cursor()

    try:
        # Execute the query
        query = "SELECT * FROM barangays WHERE barangay LIKE %s"
        search_values_title = f"%{user_data['barangay']}%"
        
        if user_data['id'] is not None:
            query += " AND id=%s"
            params = (search_values_title, user_data['id'])
        else:
            params = (search_values_title,)
            
        cursor.execute(query, params)
        
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

@app.route('/api/send-sms', methods=['POST'])
def send_sms():
    user_data = request.get_json()
    message = client.messages.create(
        body='Hello, this is a test SMS from Python!',
        from_='+17622499008',  # Replace with your Twilio phone number
        to='+63' + user_data['to_phone']    # Replace with the recipient's phone number
    )
    return jsonify({'data': 'Message Successfully sent'})

@app.route('/api/update-report-user', methods=['POST'])
def update_report_user():
    user_data = request.get_json()
    cursor = connection.cursor()

    # cursor_notification = connection.cursor()

    try:
        # update status
        query = "UPDATE concern SET requested_by_user_id=%s, name_reported=%s, schedule_hearing=%s, reason=%s, title=%s WHERE id=%s"
        cursor.execute(query, (user_data['requested_by_user_id'], user_data['name_reported'], user_data['schedule_hearing'], user_data['reason'], user_data['title'], user_data['id']))
        connection.commit()

        #insert notification
        # cursor.execute("INSERT INTO notification (modify_by_user, description, status, requested_by_user_id, scheduled_date, title, is_read) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        #            (user_data['modify_by_user'], user_data['description'], user_data['status'], user_data['requested_by_user_id'], user_data['schedule_hearing'], user_data['title'], user_data['is_read']))
        # connection.commit()

        return jsonify({'data': 'Successfully update'})

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close() 

@app.route('/api/update-report-user-done', methods=['POST'])
def update_report_user_done():
    user_data = request.get_json()
    cursor = connection.cursor()

    try:
        # update status
        query = "UPDATE concern SET status=%s, dateapproved=%s WHERE id=%s"
        cursor.execute(query, (user_data['status'], user_data['dateapproved'], user_data['id']))
        connection.commit()

        return jsonify({'data': 'Successfully update'})

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close() 

@app.route('/api/create-event', methods=['POST'])
def create_event():
    user_data = request.get_json()
    cursor = connection.cursor()

    try:
        cursor.execute("INSERT INTO events (title, date, summary, image) VALUES (%s,%s,%s,%s)",
                   (user_data['title'], user_data['date'], user_data['summary'], user_data['image']))
        connection.commit()

        # Get the last inserted ID
        cursor.execute("SELECT LAST_INSERT_ID()")
        event_id = cursor.fetchone()[0]

        return jsonify({'id': event_id, 'message': 'Successfully registered'})

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()

@app.route('/api/search-event', methods=['POST'])
def search_event():
    user_data = request.get_json()
    cursor = connection.cursor()

    try:
        # Execute the query
        query = "SELECT * FROM events WHERE title LIKE %s"
        search_values_title = f"%{user_data['title']}%"
        
        if user_data['id'] is not None:
            query += " AND id=%s"
            params = (search_values_title, user_data['id'])
        else:
            params = (search_values_title,)
            
        cursor.execute(query, params)
        
        # Fetch all the rows
        rows = cursor.fetchall()

        # Convert the rows to a list of dictionaries
        concern = []
        for row in rows:
            user = {
                'id': row[0],
                'title': row[1],
                'date': row[2],
                'summary': row[3],
                'image': 'http://localhost:5000/'+row[4]
            }
            concern.append(user)

        return jsonify(concern)

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()

@app.route('/api/delete-event', methods=['POST'])
def delete_event():
    user_data = request.get_json()
    cursor = connection.cursor()

    try:
        # Execute the query
        query = "DELETE FROM events WHERE id=%s"
        cursor.execute(query, (user_data['id'],))
        
        # Commit the transaction
        connection.commit()

        return jsonify({'message': 'Event deleted successfully'})

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()

@app.route('/api/get-all-events', methods=['GET'])
def get_all_events():
    cursor = connection.cursor()

    try:
        # Execute the query
        query = "SELECT * FROM events"
        cursor.execute(query)
        
        # Fetch all the rows
        rows = cursor.fetchall()

        # Convert the rows to a list of dictionaries
        concern = []
        for row in rows:
            user = {
                'id': row[0],
                'title': row[1],
                'date': row[2],
                'summary': row[3],
                'image': row[4],
            }
            concern.append(user)

        return jsonify(concern)

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()

@app.route('/api/create-announcement', methods=['POST'])
def create_announcement():
    user_data = request.get_json()
    cursor = connection.cursor()

    try:
        cursor.execute("INSERT INTO announcemets (title, description, datetime, image) VALUES (%s,%s,%s,%s)",
                   (user_data['title'], user_data['description'], user_data['datetime'], user_data['image']))
        connection.commit()

        # Get the last inserted ID
        cursor.execute("SELECT LAST_INSERT_ID()")
        event_id = cursor.fetchone()[0]

        return jsonify({'id': event_id, 'message': 'Successfully registered'})

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()



@app.route('/api/get-all-announcements', methods=['GET'])
def get_all_announcements():
    cursor = connection.cursor()

    try:
        # Execute the query
        query = "SELECT * FROM announcemets ORDER BY id DESC"
        cursor.execute(query)
        
        # Fetch all the rows
        rows = cursor.fetchall()

        # Convert the rows to a list of dictionaries
        concern = []
        for row in rows:
            user = {
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'datetime': row[3],
                'image': row[4]
            }
            concern.append(user)

        return jsonify(concern)

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()

@app.route('/api/search-announcement', methods=['POST'])
def search_announcement():
    user_data = request.get_json()
    cursor = connection.cursor()

    try:
        # Execute the query
        query = "SELECT * FROM announcemets  WHERE title LIKE %s"
        search_values_title = f"%{user_data['title']}%"
        
        if user_data['id'] is not None:
            query += " AND id=%s"
            params = (search_values_title, user_data['id'])
        else:
            params = (search_values_title,)
            
        cursor.execute(query, params)
        
        # Fetch all the rows
        rows = cursor.fetchall()

        # Convert the rows to a list of dictionaries
        concern = []
        for row in rows:
            user = {
                'id': row[0],
                'title': row[1],
                'datetime': row[2],
                'description': row[3],
                'image': 'http://localhost:5000/'+row[4]
            }
            concern.append(user)

        return jsonify(concern)

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()

@app.route('/api/delete-announcement', methods=['POST'])
def delete_announcement():
    user_data = request.get_json()
    cursor = connection.cursor()

    try:
        # Execute the query
        query = "DELETE FROM announcemets WHERE id=%s"
        cursor.execute(query, (user_data['id'],))
        
        # Commit the transaction
        connection.commit()

        return jsonify({'message': 'Announcement deleted successfully'})

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()

@app.route('/api/create-history', methods=['POST'])
def create_history():
    user_data = request.get_json()
    cursor = connection.cursor()

    try:
        cursor.execute("INSERT INTO history (description) VALUES (%s)",
                   (user_data['description']))
        connection.commit()

        return jsonify({'data': 'Successfully Created'})

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()

@app.route('/api/delete-history', methods=['POST'])
def delete_history():
    user_data = request.get_json()
    cursor = connection.cursor()

    try:
        # Execute the query
        query = "DELETE FROM history WHERE id=%s"
        cursor.execute(query, (user_data['id'],))
        
        # Commit the transaction
        connection.commit()

        return jsonify({'message': 'History deleted successfully'})

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()

@app.route('/api/update-history', methods=['POST'])
def update_history():
    user_data = request.get_json()
    cursor = connection.cursor()

    try:
        query = "UPDATE history SET description=%s WHERE id=%s"
        cursor.execute(query, (user_data['description'], user_data['id']))
        connection.commit()

        return jsonify({'data': 'Successfully Update'})

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()

@app.route('/api/search-history', methods=['POST'])
def search_history():
    user_data = request.get_json()
    cursor = connection.cursor()

    try:
        # Execute the query
        query = "SELECT * FROM history  WHERE description LIKE %s"
        search_values_title = f"%{user_data['description']}%"
        
        if user_data['id'] is not None:
            query += " AND id=%s"
            params = (search_values_title, user_data['id'])
        else:
            params = (search_values_title,)
            
        cursor.execute(query, params)
        
        # Fetch all the rows
        rows = cursor.fetchall()

        # Convert the rows to a list of dictionaries
        concern = []
        for row in rows:
            user = {
                'id': row[0],
                'description': row[1]
            }
            concern.append(user)

        return jsonify(concern)

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()

@app.route('/api/get-all-history', methods=['GET'])
def get_all_history():
    cursor = connection.cursor()

    try:
        # Execute the query
        query = "SELECT * FROM history"
        cursor.execute(query)
        
        # Fetch all the rows
        rows = cursor.fetchall()

        # Convert the rows to a list of dictionaries
        concern = []
        for row in rows:
            user = {
                'id': row[0],
                'description': row[1]
            }
            concern.append(user)

        return jsonify(concern)

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()

@app.route('/api/create-goals', methods=['POST'])
def create_goal():
    user_data = request.get_json()
    cursor = connection.cursor()

    try:
        cursor.execute("INSERT INTO goals (description, is_vission_or_mission) VALUES (%s, %s)",
                   (user_data['description'], user_data['is_vission_or_mission']))
        connection.commit()

        return jsonify({'data': 'Successfully Created'})

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()

@app.route('/api/delete-goals', methods=['POST'])
def delete_goals():
    user_data = request.get_json()
    cursor = connection.cursor()

    try:
        # Execute the query
        query = "DELETE FROM goals WHERE id=%s"
        cursor.execute(query, (user_data['id'],))
        
        # Commit the transaction
        connection.commit()

        return jsonify({'message': 'Goals deleted successfully'})

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()

@app.route('/api/update-goals', methods=['POST'])
def update_goals():
    user_data = request.get_json()
    cursor = connection.cursor()

    try:
        query = "UPDATE goals SET description=%s, is_vission_or_mission=%s WHERE id=%s"
        cursor.execute(query, (user_data['description'],user_data['is_vission_or_mission'], user_data['id']))
        connection.commit()

        return jsonify({'data': 'Successfully Update'})

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()

@app.route('/api/search-goals', methods=['POST'])
def search_goals():
    user_data = request.get_json()
    cursor = connection.cursor()

    try:
        # Execute the query
        query = "SELECT * FROM goals WHERE 1=1"  # Always true to start with
        params = []

        if user_data['id'] is not None:
            query += " AND id=%s"
            params.append(user_data['id'])

        if user_data['is_vission_or_mission'] is not None:
            query += " AND is_vission_or_mission=%s"
            params.append(user_data['is_vission_or_mission'])

        if user_data['description'] is not None:
            query += " AND description LIKE %s"
            params.append(f"%{user_data['description']}%")

        query += " ORDER BY id DESC"
            
        cursor.execute(query, params)
        
        # Fetch all the rows
        rows = cursor.fetchall()

        # Convert the rows to a list of dictionaries
        concern = []
        for row in rows:
            user = {
                'id': row[0],
                'description': row[1],
                'is_vission_or_mission': row[2],

            }
            concern.append(user)

        return jsonify(concern)

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()

@app.route('/api/get-all-goals', methods=['GET'])
def get_all_goals():
    cursor = connection.cursor()

    try:
        # Execute the query
        query = "SELECT * FROM goals ORDER BY id DESC"
        cursor.execute(query)
        
        # Fetch all the rows
        rows = cursor.fetchall()

        # Convert the rows to a list of dictionaries
        concern = []
        for row in rows:
            user = {
                'id': row[0],
                'description': row[1],
                'is_vission_or_mission': row[2],

            }
            concern.append(user)

        return jsonify(concern)

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()

@app.route('/api/create-contact-us', methods=['POST'])
def create_contact_us():
    user_data = request.get_json()
    cursor = connection.cursor()

    try:
        cursor.execute("INSERT INTO contactus (name, mobilenumber,email, message, date) VALUES (%s, %s, %s, %s, %s)",
                   (user_data['name'], user_data['mobilenumber'], user_data['email'], user_data['message'], user_data['date']))
        connection.commit()

        return jsonify({'data': 'You successfully contacted us! Please wait for adminitrators response'})

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()

@app.route('/api/search-all-users', methods=['POST'])
def search_all_users():
    user_data = request.get_json()
    cursor = connection.cursor()

    try:
        # Execute the query
        query = "SELECT * FROM users WHERE first_name LIKE %s OR last_name LIKE %s ORDER BY id DESC"
        search_value = f"%{user_data['search']}%"
        cursor.execute(query, (search_value, search_value))
        
        # Fetch all the rows
        rows = cursor.fetchall()

        # Convert the rows to a list of dictionaries
        concern = []
        for row in rows:
            user = {
                'id': row[0],
                'first_name': row[1],
                'last_name': row[2],
                'username': row[3],
                'age': row[7],
                'gender': row[8],
                'phone_number': row[9],
                'status': row[10],
                'birth_date': row[12]

            }
            concern.append(user)

        return jsonify(concern)

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()

@app.route('/api/get-all-users', methods=['GET'])
def get_all_users():
    cursor = connection.cursor()

    try:
        # Execute the query
        query = "SELECT * FROM users ORDER BY id DESC"
        cursor.execute(query)
        
        # Fetch all the rows
        rows = cursor.fetchall()

        # Convert the rows to a list of dictionaries
        concern = []
        for row in rows:
            user = {
                'id': row[0],
                'first_name': row[1],
                'last_name': row[2],
                'username': row[3],
                'age': row[7],
                'gender': row[8],
                'phone_number': row[9],
                'status': row[10],
                'birth_date': row[12]

            }
            concern.append(user)

        return jsonify(concern)

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()

@app.route('/api/update-user-status', methods=['POST'])
def update_user_status():
    user_data = request.get_json()
    cursor = connection.cursor()

    try:
        query = "UPDATE users SET status=%s WHERE id=%s"
        cursor.execute(query, (user_data['status'],user_data['id']))
        connection.commit()
        
        return jsonify({'data': 'Profile Successfully updated'})  
    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()
############### AUTHS ###################

@app.route('/api/register', methods=['POST'])
def register_user():
    user_data = request.get_json()
    cursor = connection.cursor()

    try:
        cursor.execute("INSERT INTO users (first_name, last_name, username, password, role, barangay, age, birth_date, gender, phone_number, status, otp) VALUES (%s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                   (user_data['first_name'], user_data['last_name'], user_data['username'], user_data['password'], user_data['role'], user_data['barangay'], user_data['age'], user_data['birth_date'], user_data['gender'], user_data['phone_number'], user_data['status'], user_data['otp']))
        connection.commit()

        cursor.execute("SELECT LAST_INSERT_ID()")
        last_inserted_id = cursor.fetchone()[0]

        # account_sid = 'ACd4ac9da1a00ae1b04b5623db26af7f01'
        # auth_token = 'fe583c8efde5313a5e67685b2413d1cb'
        # client = Client(account_sid, auth_token)

        # message = client.messages.create(
        #   body='Hello! This is fromm barangay Tres De Mayo Digos City. Kindly input the OTP code {}.'.format(user_data['otp']),
        #   from_='+13613216644',
        #   to='+63'+user_data['phone_number']
        # )


        # ========================

        # params = (
        #     ('apikey', '9adf279544786e19f5efc643e0225b3e'),
        #     ('sendername', 'PackAndGo'),
        #     ('message', 'Hello! This is fromm barangay Tres De Mayo Digos City. Kindly input the OTP code {}.'.format(user_data['otp'])),
        #     ('number', '0'+user_data['phone_number'])
        # )
        # path = 'https://semaphore.co/api/v4/messages?' + urlencode(params)
        # response = requests.get(path)
        # print('Message Sent!')

        return jsonify({'data': 'Successfully registered', 'id': last_inserted_id})

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()   

@app.route('/api/update-user-profile', methods=['POST'])
def update_user_profile():
    user_data = request.get_json()
    cursor = connection.cursor()

    query = "UPDATE users SET first_name=%s, last_name=%s, username=%s, password=%s, role=%s, barangay=%s, age=%s, gender=%s, phone_number=%s WHERE id=%s"
    cursor.execute(query, (user_data['first_name'],user_data['last_name'],user_data['username'],user_data['password'],user_data['role'],user_data['barangay'],user_data['age'],user_data['gender'],user_data['phone_number'],user_data['id']))
    connection.commit()
    
    return jsonify({'data': 'Profile Successfully updated'})
      
@app.route('/api/login', methods=['POST'])
def login():
    # user_agent_string = request.headers.get('User-Agent')
    # user_agent = parse(user_agent_string)

    # browser_info = {
    #     'browser': {
    #         'family': user_agent.browser.family,
    #         'version': user_agent.browser.version_string,
    #         'is_mobile': user_agent.is_mobile,
    #         'is_tablet': user_agent.is_tablet,
    #         'is_pc': user_agent.is_pc,
    #         'is_bot': user_agent.is_bot
    #     },
    #     'os': {
    #         'family': user_agent.os.family,
    #         'version': user_agent.os.version_string
    #     },
    #     'device': {
    #         'family': user_agent.device.family,
    #         'brand': user_agent.device.brand,
    #         'model': user_agent.device.model
    #     },
    #     'is_touch_capable': user_agent.is_touch_capable,
    #     'is_mobile': user_agent.is_mobile,
    #     'is_tablet': user_agent.is_tablet,
    #     'is_pc': user_agent.is_pc,
    #     'is_bot': user_agent.is_bot
    # }

    # browser = user_agent.browser.family + user_agent.browser.version_string + str(user_agent.is_mobile) + str(user_agent.is_tablet) + str(user_agent.is_pc) + str(user_agent.is_bot)
    # os = user_agent.os.family + user_agent.os.version_string
    # device = user_agent.device.family + user_agent.device.brand + user_agent.device.model
    # extra = str(user_agent.is_touch_capable) + str(user_agent.is_mobile) + str(user_agent.is_tablet) + str(user_agent.is_pc) + str(user_agent.is_bot)

    # vals = browser + os + device + extra

    # sha256_hash = hashlib.sha256()
    # sha256_hash.update(vals.encode('utf-8'))
    # hashed_string = sha256_hash.hexdigest()

    # # return jsonify({'data': browser_info, 'hashed': hashed})
    # # return jsonify(hashed_string)
    # return jsonify(browser_info)

    user_data = request.get_json()
    cursor = connection.cursor()
    try:
        query = "SELECT * FROM users WHERE username=%s AND password=%s AND status='active'"
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
                'role': row[5],
                'barangay': row[6],
                'age': row[7],
                'gender': row[8],
                'phone_number': row[9],
                'status': row[10],
                'otp': row[11],
                'birth_date': row[12]

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

@app.route('/api/validate-otp-login', methods=['POST'])
def validate_otp_login():
    user_data = request.get_json()
    cursor = connection.cursor()
    try:
        query = "SELECT * FROM users WHERE id=%s AND otp=%s"
        cursor.execute(query, (user_data['id'], user_data['otp']))
        result = cursor.fetchall()

        users = []
        for row in result:
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

        if len(users) > 0:
            return jsonify({'data': 'Validated'})
        else:
            return jsonify({'error': 'Incorrect Username or Password'})

    except Exception as e:
        # Handle the exception
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor
        cursor.close()

@app.route('/api/')
def index():
    return 'Index Page'

# Run the Flask application
if __name__ == '__main__':
    # app.run(debug=True)
    # socketio.run(app, host='192.168.100.147', port=5000, debug=True, cors_allowed_origins=["http://localhost:3000", "http://192.168.100.147"])
    socketio.run(app, port=5000, debug=True)
    # socketio.run(app, port=5000, debug=True, allow_unsafe_werkzeug=True)
