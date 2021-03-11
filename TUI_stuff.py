

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
        print("TEST")
        self.returner = []
        self.jobs_list = []

    def afterEditing(self):
    #def edit(self):
        
        self.jobs_list = []
        self.returner = []
        self.mess = self.get_widget("titelText").value
        self.response = getAPI(self.mess)
        for resp in self.response:
            self.jobs_list.append(resp)
            self.returner.append(resp['title'])
        
        #self.parentApp.switchForm('SHOW_JOBS')
        self.parentApp.getForm('SHOW_JOBS').job.values = self.returner


    
    def on_ok(self):
        self.parentApp.setNextForm("SHOW_JOBS")
        #self.parentApp.switchForm('SHOW_JOBS')

class DisplayJobsForm(npyscreen.ActionForm):
    def create (self):
        self.job = self.add(npyscreen.TitleSelectOne, scroll_exit=True, max_height=10,  name='Jobs')
        self.chosen_job =  [] #self.parentApp.getForm('MAIN').jobs_list[self.job.value[0]]
        
        self.add(npyscreen.ButtonPress, name="OK", when_pressed_function=self.btn_press)
        self.add(npyscreen.TitleText, name="Press CTRL + T")
        self.add_handlers({"^T": self.handler})
    def handler(self, *args, **keywords):
        self.parentApp.setNextForm(None)

    def afterEditing(self):
        if self.job.value:
            self.chosen_job =  self.parentApp.getForm('MAIN').jobs_list[self.job.value[0]]
            
            self.parentApp.getForm('JOB_INFO').job_company.value = self.chosen_job['company']
            self.parentApp.getForm('JOB_INFO').job_title.value = self.chosen_job['title']
            self.parentApp.getForm('JOB_INFO').job_location.value = self.chosen_job['location']
            self.parentApp.getForm('JOB_INFO').job_url.value = self.chosen_job['url']
        #self.parentApp.getForm('JOB_INFO').job_how_to_apply.value = chosen_job['how_to_apply']

    def on_cancel(self):
        #self.parentApp.switchFormPrevious()
        self.parentApp.setNextForm('MAIN')
         
    def btn_press(self):
        self.parentApp.setNextForm('JOB_INFO')
        #npyscreen.notify_confirm(self.jobs, title="Jobs")
    def on_ok(self):
        self.parentApp.setNextForm("JOB_INFO")
        #self.parentApp.switchForm('JOB_INFO')


class JobInformationForm(npyscreen.ActionPopup):
    def create(self):
        #self.display = self.add(npyscreen.FixedText, name = "display", value = "Job description for ")
        self.job_company = self.add(npyscreen.TitleText, name = "Company: ")
        self.job_title = self.add(npyscreen.TitleText, name = "Job title: ")
        self.job_location = self.add(npyscreen.TitleText, name = "Location: ")
        self.job_url = self.add(npyscreen.TitleText, name = "Job URL: ")
        #self.job_how_to_apply = self.add(npyscreen.TitleText, name = "How to apply: ")

    def on_cancel(self):
        self.parentApp.setNextForm("SHOW_JOB")

    
    def on_ok(self):
        self.parentApp.setNextForm(None)
     

app = App()
app.run()

"""
Show: Job title
-> click title
-> open new page
-> shows title, company, location, company_url and where to apply




"""
