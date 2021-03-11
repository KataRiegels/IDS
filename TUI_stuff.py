

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
    url_ = "https://jobs.github.com/positions.json?"
    r = requests.get(url = url_ + payload) 
    response = r.json() 
    response = checkMorePages(response, url_, payload)
    return response

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



"""
problem
implementation
how we worked???

"""


class App(npyscreen.NPSAppManaged):
    def onStart(self):
        npyscreen.setTheme(npyscreen.Themes.ColorfulTheme)
        #add forms to the application
        self.addForm('MAIN',      getInput,           name = "Enter locations")
        self.addForm('NO_JOBS',   NoJobsForm,         name = "Error - no jobs")
        self.addForm('SHOW_JOBS', DisplayJobsForm,    name = "Job titles")
        self.addForm('JOB_INFO',  JobInformationForm, name = "info")

class getInput(npyscreen.ActionFormMinimal):
    def create (self):
        self.add(npyscreen.TitleText, w_id="locationText",    name = "Enter a location:")
        self.add(npyscreen.TitleText, w_id="descriptionText", name = "Enter optional discription:")
   
 
    def afterEditing(self):
        
        self.jobs_list = []
        self.returner  = []
    
        self.mess1 = self.get_widget("locationText").value
        self.mess2 = self.get_widget("descriptionText").value
        self.response = search(location = self.mess1, search = self.mess2)
        for resp in self.response:
            self.jobs_list.append(resp)
            self.returner.append(resp['title'])
        if len(self.jobs_list) < 1:
            self.parentApp.setNextForm("NO_JOBS")
        self.parentApp.getForm('SHOW_JOBS').job.values = self.returner

    
    def on_ok(self):
        self.parentApp.setNextForm("SHOW_JOBS")
    

class DisplayJobsForm(npyscreen.ActionForm):
    def create (self):
        self.job        = self.add(npyscreen.TitleSelectOne, scroll_exit=True, max_height=11,  name='Jobs')
        self.chosen_job =  [] 
        


    def afterEditing(self):
        if self.job.value:
            self.chosen_job =  self.parentApp.getForm('MAIN').jobs_list[self.job.value[0]]
            self.parentApp.getForm('JOB_INFO').job_company.value = self.chosen_job['company']
            self.parentApp.getForm('JOB_INFO').job_title.value = self.chosen_job['title']
            self.parentApp.getForm('JOB_INFO').job_location.value = self.chosen_job['location']
            self.parentApp.getForm('JOB_INFO').job_url.value = self.chosen_job['url']
    def on_cancel(self):
        self.parentApp.setNextForm('MAIN')
    def on_ok(self):
        self.parentApp.setNextForm("JOB_INFO")

class NoJobsForm(npyscreen.ActionPopup):
    def create(self):
        self.job_company = self.add(npyscreen.FixedText, name = "Error", value = "No jobs found :-( ")
    def on_ok(self):
        self.parentApp.setNextForm("MAIN")
    def on_cancel(self):
        self.parentApp.setNextForm("MAIN")



class JobInformationForm(npyscreen.ActionPopupWide):
    def create(self):
        self.job_company  = self.add(npyscreen.TitleText, name = "Company: ")
        self.job_title    = self.add(npyscreen.TitleText, name = "Job title: ")
        self.job_location = self.add(npyscreen.TitleText, name = "Location: ")
        self.job_url      = self.add(npyscreen.TitleText, name = "Job URL: ")
    def on_cancel(self):
        self.parentApp.setNextForm("SHOW_JOBS")
    def on_ok(self):
        self.parentApp.setNextForm(None)
     

app = App()
app.run()

"""


TO-DO
- fix naming
- Comments
- make stuff list


- Error handling

- write report


Show: Job title
-> click title
-> open new page
-> shows title, company, location, company_url and where to apply




"""
