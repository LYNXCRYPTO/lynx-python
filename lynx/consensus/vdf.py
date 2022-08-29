from cmath import sqrt
from random import random
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from math import log

class VDF:

    @classmethod
    def create_vdf(self, a: int, t: int, data: str):
        rsa_key = RSA.generate(bits=1024)
        
        phi = (rsa_key.p - 1) * (rsa_key.q - 1) # phi should be included in cipher and block
        random_key = rsa_key.d
        key = b'Sixteen byte key'

        # Figure out which mode to use
        cipher = AES.new(key, AES.MODE_ECB)
        # Figure out if nonce is needed
        nonce = cipher
        ciphertext, tag = cipher.encrypt(data)
        print(nonce)
        print(tag)

        helper = pow(a, t, phi) # helper = 2^t (mod phi(n))
        b = pow(a, helper, rsa_key.n) # b = a^helper (mod n)
        sig_ciphertext = random_key + b

        return (rsa_key.n, a, t, ciphertext, sig_ciphertext)

    @classmethod
    def sequential_squaring(self, n: int, a: int, t: int) -> int:

        b = pow(a, pow(2, t), n)

        return b

    @classmethod
    def verify(self,):
        pass

    