from cryptography.fernet import Fernet

def generate_key():#? (None)-> byte 
    key = Fernet.generate_key()
    return key


def encrypt(text, key):  # ? (string,byte)-> object
    text = text.encode()
    cypher = Fernet(key)
    encrypted_text = cypher.encrypt(text)
    encrypted_text = encrypted_text.decode()
    return encrypted_text


def decrypt(text, key):  # ?(string,byte)->string
    text = text.encode()
    cypher = Fernet(key)
    decrypted_text = cypher.decrypt(text)
    decrypted_text = decrypted_text.decode()
    return decrypted_text


key = generate_key()
string = "hello"
string = encrypt(string, key)
string = decrypt(string, key)
print(string)
