from cryptography.fernet import Fernet


def generate_key():
    key = Fernet.generate_key()
    key = key.decode()
    return key 


def encrypt(text, key):  # ? (string)-> object
    try:
        
        key = key.encode()
    except:
        print("Key is already encoded")
        
    text = text.encode()
    cypher = Fernet(key)
    encrypted_text = cypher.encrypt(text)
    encrypted_text = encrypted_text.decode()
    return encrypted_text

def decrypt (text,key):  # ?(object)->string
    try:
        key = key.encode()
    except:
        print("Key is already encoded")
    text = text.encode()
    cypher = Fernet(key)
    decrypted_text = cypher.decrypt(text)
    decrypted_text = decrypted_text.decode()
    return decrypted_text


