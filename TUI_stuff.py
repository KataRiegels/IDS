

import json
import requests
import npyscreen


#cd Documents\4th sem\IDS\hand-in

# Returns string with the stuff we want to search for.
def search(**kwargs):
    payload = ""
    for key, value in kwargs.items():
        payload += "{}={}".format(str(key),value)
        payload += "&"
    payload = payload.rstrip(payload[-1])

    return payload
        

"""
problem
implementation
how we worked???

"""



# then represent it in the npyscreen application in the terminal
class App(npyscreen.NPSAppManaged):
    def onStart(self):
        #add forms to the application
        self.addForm('MAIN', FirstForm, name="main")

class FirstForm(npyscreen.ActionFormMinimal):
    def create (self):
        self.add(npyscreen.TitleText, w_id="titelText", name = "Enter a city:")
        self.add(npyscreen.ButtonPress, name="OK", when_pressed_function=self.btn_press)
    def btn_press(self):
        message = self.get_widget("titelText").value
        searching = search(location = message)
        url_ = "https://jobs.github.com/positions.json?"

        r = requests.get(url = url_ + searching) 
        response = r.json() 

        size = 50
        pages = 2   
        more_pages = len(response) >= size and pages < 6

        while (more_pages):
            url__ = url_  + searching + '&page=' + str(pages)
            print(url__)
            r = requests.get(url = url__) 

            response = response + r.json()
 
            pages += 1
            size += 50
            more_pages = len(response) >= size and pages < 6
            
        returner = ""
        for resp in response:
            
            returner = returner + resp['title']
            returner += "\n"

   
        npyscreen.notify_confirm(returner, title="Hi", wrap=True, wide=True, editw=1)
    def on_ok(self):
     self.parentApp.switchForm(None)

app = App()
app.run()

"""
Show: Job title
-> click title
-> open new page
-> shows title, company, location, company_url and where to apply
""



"""
import npyscreen

class App(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm('MAIN', FirstForm, name="main")

class FirstForm(npyscreen.ActionFormMinimal):
    def create(self):
        self.add(npyscreen.TitleText, w_id="txt", name= "Hello World" )
    def on_ok(self):
        self.parentApp.switchForm(None)

app = App()
app.run()
"""
