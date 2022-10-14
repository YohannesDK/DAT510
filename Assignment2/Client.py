import socketio
import sys
from Person import Person
from SecureCommunication import SecureCommunication

sio = socketio.Client()

# Client State Variables
processing = False
user_has_joined = False
user_on_other_side = None
exit_application = False

# User Variables
currentUser = None
secureCommunication = None


def DisplayMessageBox(length, messages, withbox=True):
    if withbox:
        print("\n")
        print("+" + "-" * length + "+")
        for m in messages:
            print("|" + m + " " * (length - len(m)) + "|")
        print("+" + "-" * length + "+")
        print("\n")
    else:
        print(messages, end="")

def DisplayMenu():
    actions = ["Actions:", "   1 : Show Online Users", "   2 : Start Chat Session with User", "   3 : Send Message", "   4 : Exit"]
    actions_length = max([len(action) for action in actions]) + 3
    DisplayMessageBox(actions_length, actions)

def DisplayEnterAction():
    l = ["Enter Action: "]
    DisplayMessageBox(len(l[0]), l[0], withbox=False)

def joined(data):
    global processing
    print('\nJoined Chat Server!')
    processing = False

def OnlineUsers(data):
    global processing
    online_users = ["Online Users: "] + [f"   - {user}" for user in data["online_users"]]
    online_users_length = max([len(user) for user in online_users]) + 3
    DisplayMessageBox(online_users_length, online_users)
    processing = False

def public_key_received(data):
    global user_on_other_side
    global secureCommunication

    user_on_other_side = data["From"]
    public_key = data["public_key"]
    secureCommunication.store_counterpart_public_key(public_key)
    sio.emit('share_public_key_reply', {'to': data["From"], 'public_key': secureCommunication.user.public_key})

def public_key_received_reply(data):
    global processing
    global secureCommunication
    public_key = data["public_key"]
    secureCommunication.store_counterpart_public_key(public_key)
    secureCommunication.generate_shared_keys()
    
    l = [f"Chat session with {user_on_other_side} started!"]
    DisplayMessageBox(len(l[0]), l)
    processing = False


def message(data):
    global secureCommunication
    global processing
    global user_on_other_side
    currentUser = secureCommunication.user
    if currentUser.shared_key == "":
        secureCommunication.generate_shared_keys()
    
    decrypted_message = secureCommunication.Decrypt(data["message"])
    print(f'\n\n{user_on_other_side} says: {data["message"]} -> {decrypted_message}', "\n")
    processing = False
    DisplayMenu()
    DisplayEnterAction()

# define the event handlers
sio.on('joined', joined)
sio.on('public_key_received', public_key_received)
sio.on('share_public_key_reply', public_key_received_reply)
sio.on('message', message)
sio.on('onlineUsers', OnlineUsers)

def Client():
    global processing
    global user_has_joined
    global user_on_other_side
    global secureCommunication
    global exit_application
    currentUser = secureCommunication.user

    if not user_has_joined:
        processing = True
        sio.emit('join', {'name': currentUser.name})
        user_has_joined = True

    action = ""
    if not processing:
        DisplayMenu()
        action = input("Enter Action: ")
        processing = True

    if action == "1":
        sio.emit('getOnlineUsers')

    elif action == "2":
        who = input("Enter name of person to start a chat with: ")
        user_on_other_side = who
        sio.emit('share_public_key', {'with': who, "From": currentUser.name, 'public_key': currentUser.public_key})

    elif action == "3":
        to = user_on_other_side
        if currentUser.shared_key == "":
            to = input("Enter name of user to start chat session with: ")
            secureCommunication.generate_shared_keys()

        message = input("Enter message: ")
        encrypted_message = secureCommunication.Encrypt(message)
        sio.emit('sendmessage', {'message': encrypted_message, 'to': to})
        processing = False
    
    elif action == "4":
        exit_application = True
        sio.disconnect()
        exit(0)

if __name__ == '__main__':
    name = sys.argv[1]
    currentUser = Person(name)
    secureCommunication = SecureCommunication.createCommunication(currentUser)
    secureCommunication.dh.generate_keys(secureCommunication.user)

    sio.connect('http://127.0.0.1:3000')
    while not exit_application:
        Client()
    
    sio.disconnect()