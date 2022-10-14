# Secure Communication

This readme explains the steps to run the secure communication program.

## Steps to run the program

1. pip install -r requirements.txt - This will install all the necessary packages.
2. python server.py - to run the server
3. python client.py Alice - to run the client for a person named Alice (can be any name)
4. python client.py Bob - to run the client for a person named Bob (can be any name)
5. Follow options in the client console to send messages and other options.


## Explanation

* Client.py - user interface for the client
* server.py - server to handle the communication
* KES.py - KES class to handle encryption and decryption
* DH.py - Diffie-Hellman class to handle key exchange
* Person.py - dataclass to store the person's name, public key, private key...
* SecureCommunication.py - class for handling client side state and data encryption and decryption


## To Run Part I
    - python SecureCommunication.py