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
    
    def KES_cipher(self, text, street_name, house_number, phone_nr, mode="encrypt", withimprovments=False):
        message = ""
        text = text.upper().replace(" ", "").replace("\n", "")

        if mode == "encrypt":
            message = self.ceasar_cipher(text, house_number)
            message = self.vigener_cipher(message, street_name)
        else:
            message = self.vigener_cipher(text, street_name, mode="decrypt")
            message = self.ceasar_cipher(message, house_number, mode="decrypt")
        return message