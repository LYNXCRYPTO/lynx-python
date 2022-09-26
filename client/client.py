from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.datatables import MDDataTable
# to change the kivy default settings we use this module config
from kivy.config import Config
    
# 0 being off 1 being on as in true / false
# you can use 0 or 1 && True or False
Config.set('graphics', 'resizable', True)


class ClientWindow(MDBoxLayout):
    def __init__(self, **kwargs):
        super(ClientWindow,self).__init__(**kwargs)
class ClientApp(MDApp):
    def build(self):
        return ClientWindow()


if __name__ == "__main__":
    ClientApp().run()

