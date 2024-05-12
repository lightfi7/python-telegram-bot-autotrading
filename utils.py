from Crypto import Random
from Crypto.Cipher import AES

key = b'7f24a1b5c9d2f4e6'
iv = Random.new().read(AES.block_size)

def is_hex(s):
    try:
        bytes.fromhex(s)
        return True
    except ValueError:
        return False


def generate_key(user):
    cipher = AES.new(key, AES.MODE_CFB, iv)
    user_data = f'{user["id"]}@{user["username"]}'
    return ''.join(f'{byte:02X}' for byte in cipher.encrypt(user_data.encode('utf-8')))


def verify_key(user, token):
    cipher = AES.new(key, AES.MODE_CFB, iv)
    decrypted_str = cipher.decrypt(token)
    return decrypted_str.decode('utf-8') == f'{user.id}@{user.username}'


