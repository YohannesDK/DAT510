from DH import DH
from KES import KES
from Person import Person

class SecureCommunication:
    def __init__(self, user: Person, dh: DH, kes: KES):
        self.user = user
        self.dh = dh
        self.kes = kes
     
    def generate_shared_keys(self):
        shared_key = self.dh.generate_shared_key(self.user.private_key, self.user.counter_part_public_key, self.user)
        self.user.shared_key = self.dh.BBS(shared_key, 8, self.user)
        self.dh.log(f"Shared key for {self.user.name}: {self.user.shared_key}")
    
    def store_counterpart_public_key(self, counter_part_public_key):
        self.user.counter_part_public_key = counter_part_public_key
    
    def Encrypt(self, message):
        ceasar_key = self.dh.generate_psuedo_random_ceasar_key()
        return self.kes.KES_cipher(message, ceasar_key, self.user.shared_key)
    
    def Decrypt(self, message):
        ceasar_key = self.dh.generate_psuedo_random_ceasar_key()
        return self.kes.KES_cipher(message, ceasar_key, self.user.shared_key, mode="decrypt")

    # factory method to create a Communication object
    @classmethod
    def createCommunication(cls, user: Person):
        return cls(user, DH.createDH(23, 5), KES.createKES())

# Test the communication between Alice and Bob
def test_communication(comm1: SecureCommunication, comm2: SecureCommunication):
    # Alice and Bob generates a private key and a public key
    _,_ = comm1.dh.generate_keys(comm1.user), comm1.dh.generate_keys(comm2.user)

    print("Alice", "public key", comm1.user.public_key, "private key", comm1.user.private_key)
    print("\n")
    print("Bob", "public key", comm2.user.public_key, "private key",comm2.user.private_key)

    # Alice and Bob share their public keys
    comm1.store_counterpart_public_key(comm2.user.public_key)
    comm2.store_counterpart_public_key(comm1.user.public_key)

    # Alice and Bob generate their shared key
    comm1.generate_shared_keys()
    comm2.generate_shared_keys()

    print("Alice", "shared key", comm1.user.shared_key)
    print("bob", "shared key", comm2.user.shared_key)

    # Alice encrypts the message with the shared key, and sends it to Bob
    # Bob decrypts the message with the shared key, and reads the message
    alice_message = "Hi bob"
    alice_encrypted_message = comm1.Encrypt(alice_message)
    bob_decrypted_message = comm2.Decrypt(alice_encrypted_message)
    print(bob_decrypted_message)

if __name__ == "__main__":
    alice = Person("Alice")
    bob = Person("Bob")
    comm1 = SecureCommunication.createCommunication(alice)
    comm2 = SecureCommunication.createCommunication(bob)
    test_communication(comm1, comm2)