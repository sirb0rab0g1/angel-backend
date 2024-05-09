import sys, requests
from urllib.parse import urlencode


apikey = '9adf279544786e19f5efc643e0225b3e'
sendername = 'PackAndGo'

def send_message(message, number):
    print('Sending Message...')
    params = (
        ('apikey', apikey),
        ('sendername', sendername),
        ('message', message),
        ('number', number)
    )
    path = 'https://semaphore.co/api/v4/messages?' + urlencode(params)
    response = requests.get(path)
    print('Message Sent!')
    return response.text  # Return the response content

if __name__ == '__main__':
    message = 'Hello!!'
    number = '09667542245'
    response_content = send_message(message, number)
    print("Response:", response_content)