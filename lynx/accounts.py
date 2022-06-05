import random
import glob
import json

class Accounts:
    def __init__(self):
        self.address = hex(random.getrandbits(512))
        self.contractCode = ""
        self.storage = None
        self.balance = self.getBalance()


    def getBalance(self):
        #sets the directory which the state chain .dat files are located
        directory = f"./accounts/{self.address}/states"


        #itterates through the files 
        for filename in glob.iglob(f'{directory}/*'):

            #opens as json and reads the balance of the state chain object
            with open(f"{filename}") as datfile:
                data = json.load(datfile)

        #returns most recent blance which is set to the self.balance attribute
        return data["balance"]

