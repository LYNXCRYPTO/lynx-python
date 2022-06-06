import random
import glob
import os
import json

class Accounts:
    def __init__(self):
        self.address = hex(random.getrandbits(512))
        self.contractCode = ""
        self.storage = None
        self.balance = self.getBalance()


    def getBalance(self):
        try:
            #opens as json and reads the balance of the state chain object
            file_list = os.listdir(f"./accounts/{self.address}/states/")

            with open(f"./accounts/{self.address}/states/{file_list[-1]}") as datfile:
                data = json.load(datfile)

            #returns most recent blance which is set to the self.balance attribute
            return data["balance"]
        except:
            return None

newAccount = Accounts()
print(newAccount.balance)

