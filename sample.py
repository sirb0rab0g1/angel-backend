from flask import Flask, request, jsonify
import pymysql

# Create a Flask application
app = Flask(__name__)

# MySQL database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'database': 'helpdesk'
}

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

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)