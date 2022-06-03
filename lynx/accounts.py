import random

class Accounts:
    def __init__(self):
        #should point to the most recent distributed state chain
        self.balance = None

        #512 bit random generated string
        self.address = hex(random.getrandbits(512))

        #set to empty string by default 
        self.contractCode = ""

        #Storage set to None as per the Lynx whitepaper
        self.storage = None

