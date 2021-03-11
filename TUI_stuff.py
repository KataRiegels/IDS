

import json
import requests
import npyscreen




# Returns a list of jobs based on the search terms (kwargs) given
def search(**kwargs):
    payload = ""
    for key, value in kwargs.items():                   # Goes through the keyword arguments
        payload += "{}={}&".format(key,value)           # formats the key for the search and the search choice so the string can be added to the url later
    payload = payload.rstrip(payload[-1])               # Removes the last &
    url_ = "https://jobs.github.com/positions.json?"    # The "base" part of the API address
    r = requests.get(url = url_ + payload)              # Gettings the API data
    response = r.json()                                 # Convers the json file into a list
    response = checkMorePages(response, url_, payload)  # Checks if there are more pages (see report for more info)
    return response

# The API can only give 50 responses at a time, so we may need to check more pages. See report for more.
def checkMorePages(response, url_, search_choice):
    size = 50                                                   # First time checking should only happen if it seems we reached max for the first page
    pages = 2                                                   # Starts at page 1, so we check second page
    more_pages = len(response) >= size and pages < 10           # Should check more pages if there are 50 responses
    while (more_pages):                                         # Continuously checks if we need to access more pages
        url__ = url_  + search_choice + '&page=' + str(pages)   # Contatinating url such that it can check different page numbers 
        r = requests.get(url = url__)                           # Getting API data
        response = response + r.json()                          # Appends the previous response with the most recent page. 
        pages += 1
        size += 50
        more_pages = len(response) >= size and pages < 10       # Updates loop ***REQUIREMENT**??? word??
    return response



"""
problem
implementation
how we worked???

"""


class App(npyscreen.NPSAppManaged):
    def onStart(self):
        npyscreen.setTheme(npyscreen.Themes.ColorfulTheme)              # Setting cute color theme
        # Adding all forms to the app
        self.addForm('MAIN',      getInputForm,       name = "Enter locations")
        self.addForm('NO_JOBS',   NoJobsForm,         name = "Error - no jobs")
        self.addForm('SHOW_JOBS', DisplayJobsForm,    name = "Job titles")
        self.addForm('JOB_INFO',  JobInformationForm, name = "info")

# Form that asks user to give a location and optional search keyword for finding a job
class getInputForm(npyscreen.ActionFormMinimal):
    def create (self):
        self.add(npyscreen.TitleText, w_id="locationText",    name = "Enter a location:")
        self.add(npyscreen.TitleText, w_id="descriptionText", name = "Enter optional keyword:")
    def afterEditing(self):
        self.jobs_list = []
        self.returner  = []
        self.location_input  = self.get_widget("locationText").value
        self.keywords_inputs = self.get_widget("descriptionText").value
        self.response        = search(location = self.location_input, search = self.keywords_inputs)
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
