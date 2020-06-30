from Crypto.Cipher import Blowfish
from Crypto import Random
from struct import pack
import logging
logger = logging.getLogger(__name__)

def encrypt_blowfish_CBC(key, plaintext) :
    bs = Blowfish.block_size
    iv = Random.new().read(bs)

    cipher = Blowfish.new(key, Blowfish.MODE_CBC, iv)
    
    # padding
    plen = bs - divmod(len(plaintext), bs)[1]
    padding = [plen]*plen
    padding = pack('b'*plen, *padding)

    ciphertext = iv + cipher.encrypt(plaintext + padding)
    return ciphertext


def decrypt_blowfish_CBC(key, ciphertext) : 
    bs = Blowfish.block_size
    iv = ciphertext[:bs] 
    ciphertext = ciphertext[bs:]

    cipher = Blowfish.new(key, Blowfish.MODE_CBC, iv)
    plaintext = cipher.decrypt(ciphertext)

    # remove padding
    last_byte = plaintext[-1]
    plaintext = plaintext[:-(last_byte if type(last_byte) is int else ord(last_byte))]
    return plaintext


def encrypt_file(cipher, key, src, dest) :
    """ encrypts the given file inplace """
    try :
        CIPHER = {
                'blowfish_CBC' : encrypt_blowfish_CBC
                }
        with open(src, 'rb') as f :
            plaintext = f.read()
        ciphertext = CIPHER[cipher](key, plaintext)
        with open(dest, 'wb') as f :
            f.write(ciphertext)
        return True
    except Exception as e :
        logger.error("{}:{}".format(e.__class__.__name__, str(e)))
        return False


def decrypt_file(cipher, key, src, dest) :
    """ decrypts the given file inplace """
    try :
        DECIPHER = {
                'blowfish_CBC' : decrypt_blowfish_CBC
                }
        with open(src, 'rb') as f :
            ciphertext = f.read()
        plaintext = DECIPHER[cipher](key, ciphertext)
        with open(dest, 'wb') as f :
            f.write(plaintext)
        return True
    except Exception as e :
        logger.error("{}:{}".format(e.__class__.__name__, str(e)))
        return False


if __name__ == "__main__" : 
    pass
