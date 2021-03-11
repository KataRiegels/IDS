

import json
import requests
import npyscreen


#cd Documents\4th sem\IDS\hand-in

# Returns string with the stuff we want to search for.
def search(**kwargs):
    payload = ""
    print(f"kwargs: {kwargs}")
    for key, value in kwargs.items():
        payload += "{}={}".format(str(key),value)
        payload += "&"
        print(f'Payload: {payload}')
    print(f'Payload: {payload}')
    payload = payload.rstrip(payload[-1])
    print(f'Payload: {payload}')
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
    
def getAPI(loc):
    searching = search(location = loc)
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
        self.addForm('JOB_INFO', JobInformationForm, name="info")

class getInput(npyscreen.ActionFormMinimal):
    def create (self):
        self.add(npyscreen.TitleText, w_id="titelText", name = "Enter a location:")
        self.returner = []
        #self.add(npyscreen.ButtonPress, name="OK", when_pressed_function=self.btn_press)

    def afterEditing(self):
        self.mess = self.get_widget("titelText").value
        print(f"message: {self.mess}")
        self.response = getAPI(self.mess)
        for resp in self.response:
            self.returner.append(resp['title'])
        self.parentApp.switchForm('SHOW_JOBS')
        self.parentApp.getForm('SHOW_JOBS').jobs.values = self.returner
    def on_ok(self):
        self.parentApp.switchForm('SHOW_JOBS')

class DisplayJobsForm(npyscreen.ActionFormMinimal):
    def create (self):
        self.jobs = self.add(npyscreen.TitleSelectOne, scroll_exit=True, max_height=10,  name='Jobs')
        self.add(npyscreen.ButtonPress, name="OK", when_pressed_function=self.btn_press)
    def btn_press(self):
        npyscreen.notify_confirm(self.jobs, title="Jobs")
    def on_ok(self):
        self.parentApp.switchForm(None)


class JobInformationForm(npyscreen.ActionFormMinimal):
    def create():
        self.job_info = self.add(npyscreen.TitleText, name = "Job discription", value = )

app = App()
app.run()

"""
Show: Job title
-> click title
-> open new page
-> shows title, company, location, company_url and where to apply




"""
