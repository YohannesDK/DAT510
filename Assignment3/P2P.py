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
         "file6.txt", "file7.txt", "file8.txt", "file9.txt", "file10.txt"]

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
        self.DHT = {}
    
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
                    if data["type"] == "heartbeat":
                        if self.show_broadcast_messages:
                            print("Received heartbeat from", user_data["name"])
                        self.DHT[user_data["name"]] = {"ipaddress": user_data["ipaddress"], "files": user_data["files"], "public_key": user_data["public_key"]}
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
    
    def start(self):
        """
            This method starts the communication with the P2P network
        """
        th1 = threading.Thread(target=self.update_received)
        th1.start()
        th2 = threading.Thread(target=self.update_network)
        th2.start()
        
    # factory method
    @classmethod
    def createP2P(cls, username: str):
        user = Person(username)
        sc = SecureCommunication.createCommunication(user)
        sc.dh.generate_keys(sc.user)

        # find a free port
        port = Find_Free_Port()
        # create node
        node = Node(sc, (IP, port))
        print(f"P2P node created - username: {username}, port: {port}, files: {[]}, public_key: {sc.user.public_key}")

        return cls(node)

def Program(p2p: P2P):
    while True:
        print("1. Toggle broadcast messages")
        print("2. Show Online Nodes")
        print("3. Exit")
        option = input("Choose an option: ")
        if option == "1":
            p2p.show_broadcast_messages = not p2p.show_broadcast_messages
        elif option == "2":
            print(p2p.DHT)
        elif option == "3":
            p2p.online = False
            break

        

if __name__ == "__main__":
    username = input("Enter username: ")
    p2p = P2P.createP2P(username)
    p2p.start()
    Program(p2p)