

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
        
def checkMorePages(response, url_, search_choice):
    size = 50
    pages = 2   
    more_pages = len(response) >= size and pages < 6

    while (more_pages):
        url__ = url_  + search_choice + '&page=' + str(pages)
        print(url__)
        r = requests.get(url = url__) 

        response = response + r.json()

        pages += 1
        size += 50
        more_pages = len(response) >= size and pages < 6
    return response
    
def getAPI(message):
    searching = search(location = message)
    url_ = "https://jobs.github.com/positions.json?"
    r = requests.get(url = url_ + searching) 
    response = r.json() 
    response = checkMorePages(response, url_, searching)
    return response



"""
problem
implementation
how we worked???

"""



# then represent it in the npyscreen application in the terminal
class App(npyscreen.NPSAppManaged):
    def onStart(self):
        #add forms to the application
        self.addForm('MAIN', getInput, name="Enter locations")
        self.addForm('SHOW_JOBS', DisplayJobsForm, name="Job titles")

class getInput(npyscreen.ActionFormMinimal):
    def create (self):
        self.add(npyscreen.TitleText, w_id="titelText", name = "Enter a location:")

        #self.add(npyscreen.ButtonPress, name="OK", when_pressed_function=self.btn_press)
        self.mess = self.get_widget("titelText").value
    def afterEditing(self):
        response = getAPI(self.mess)
        returner = ""
        for resp in response:
            returner = returner + resp['title']
            returner += "\n"
        self.parentApp.switchForm('SHOW_JOBS')
        self.parentApp.getForm('SHOW_JOBS').response.value = response
    def on_ok(self):
        self.parentApp.switchForm('SHOW_JOBS')

class DisplayJobsForm(npyscreen.ActionFormMinimal):
    def create (self):
        self.response = self.add(npyscreen.TitleText, name="Chosen city:",     editable=False)

        #self.add(npyscreen.TitleText, w_id="titelText", name = "Enter a city:")
        self.add(npyscreen.ButtonPress, name="OK", when_pressed_function=self.btn_press)
        self.jobs = self.add(npyscreen.TitleSelectOne, scroll_exit=True, max_height=3, name='Department', values=self.response)
    def btn_press(self):
        response = getAPI(self.message)
        returner = ""
        for resp in response:
            returner = returner + resp['title']
            returner += "\n"
        npyscreen.notify_confirm(returner, title="Jobs", wrap=True, wide=True, editw=1)
    def on_ok(self):
        self.parentApp.switchForm(None)

app = App()
app.run()

"""
Show: Job title
-> click title
-> open new page
-> shows title, company, location, company_url and where to apply




"""
