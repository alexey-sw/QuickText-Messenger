from cryptography.fernet import Fernet

class Key_Message:
    def __init__(self, key, message):
        self.key = key
        self.message = message


class Encryptor:
    def encrypt(self, text):#? (string)-> object
        text = text.encode()
        cypher_key = Fernet.generate_key()
        cipher = Fernet(cypher_key)
        encrypted_text = cipher.encrypt(text)
        return Key_Message(cypher_key, encrypted_text)


class Decryptor:
    def decrypt(self,key_message): #?(object)->string
        cypher_key = key_message.key
        text = key_message.message
        cypher_obj = Fernet(cypher_key)
        decrypted_text = cypher_obj.decrypt(text).decode()
        return decrypted_text
    
    
