from DH import DH
from KES import KES
from Person import Person

class Communication:
    def __init__(self, alice: Person, bob: Person, dh: DH, kes: KES):
        self.alice = alice
        self.bob = bob
        self.dh = dh
        self.kes = kes
    
    def share_public_keys(self):
        self.dh.log(f"Sharing public keys between {self.alice.name} and {self.bob.name}")
        self.alice.counter_part_public_key = self.bob.public_key
        self.bob.counter_part_public_key = self.alice.public_key
    
    def generate_shared_keys(self):
        alice_shared_key = self.dh.generate_shared_key(self.alice.private_key, self.bob.counter_part_public_key, self.alice)
        bob_shared_key = self.dh.generate_shared_key(self.bob.private_key, self.alice.counter_part_public_key, self.bob)

        self.alice.shared_key = self.dh.BBS(alice_shared_key, 100, self.alice)
        self.bob.shared_key = self.dh.BBS(bob_shared_key, 100, self.bob)
        
        self.dh.log(f"Shared key for {self.alice.name} - {self.bob.name}: {self.alice.shared_key}")


    # Test the communication between Alice and Bob
    def test_communication(self):
        # Alice and Bob generates a private key and a public key
        _,_ = self.dh.generate_keys(self.alice), self.dh.generate_keys(self.bob)

        # Alice and Bob share their public keys
        self.share_public_keys()

        # Alice and Bob generate their shared key
        self.generate_shared_keys()

        # Alice generates a random message, encrypts it
        # Alice encrypts the message with the shared key
        # Alice sends the encrypted message to Bob
        # Bob decrypts the message with the shared key
        # Bob prints the decrypted message
        alice_message = "This is a secret message"
        alice_encrypted_message = self.kes.vigener_cipher(alice_message, self.alice.shared_key)
        bob_decrypted_message = self.kes.vigener_cipher(alice_encrypted_message, self.bob.shared_key, mode="decrypt")
        print(bob_decrypted_message)

if __name__ == "__main__":
    alice = Person("Alice")
    bob = Person("Bob")
    dh = DH.createDH(23, 5, "test")
    kes = KES()
    communication = Communication(alice, bob, dh, kes)
    communication.test_communication()