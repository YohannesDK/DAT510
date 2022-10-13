import logging
import os
import random
from Person import Person



class DH(object):
    def __init__(self, p, g, dh_name, logger, keyMax=1000000):
        self.p = p
        self.g = g
        self.dh_name = dh_name
        self.logger = logger
        self.keyMax = keyMax

    def generate_private_key(self, person: Person = None):
        private_key = random.randint(1, self.keyMax)
        if person is not None:
            self.logger.info(f"Generating private key - {private_key}, for {person.name}")
        return private_key
    
    def generate_public_key(self, private_key, person: Person = None):
        public_key = pow(self.g, private_key, self.p)
        if person is not None:
            self.logger.info(f"Generating public key - {public_key}, for {person.name}, with private key {person.private_key}")
        return public_key
    
    def generate_shared_key(self, private_key, public_key, person: Person = None):
        shared_key = pow(public_key, private_key, self.p)
        if person is not None:
            self.logger.info(f"Generating shared key - {shared_key}, for {person.name}")
        return shared_key
    
    def generate_keys(self, person: Person = None):
        private_key = self.generate_private_key(person=person)
        public_key = self.generate_public_key(private_key, person=person)

        if person is not None:
            person.private_key = private_key
            person.public_key = public_key
        return private_key, public_key
    
    def BBS(self, shared_key, length, person: Person = None):
        bits = ""
        for i in range(length):
            shared_key = pow(shared_key, 2, self.p)
            bits += str(shared_key % 2)

        if person is not None:
            self.logger.info(f"Generating BBS - {bits}, for {person.name}")
        # return "mama"
        return bits
    
    def log(self, message):
        self.logger.info(message)
    
    # factory method to create a DH object
    @classmethod
    def createDH(cls, p, g, dh_name="test"):
        print(f"Creating DH object with p={p}, g={g}, dh_name={dh_name}")
        logger_path = "./logs"

        # create folder if it doesn't exist
        if not os.path.exists(logger_path):
            os.makedirs(logger_path)
        
        logger_name = "DH.log"
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(logger_path + "/" + logger_name)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        logger.log(logging.INFO, f"DH - created with p = " + str(p) + " and g = " + str(g) + "-" * 50)
        return cls(p, g, dh_name, logger)

if __name__ == "__main__":
    dh_test = DH.createDH(23, 5, "test")
    print(dh_test.p, dh_test.g)

    