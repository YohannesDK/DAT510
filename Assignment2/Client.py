import socketio
import sys
from pprint import pprint
from Person import Person

sio = socketio.Client()
currentUser = None
global person
global communication
exit_application = False


def message(data):
    print('message received', data["message"], "\n")

def joined(data):
    print('connected received', data, "\n")

sio.on('joined', joined)
sio.on('message', message)

def Client():
    global currentUser
    print("Actions - 1 : Join, 2 : Send Message, 3 : Exit")
    action = input("Enter action: ")

    if action == "1":
        sio.emit('join', {'name': currentUser.name})

    elif action == "2":
        to = input("Enter name to send message to: ")
        message = input("Enter message: ")
        sio.emit('sendmessage', {'message': message, 'to': to})

    elif action == "-1":
        exit()

if __name__ == '__main__':
    name = sys.argv[1]
    currentUser = Person(name)

    sio.connect('http://127.0.0.1:3000')
    while not exit_application:
        Client()
    
    sio.disconnect()