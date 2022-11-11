from DH import DH
from Person import Person
from cryptography.fernet import Fernet
import base64

class SecureCommunication:
    def __init__(self, user: Person, dh: DH):
        self.user = user
        self.dh = dh
        self.fernet_instances = {}
     
    def init_peer_file_transfer(self, peer) -> Fernet:
        peer_public_key = self.get_peers_public_key(peer)
        shared_key = None
        if peer_public_key is None:
            return None
        
        if peer not in self.user.peers_shared_keys:
            shared_key = self.dh.generate_shared_key(self.user.private_key, peer_public_key)
            self.store_peers_shared_key(peer, shared_key)
            self.dh.log(f"Shared key for {self.user.name} -> {peer} : {shared_key}")

        if peer not in self.fernet_instances:
            shared_fernet_key = self.generate_shared_fernet_key(shared_key)
            fernet = Fernet(shared_fernet_key)
            self.fernet_instances[peer] = fernet
        else:
            fernet = self.get_fernet_instance(peer)

        return fernet
    
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
    
    def generate_fernet_encryption_key(self, peer: str, shared_key=None) -> bytes:
        shared_key = self.get_peers_shared_key(peer) if shared_key is None else shared_key
        public_key = None
        if shared_key is None:
            public_key = self.get_peers_public_key(peer)
            if public_key is None:
                return None
            shared_key = self.init_peer_file_transfer(peer)
        
        shared_fernet_key = self.generate_shared_fernet_key(shared_key)
        return shared_fernet_key
    
    def get_fernet_instance(self, peer: str):
        return self.fernet_instances[peer]
    
    def Encrypt(self, fernet: Fernet, file: bytes) -> bytes:
        return fernet.encrypt(file)

    
    def Decrypt(self, fernet: Fernet, file: bytes) -> bytes:
        return fernet.decrypt(file)

    # factory method to create a Communication object
    @classmethod
    def createCommunication(cls, user: Person):
        return cls(user, DH.createDH(30000000091, 40000000003))

# Test the communication between Alice and Bob
def test_communication(alice_comm: SecureCommunication, bob_comm: SecureCommunication):
    BUFFER = 1024
    FILES = ["file1.txt", "file2.txt", "file3.txt"]
    FILE = FILES[1]
    FILE_NAME, EXT = FILE.split(".")
    # Alice and Bob generates a private key and a public key
    _,_ = alice_comm.dh.generate_keys(alice_comm.user), alice_comm.dh.generate_keys(bob_comm.user)

    # Alice sends her public key to Bob
    alice_comm.store_peers_public_key(bob_comm.user.name, bob_comm.user.public_key)
    bob_comm.store_peers_public_key(alice_comm.user.name, alice_comm.user.public_key)

    bob_fernet = alice_comm.init_peer_file_transfer(bob_comm.user.name)
    alice_fernet = bob_comm.init_peer_file_transfer(alice_comm.user.name)

    
    # encrypting the file, using Bob's public key
    print("Alice encrypts the file using Bob's public key and generating a shared key")
    with open(f"Files/{FILE}", "rb") as file:
        while True:
            bytes_read = file.read(BUFFER)
            if not bytes_read:
                break
            encrypted_bytes = alice_comm.Encrypt(bob_fernet, bytes_read)
            # then its sent to Bob
            with open(f'EncryptionTest/{FILE_NAME}.encrypted.{EXT}', "wb") as encrypted_file: # file is written
                encrypted_file.write(encrypted_bytes)

    # decrypting the file
    print("Bob decrypts the file using Alice's public key and generating the same shared key")
    with open(f'EncryptionTest/{FILE_NAME}.encrypted.{EXT}', 'rb') as enc_file:
        while True:
            bytes_read = enc_file.read(BUFFER)
            if not bytes_read:
                break
            decrypted_bytes = bob_comm.Decrypt(alice_fernet, bytes_read)
            with open(f'EncryptionTest/{FILE_NAME}.decrypted.{EXT}', 'wb') as dec_file:
                dec_file.write(decrypted_bytes)

if __name__ == "__main__":
    alice = Person("Alice")
    bob = Person("Bob")
    comm1 = SecureCommunication.createCommunication(alice)
    comm2 = SecureCommunication.createCommunication(bob)
    test_communication(comm1, comm2)