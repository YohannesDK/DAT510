from DH import DH
from Person import Person
from cryptography.fernet import Fernet
import base64

class SecureCommunication:
    def __init__(self, user: Person, dh: DH):
        self.user = user
        self.dh = dh
     
    def generate_shared_key(self, peer):
        peer_public_key = self.get_peers_public_key(peer)
        if peer_public_key is None:
            return None
        
        shared_key = self.dh.generate_shared_key(self.user.private_key, peer_public_key)
        self.store_peers_shared_key(peer, shared_key)
        self.dh.log(f"Shared key for {self.user.name} -> {peer} : {shared_key}")
    
    def get_peers_public_key(self, peer):
        return self.user.peers_public_keys[peer]

    def store_peers_public_key(self, peer, public_key):
        self.user.peers_public_keys[peer] = public_key
    
    def get_all_public_keys(self):
        return self.user.peers_public_keys
    
    def store_peers_shared_key(self, peer, shared_key):
        self.user.peers_shared_keys[peer] = shared_key
    
    def get_peers_shared_key(self, peer):
        return self.user.peers_shared_keys[peer]

    def get_all_shared_keys(self):
        return self.user.peers_shared_keys
    
    def generate_shared_fernet_key(self, shared_key: int):
        return base64.urlsafe_b64encode(shared_key.to_bytes(32, byteorder='big'))
    
    def generate_encryption_key(self, peer: str):
        shared_key = self.get_peers_shared_key(peer)
        public_key = None
        if shared_key is None:
            public_key = self.get_peers_public_key(peer)
            if public_key is None:
                return None
            shared_key = self.generate_shared_key(peer)
        
        shared_fernet_key = self.generate_shared_fernet_key(shared_key)
        return shared_fernet_key
    
    
    def Encrypt(self, file_name: str, peer: str) -> bytes:
        shared_fernet_key = self.generate_encryption_key(peer)
        fernet = Fernet(shared_fernet_key)
        with open(f"Files/{file_name}", 'rb') as file:
            file_data = file.read()
        file.close()
        return fernet.encrypt(file_data)

    
    def Decrypt(self, encrypted_file: bytes, peer: str) -> bytes:
        shared_fernet_key = self.generate_encryption_key(peer)
        fernet = Fernet(shared_fernet_key)
        return fernet.decrypt(encrypted_file)

    # factory method to create a Communication object
    @classmethod
    def createCommunication(cls, user: Person):
        return cls(user, DH.createDH(30000000091, 40000000003))

# Test the communication between Alice and Bob
def test_communication(alice_comm: SecureCommunication, bob_comm: SecureCommunication):
    FILE = "likeaboss.jpg"
    FILE_NAME, EXT = FILE.split(".")
    # Alice and Bob generates a private key and a public key
    _,_ = alice_comm.dh.generate_keys(alice_comm.user), alice_comm.dh.generate_keys(bob_comm.user)

    # Alice sends her public key to Bob
    alice_comm.store_peers_public_key(bob_comm.user.name, bob_comm.user.public_key)
    bob_comm.store_peers_public_key(alice_comm.user.name, alice_comm.user.public_key)

    alice_comm.generate_shared_key(bob_comm.user.name)
    bob_comm.generate_shared_key(alice_comm.user.name)

    # encrypting the file, using Bob's public key
    print("Alice encrypts the file using Bob's public key")
    encrypted = alice_comm.Encrypt(f'{FILE}', bob_comm.user.name)

    # writing the encrypted data
    with open(f'EncryptionTest/{FILE_NAME}.encrypted.{EXT}', 'wb') as encrypted_file:
        encrypted_file.write(encrypted)
    
    # decrypting the file
    with open(f'EncryptionTest/{FILE_NAME}.encrypted.{EXT}', 'rb') as enc_file:
        encrypted_read = enc_file.read()
    
    print("Bob decrypts the file using Alice's public key")
    decrypted = bob_comm.Decrypt(encrypted_read, alice_comm.user.name)
    with open(f'EncryptionTest/{FILE_NAME}.decrypted.{EXT}', 'wb') as dec_file:
        dec_file.write(decrypted)

if __name__ == "__main__":
    alice = Person("Alice")
    bob = Person("Bob")
    comm1 = SecureCommunication.createCommunication(alice)
    comm2 = SecureCommunication.createCommunication(bob)
    test_communication(comm1, comm2)