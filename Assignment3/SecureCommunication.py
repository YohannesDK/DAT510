from DH import DH
from KES import KES
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
    
    
    def Encrypt(self, file_name, peer):
        shared_key = self.get_peers_shared_key(peer)
        public_key = None
        if shared_key is None:
            p
            return None
    
    def Decrypt(self, message):
        ceasar_key = self.dh.generate_psuedo_random_ceasar_key()

    # factory method to create a Communication object
    @classmethod
    def createCommunication(cls, user: Person):
        return cls(user, DH.createDH(30000000091, 40000000003))

# Test the communication between Alice and Bob
def test_communication(comm1: SecureCommunication, comm2: SecureCommunication):
    # Alice and Bob generates a private key and a public key
    _,_ = comm1.dh.generate_keys(comm1.user), comm1.dh.generate_keys(comm2.user)

    print("\n")
    print("Alice", "public key", comm1.user.public_key, "private key", comm1.user.private_key)
    print("Bob", "public key", comm2.user.public_key, "private key",comm2.user.private_key)
    print("\n")

    # Alice sends her public key to Bob
    comm1.store_peers_public_key(comm2.user.name, comm2.user.public_key)
    comm2.store_peers_public_key(comm1.user.name, comm1.user.public_key)

    comm1.generate_shared_key(comm2.user.name)
    comm2.generate_shared_key(comm1.user.name)

    alice_bob_shared_key = comm1.get_peers_shared_key(comm2.user.name)
    bob_alice_shared_key = comm2.get_peers_shared_key(comm1.user.name)
    print("Generated Shared Keys", alice_bob_shared_key, bob_alice_shared_key)
    
    shared_fernet_key_alice = base64.urlsafe_b64encode(alice_bob_shared_key.to_bytes(32, byteorder='big'))
    shared_fernet_key_bob = base64.urlsafe_b64encode(bob_alice_shared_key.to_bytes(32, byteorder='big'))

    fernet_alice = Fernet(shared_fernet_key_alice)
    fernet_bob = Fernet(shared_fernet_key_bob)

    with open('Files/file1.txt', 'rb') as file:
        original = file.read()
        
    # encrypting the file
    encrypted = fernet_alice.encrypt(original)
    
    # opening the file in write mode and
    # writing the encrypted data
    with open('file1.encrypted.txt', 'wb') as encrypted_file:
        encrypted_file.write(encrypted)
    
    # decrypting the file
    with open('file1.encrypted.txt', 'rb') as enc_file:
        encrypted_read = enc_file.read()
    
    decrypted = fernet_bob.decrypt(encrypted_read)
    with open('file1.decrypted.txt', 'wb') as dec_file:
        dec_file.write(decrypted)

if __name__ == "__main__":
    alice = Person("Alice")
    bob = Person("Bob")
    comm1 = SecureCommunication.createCommunication(alice)
    comm2 = SecureCommunication.createCommunication(bob)
    test_communication(comm1, comm2)