

import json, requests, os 
import npyscreen as nps
import ascii_conv
import pyperclip







def ascii_art(file):
    fil = open(f'{file}.txt', "r")
    file_list = fil.read().splitlines()
    ascii_array = []
    for line in file_list:
        ascii_array.append([line])
    return ascii_array
            




#----------- Functions used to get API responses ------------------------------------------- 


# Returns a list of jobs based on the search terms (kwargs) given
def jobSearchAPI(**kwargs):
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
    response_size_limit = 50                                           # First time checking should only happen if it seems we reached max for the first page
    pages = 2                                                          # Starts at page 1, so we check second page
    more_pages = len(response) >= response_size_limit and pages < 10   # Should check more pages if there are 50 responses
    while (more_pages):                                                # Continuously checks if we need to access more pages
        url__ = url_  + search_choice + '&page=' + str(pages)          # Contatinating url such that it can check different page numbers 
        r = requests.get(url = url__)                                  # Getting API data
        response = response + r.json()                                 # Appends the previous response with the most recent page. 
        pages += 1
        response_size_limit += 50
        more_pages = len(response) >= response_size_limit and pages < 10       # Updates loop condition
    return response


"""
def move_ok_button(self):
    if hasattr(self, 'ok_button'):
        my, mx = self.curses_pad.getmaxyx()
        my -= self.__class__.OK_BUTTON_BR_OFFSET[0]
        mx -= len(self.__class__.OK_BUTTON_TEXT)+self.__class__.OK_BUTTON_BR_OFFSET[1]
        self.ok_button.relx = mx
        self.ok_button.rely = my

"""

def testing(self):
    


# -------------- App and Forms for the TUI -----------------------------------------

class App(nps.NPSAppManaged):
    def onStart(self):
        nps.setTheme(nps.Themes.ColorfulTheme)              # Setting cute color theme
        # Adding all forms to the app
        self.addForm('MAIN',      getInputForm,       name = "Enter locations")
        self.addForm('NO_JOBS',   NoJobsForm,         name = "Error - no jobs")
        self.addForm('SHOW_JOBS', DisplayJobsForm,    name = "Job titles")
        self.addForm('JOB_INFO',  JobInformationForm, name = "info")
    def exit(self):
        self.switchForm(None)

# Form that asks user to give a location and optional search keyword for finding a job
class getInputForm(nps.ActionFormMinimal):
    def create (self):
        self.form_art = ascii_art("computer_ascii")
        print(len(self.form_art[0][0]))
        my, mx = self.curses_pad.getmaxyx()
        print(mx)
        self.add(nps.FixedText, w_id="locationTexta",    name = str(my)) 
        self.add(nps.TitleText, w_id="locationText",    name = "Enter a location:           ", use_two_lines = False, begin_entry_at=30)     # Widget for taking location user input
        self.add(nps.TitleText, w_id="descriptionText", name = "Enter optional keywords:    ", use_two_lines = False, begin_entry_at=30)     # Widget for taking extra keyword user input
        self.add(nps.SimpleGrid, values = self.form_art, columns_width = 100, columns = 1, editable = False, rely = -len(self.form_art), relx = round(mx/2-len(self.form_art[0][0])/2 ) )
        self.add(nps.ButtonPress, name="Continue", when_pressed_function=self.contin_btn, rely = -5, relx = -15)
        print(self.get_widget(   "locationText").value)


    def contin_btn(self, *args, **kwargs):
        self.jobs_list       = []                                                                         # Creating (and resetting) empty list of jobs
        self.job_list_titles = []                                                                         # Creating (and resetting) empty list of titles from the jobs
        self.location_input  = self.get_widget(   "locationText").value                                       # Getting location input from user
        self.keywords_inputs = self.get_widget("descriptionText").value                                    # Getting other keywords input from user
        self.response        = jobSearchAPI(location = self.location_input, search = self.keywords_inputs) # Using the API to look for jobs at the given location and keywords
        for resp in self.response:                                                                         # Adding API response to lists
            self.jobs_list.append(resp)                                                                         # List with dictionaries for all response jobs
            self.job_list_titles.append(resp['title'])                                                          # List with values for the 'title' key for all response jobs
        if len(self.jobs_list) < 1:                                                                        # If no jobs were found
            self.parentApp.switchForm("NO_JOBS")                                                               # Show error popup saying there are no jobs
        else:
            self.parentApp.getForm('SHOW_JOBS').jobs.values = self.job_list_titles                             # Setting the values of the job list widget
            self.parentApp.switchForm("SHOW_JOBS")
    def on_ok(self):
        self.parentApp.exit()
        #self.parentApp.setNextForm(None)
        #self.parentApp.setNextForm("SHOW_JOBS")                                                            # Go to form that show list of available jobs               
    

