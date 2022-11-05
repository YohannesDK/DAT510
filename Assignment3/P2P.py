import socket
import threading
import random
import json
import time

from Person import Person
from Node import Node
from SecureCommunication import SecureCommunication

# localhost ip address
IP = "127.0.0.1"
BROADCAST_PORT = 5000
FILES = ["file1.txt", "file2.txt", "file3.txt", "file4.txt", "file5.txt",
         "file6.txt", "file7.txt"]

def Find_Free_Port():
    port = None
    while port is None:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', 0))
        s.listen(1)
        new_port = s.getsockname()[1]
        s.close()

        if new_port != BROADCAST_PORT:
            port = new_port
    return port

class P2P:
    def __init__(self, node: Node):
        self.node = node
        self.online = True
        self.show_broadcast_messages = False
        self.last_sender = None
        self.DHT = {}
    
    #region Broadcast
    def update_received(self):
        """
            This method listens to broadcast messages on the network and adds the node to the DHT
        """
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as socket_receiver:
            socket_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            socket_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            socket_receiver.bind(("", BROADCAST_PORT))
            while self.online:
                data, address = socket_receiver.recvfrom(1024)
                if data:
                    data = json.loads(data)
                    user_data = data["data"]

                    if user_data["name"] == self.node.secureCommunication.user.name:
                        continue
                    if data["type"] == "heartbeat":
                        if self.show_broadcast_messages:
                            print("Received heartbeat from", user_data["name"])
                        self.DHT[user_data["name"]] = user_data
                    if data["type"] == "node_left":
                        if self.show_broadcast_messages:
                            print("Received node_left from", user_data["name"])
                        self.DHT.pop(user_data["name"])
    
    def update_network(self, message_type="heartbeat"):
        """
            This method joins the P2P network by broadcasting the node's information
        """
        
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as socket_sender:
            socket_sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            socket_sender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            # socket_sender.settimeout(10)
            while self.online:
                if message_type == "heartbeat":
                    socket_sender.sendto(json.dumps(
                        {
                            "type": "heartbeat",
                            "data": self.node.dto()
                        }
                        ).encode("utf-8"), ("<broadcast>", BROADCAST_PORT))
                time.sleep(5)

            socket_sender.sendto(json.dumps(
                {
                    "type": "node_left",
                    "data": self.node.dto()
                }
                ).encode("utf-8"), ("<broadcast>", BROADCAST_PORT)) 
    #endregion
    
    def send_message(self, message: str, receiver: str):
        """
            This method sends a message to a specific node
        """
        if receiver not in self.DHT:
            print("\nNode not found")
            DisplayMenu()
            return
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_sender:
            socket_sender.connect((self.DHT[receiver]["ipaddress"][0], self.DHT[receiver]["ipaddress"][1]))
            socket_sender.sendall(json.dumps(
                {
                    "from": self.node.secureCommunication.user.name,
                    "type": "message",
                    "data": message
                }
                ).encode("utf-8"))
            socket_sender.close()
    
    def request_received(self):
        """
            This method listens to messages sent to the node
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_receiver:
            socket_receiver.bind((self.node.ipaddress[0], self.node.ipaddress[1]))
            socket_receiver.listen()
            while self.online:
                conn, addr = socket_receiver.accept()
                with conn:
                    data = conn.recv(1024)
                    if data:
                        data = json.loads(data)
                        if data["type"] == "message":
                            print("\nMessage Received - ", data["from"], ": ", data["data"])
                            DisplayMenu()
                            self.last_sender = data["from"]
                        if data["type"] == "request_file":
                            # reply with the file requested if it exists
                            if data["filename"] in FILES:
                                conn.sendall(json.dumps(
                                    {
                                        "from": self.node.secureCommunication.user.name,
                                        "type": "file",
                                        "filename": data["filename"]
                                    }
                                    ).encode("utf-8"))
                            else:
                                conn.sendall(json.dumps(
                                    {
                                        "from": self.node.secureCommunication.user.name,
                                        "type": "file_not_found",
                                        "filename": None
                                    }
                                    ).encode("utf-8"))
            socket_receiver.close()
            
    # region File Sharing
    def request_public_file(self, file_name: str, receiver: str):
        """
            This method requests a file from a specific node
        """
        if receiver not in self.DHT:
            print("\nNode not found")
            DisplayMenu()
            return
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_sender:
            socket_sender.connect((self.DHT[receiver]["ipaddress"][0], self.DHT[receiver]["ipaddress"][1]))
            socket_sender.sendall(json.dumps(
                {
                    "from": self.node.secureCommunication.user.name,
                    "type": "request_file",
                    "filename": file_name
                }
                ).encode("utf-8"))

            # store the reply in a file            
            reply = socket_sender.recv(1024)
            if reply:
                reply = json.loads(reply)
                if reply["type"] == "file": 
                    print("\nFile Received - ", file_name)
                    if not file_name in self.node.files:
                        self.node.files.append(file_name)
                else:
                    print("\nFile not available")
            
            socket_sender.close()

    def join_network(self):
        """
            This method starts the communication with the P2P network
        """
        th1 = threading.Thread(target=self.update_received, daemon=True)
        th1.start()
        th2 = threading.Thread(target=self.update_network, daemon=True)
        th2.start()

        th3 = threading.Thread(target=self.request_received, daemon=True)
        th3.start()

    # factory method
    @classmethod
    def createP2P(cls, username: str):
        user = Person(username)
        sc = SecureCommunication.createCommunication(user)
        sc.dh.generate_keys(sc.user)

        node_files = random.choices(FILES, k=random.randint(1, len(FILES)))

        # find a free port
        port = Find_Free_Port()
        # create node
        node = Node(sc, (IP, port), node_files)
        print(f"\nP2P node created - username: {username}, port: {port}, files: {node_files}, public_key: {sc.user.public_key}\n")

        return cls(node)

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
    actions = ["Actions:", "   1 : Toogle broadcast messages", "   2 : Show Online Nodes", "   3 : Send Message", 
                "   4 : Reply to Last Message", "   5 : Show all files", "   6 : Show public files",
                "   7 : Add public file", "   8 : Request public file", "   9 : Exit", "  -1 : Kill Everyone"]
    actions_length = max([len(action) for action in actions]) + 3
    DisplayMessageBox(actions_length, actions)

def DisplayOnlineNodes(DHT):
    nodes = ["Online Nodes:"]
    for node in DHT:
        nodes.append(f"   {node} : {DHT[node]['ipaddress']}")
    nodes_length = max([len(node) for node in nodes]) + 3
    DisplayMessageBox(nodes_length, nodes)

def DisplayAllFilesInNetwork(DHT):
    files = ["All Files:"]
    for node in DHT:
        files.append(f"   {node} : {DHT[node]['files']}")
    files_length = max([len(file) for file in files]) + 3
    DisplayMessageBox(files_length, files)

def DisplayPublicFiles(DHT):
    files = ["Public Files:"]
    for node in DHT:
        files.append(f"   {node} : {DHT[node]['public_files']}")
    files_length = max([len(file) for file in files]) + 3
    DisplayMessageBox(files_length, files)

def DisplayEnterAction():
    l = ["Enter Action: "]
    DisplayMessageBox(len(l[0]), l[0], withbox=False)

def Program(p2p: P2P):
    while True:
        DisplayMenu()
        option = input("Choose an Action: ")
        if option == "1":
            p2p.show_broadcast_messages = not p2p.show_broadcast_messages
        elif option == "2":
            DisplayOnlineNodes(p2p.DHT)
        elif option == "3":
            receiver = input("Receiver: ")
            message = input("Message: ")
            p2p.send_message(message, receiver)
        elif option == "4":
            message = input("Message: ")
            p2p.send_message(message, p2p.last_sender)
        elif option == "5":
            DisplayAllFilesInNetwork(p2p.DHT)
        elif option == "6":
            DisplayPublicFiles(p2p.DHT)
        elif option == "7":
            file_to_add_to_public = input("File to add to public: ")
            if file_to_add_to_public in p2p.node.files:
                p2p.node.public_files.append(file_to_add_to_public)
        elif option == "8":
            file_to_request = input("File to request: ")
            from_node = input("From: ")
            p2p.request_public_file(file_to_request, from_node)
        elif option == "9":
            p2p.online = False
            break

if __name__ == "__main__":
    username = input("Enter username: ")
    p2p = P2P.createP2P(username)
    p2p.join_network()
    Program(p2p)