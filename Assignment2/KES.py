import string

class KES:
    def __init__(self):
        self.ALPHABET = string.ascii_uppercase
    
    def ceasar_cipher(self, text, key, mode="encrypt"):
        message = ""
        text = text.upper().replace(" ", "").replace("\n", "")
        cipher_alpha = self.ALPHABET[key:] + self.ALPHABET[:key] # shift the alphabet by key positions

        # mapping between the two alphabets
        alpha_dict = dict(zip(cipher_alpha, self.ALPHABET)) if mode == "decrypt" else dict(zip(self.ALPHABET, cipher_alpha))
        for c in text:
            message += alpha_dict[c]
        return message
    
    def vigener_cipher(self, text, key, mode = 'encrypt'):
        message = ""
        text = text.upper().replace(" ", "").replace("\n", "")
        key = key.upper()

        for i in range(len(text)):
            if mode == "encrypt":
                message += self.ALPHABET[(ord(text[i]) + ord(key[i % len(key)])) % 26]
            else:
                message += self.ALPHABET[(ord(text[i]) - ord(key[i % len(key)])) % 26]
        return message
    
    def KES_cipher(self, text, ceasar_key, vigener_key, mode="encrypt"):
        message = ""
        text = text.upper().replace(" ", "").replace("\n", "")

        if mode == "encrypt":
            message = self.ceasar_cipher(text, ceasar_key)
            message = self.vigener_cipher(message,vigener_key )
        else:
            message = self.vigener_cipher(text, vigener_key, mode="decrypt")
            message = self.ceasar_cipher(message, ceasar_key, mode="decrypt")
        return message
    
    @classmethod
    def createKES(cls):
        return cls()