# Form that will display the jobs that match search criteria and saves information about a job the user wants to see
class DisplayJobsForm(nps.ActionForm):
    def create (self):
        self.jobs       = self.add(nps.TitleSelectOne, scroll_exit=True, max_height=11,  name='Jobs') # Widget that allows user to see and pick available jobs
        self.chosen_job =  []                                                                               # Creating empty chosen job list
        self.add(nps.ButtonPress, name="Continue", when_pressed_function = self.contin_btn, rely = -10)
        self.add(nps.ButtonPress, name="Return",   when_pressed_function = self.return_btn, rely = -5, color = "DANGER")

    def return_btn(self):
        self.parentApp.switchFormPrevious()

    def contin_btn(self):
    #def afterEditing(self):
        if self.jobs.value:                                                                             # If there were actually any jobs
            self.chosen_job =  self.parentApp.getForm('MAIN').jobs_list[self.jobs.value[0]]             # Saving dictionary for chosen job
            self.parentApp.getForm('JOB_INFO').job_company.value = self.chosen_job['company']           # sets chosen company value
            self.parentApp.getForm('JOB_INFO').job_title.value = self.chosen_job['title']               # Sets chosen title value
            self.parentApp.getForm('JOB_INFO').job_location.value = self.chosen_job['location']         # Sets location value
            self.parentApp.getForm('JOB_INFO').job_url.value = self.chosen_job['url']                   # Sets github url value
            self.parentApp.switchForm('JOB_INFO')
        # else what?   
    def on_cancel(self):
        self.parentApp.setNextForm('MAIN')                                                              # Cancelling take user back to search form
    def on_ok(self):
        self.parentApp.exit()
        #self.parentApp.setNextForm("JOB_INFO")                                                          # Ok continues to show job info about chosen job

# Popup in case there were no jobs matching the search criteria
class NoJobsForm(nps.ActionPopup):
    def create(self):
        self.job_company = self.add(nps.FixedText, name = "Error", value = "No jobs found :-( Try with other search terms", editable = False)
    def on_ok(self):
        self.parentApp.setNextForm("MAIN")
    def on_cancel(self):
        self.parentApp.setNextForm("MAIN")

# Popup that shows information about the job the user picked in the DisplayJobsForm
class JobInformationForm(nps.ActionPopupWide):
    def create(self):
        # Widgets that will display the values assigned in DisplayJobsForm
        self.job_company  = self.add(nps.TitleText, name = "Company: ",   editable = False)
        self.job_title    = self.add(nps.TitleText, name = "Job title: ", editable = False)
        self.job_location = self.add(nps.TitleText, name = "Location: ",  editable = False)
        self.job_url      = self.add(nps.TitleFixedText, name = "Job URL: ")
        self.copy_hint    = self.add(nps.FixedText, value = "Press CTRL+C / CMD+C to copy URL", relx = 20, color = 'CURSOR', editable = False)
        self.add(nps.ButtonPress, name="Return", when_pressed_function=self.return_btn, rely = 10, color = "DANGER")

        self.add_handlers({"^C": self.handler})
    def handler(self):
        pyperclip.copy(self.job_url.value)
        spam = pyperclip.paste()


    def return_btn(self):
        self.parentApp.switchFormPrevious()

    def on_cancel(self):                                                            # Go back to choose another job
        self.parentApp.setNextForm("SHOW_JOBS")
    def on_ok(self):
        self.parentApp.exit()
        #self.parentApp.setNextForm(None)                                            # Leave the application
     

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
