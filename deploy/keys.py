# Inspired from http://coding4streetcred.com/blog/post/Asymmetric-Encryption-Revisited-(in-PyCrypto)
# PyCrypto docs available at https://www.dlitz.net/software/pycrypto/api/2.6/

from Crypto import Random
from Crypto.PublicKey import RSA
import base64


def generate_keys():
    # RSA modulus length must be a multiple of 256 and >= 1024
    modulus_length = 256 * 4  # use larger value in production
    private_key = RSA.generate(modulus_length, Random.new().read)
    public_key = private_key.publickey()
    return private_key, public_key


def encrypt_message(a_message, public_key):
    encrypted_msg = public_key.encrypt(a_message.encode('utf-8'), 32)[0]
    encoded_encrypted_msg = base64.b64encode(encrypted_msg)  # base64 encoded strings are database friendly
    return encoded_encrypted_msg


def decrypt_message(encoded_encrypted_msg, private_key):
    decoded_encrypted_msg = base64.b64decode(encoded_encrypted_msg)
    decoded_decrypted_msg = private_key.decrypt(decoded_encrypted_msg)
    return decoded_decrypted_msg


a_message = "The quick brown fox jumped over the lazy dog"
private_key, public_key = generate_keys()
encrypted_msg = encrypt_message(a_message, public_key)
decrypted_msg = decrypt_message(encrypted_msg, private_key)

f = open('client/private_key.pem', 'wb')
f.write(private_key.exportKey('PEM'))
f.close()

f = open('client/public_key.pem', 'wb')
f.write(public_key.exportKey('PEM'))
f.close()

print("%s - (%d)" % (private_key.exportKey('PEM'), len(private_key.exportKey())))
print("%s - (%d)" % (public_key.exportKey('PEM'), len(public_key.exportKey())))
print(" Original content: %s - (%d)" % (a_message, len(a_message)))
print("Encrypted message: %s - (%d)" % (encrypted_msg, len(encrypted_msg)))
print("Decrypted message: %s - (%d)" % (decrypted_msg, len(decrypted_msg)))
