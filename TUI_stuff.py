

import json, requests, pyperclip
import npyscreen as nps







# Takes a file with ascii art and converts it to a two dimensional list to be used for npyscreen's grid widget.
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
    # Gettings and converting the API data
    url_ = "https://jobs.github.com/positions.json?"    
    r = requests.get(url = url_ + payload)              
    response = r.json()                                 
    response = checkMorePages(response, url_, payload)  # Checks if there are more pages (see report for more info)
    return response

# The API can only give 50 responses at a time, so we may need to check more pages. See report for more.
def checkMorePages(response, url_, search_choice):
    response_size_limit = 50                                           # First time checking should only happen if it seems we reached max for the first page
    pages = 2                                                          # Starts at page 1, so we check second page
    more_pages = len(response) >= response_size_limit and pages < 10   # Should check more pages if there are 50 responses
    while (more_pages):                                                
        url__ = url_  + search_choice + '&page=' + str(pages)         
        r = requests.get(url = url__)                                  
        response = response + r.json()                                 # Appends the previous response with the most recent page. 
        pages += 1
        response_size_limit += 50
        more_pages = len(response) >= response_size_limit and pages < 10       
    return response




# ---------------------- Subclassing npyscreens forms -------------------------------------------------------------------------

# Subclassing npyscreen's ActionFormV2 in order to remove the "cancel" and "ok" buttons and add our own buttons. Additional functionality added
class ActionForm_edited(nps.ActionFormV2):
    # Function that overrides the creation of cancel and ok button
    def create_control_buttons(self):
        pass
    # Function that can find and return the max x and y for a Form
    def max_dim(self):
        my, mx = self.curses_pad.getmaxyx()
        return my,mx

    # Function that will return the position a widget (mainly for ascii art) should be placed if wanted placed in the middle
    def half_dim(self, widget):
        halfy = self.max_dim()[0]/2                     # y value at middle of screen       
        halfx = self.max_dim()[1]/2                     # x value at middle of screen
        pos_halfy = round(halfy-len(widget)/2)          # y value for ascii art if it should be at the middle
        pos_halfx = round(halfx-len(widget[0][0])/2)    # x value for ascii art if it should be at the middle
        return pos_halfx, pos_halfy
    
    # Adds ascii art to the form and places it at midbottom -> 
    def addAsciiArt(self, ascii_art_file):
        self.form_art = ascii_art(ascii_art_file)
        halfx, halfy = self.half_dim(self.form_art)  
        self.add(nps.SimpleGrid, values = self.form_art,  columns = 1, color = "CAUTIONHL", editable = False, rely = -len(self.form_art)-2, relx = halfx) 

    # Function that subclasses this should overwrite to choose what "continue" should do
    def contin_btn(self):
        pass

    # Added for function addButtons below, since when_pressed_function's input cannot take the None argument
    def exitApp(self):
        self.parentApp.switchForm(None)

   # Adds buttons to a form. Each form can get multiple of the possible buttons: Continue, return and Exit application. 
    def addButtons(self, *names):
        for name in names:
            if name == "continue":   # Behvaior depends on specific form. 
                self.add(nps.ButtonPress, name="Continue",         when_pressed_function = self.contin_btn, rely = -7, color = "LABEL")
            elif name == "return":   # Returns to previous form
                self.add(nps.ButtonPress, name="Return",           when_pressed_function = self.parentApp.switchFormPrevious, rely = -5, color = "WARNING")
            elif name == "exit":     # "Exit" button will close the application
                self.add(nps.ButtonPress, name="Exit application", when_pressed_function=  self.exitApp,    rely = -3, color = "DANGER")


# Subclassing custom ActionFormV2 to make a popup form. Changes size and position of form.
class ActionPopup_edited(ActionForm_edited):
    DEFAULT_COLUMNS = 50
    DEFAULT_LINES   = 14
    SHOW_ATX        = 10
    SHOW_ATY        = 2

# Subclassing custom ActionFormV2 to make a wide popup form. Changes size and position of form.
class ActionPopupWide_edited(ActionForm_edited):
    DEFAULT_COLUMNS = None
    DEFAULT_LINES   = 14
    SHOW_ATY        = 2




# -------------- APPS AND FORMS FOR THE TUI -----------------------------------------

# Defines the colors of the theme. Especially useful for choosing colors for a specific widget (e.g. making "Exit application" red)
class DefaultTheme(nps.ThemeManager):
    default_colors = {
    'DEFAULT'     : 'MAGENTA_BLACK',
    'FORMDEFAULT' : 'BLUE_BLACK',
    'NO_EDIT'     : 'BLUE_BLACK',
    'STANDOUT'    : 'CYAN_BLACK',
    'CURSOR'      : 'BLUE_BLACK',
    'CURSOR_INVERSE': 'BLACK_WHITE',
    'LABEL'       : 'GREEN_BLACK',
    'LABELBOLD'   : 'CYAN_BLACK',
    'CONTROL'     : 'YELLOW_BLACK',
    'IMPORTANT'   : 'GREEN_BLACK',
    'SAFE'        : 'GREEN_BLACK',
    'WARNING'     : 'YELLOW_BLACK', 
    'DANGER'      : 'RED_BLACK',
    'CRITICAL'    : 'BLACK_RED',
    'GOOD'        : 'GREEN_BLACK',
    'GOODHL'      : 'WHITE_BLACK',
    'VERYGOOD'    : 'BLACK_GREEN',
    'CAUTION'     : 'YELLOW_BLACK',
    'CAUTIONHL'   : 'MAGENTA_BLACK',
    }

# Parent app for the forms we use
class App(nps.NPSAppManaged):
    def onStart(self):
        nps.setTheme(DefaultTheme)              # Setting cute color theme
        # Adding all forms to the app
        self.addForm('MAIN',            getInputForm,       name = "Job Search")
        self.addForm('NO_JOBS',         NoJobsForm,         name = "Error - no jobs")
        self.addForm('SHOW_JOBS',       DisplayJobsForm,    name = "Job titles")
        self.addForm('JOB_INFO',        JobInformationForm, name = "Job information")
        self.addForm('NO_JOB_SELECTED', NoSelectedJobForm,  name = "Error - no job selected")


# Form that asks user to give a location and optional search keyword for finding a job
class getInputForm(ActionForm_edited):
    def create (self):
        self.location_input  = ''
        self.keywords_inputs = ''
        self.how_to_use = "Enter location and/or optional search keywords to see\navailable job positions from GitHub Jobs matching the search.\nTo search for multiple keywords, separate with whitespace."
        self.add(nps.MultiLineEdit, value = self.how_to_use, relx = 10, editable = False)                                                              # Widget displaying how to use the form
        self.add(nps.TitleText, w_id="locationText",    name = "Enter a location:           ", use_two_lines = False, begin_entry_at=30, rely = 6)     # Widget for taking location user input
        self.add(nps.TitleText, w_id="descriptionText", name = "Enter optional keywords:    ", use_two_lines = False, begin_entry_at=30, rely = 8)     # Widget for taking extra keyword user input
        self.addButtons("continue","exit")      
        self.addAsciiArt("computer2_ascii")

    # What happens when user chooses the continue button
    def contin_btn(self):
        self.jobs_list       = []                                                                         
        self.job_list_titles = [] 
        # Saving the input for location and keywords given by user                                                                  
        self.location_input  = self.get_widget(   "locationText").value                                       
        self.keywords_inputs = self.get_widget("descriptionText").value   
        # Using the API to look for jobs at the given location and keywords                                    
        self.response        = jobSearchAPI(location = self.location_input, search = self.keywords_inputs)    
        # Adding API response to lists
        for resp in self.response:                                                                            
            self.jobs_list.append(resp)                     # To get the list of jobs                                                             
            self.job_list_titles.append(resp['title'])      # To display titles for user                                                     
        
        if len(self.jobs_list) < 1:                # If no jobs were found, show NO_JOBS error Form                                                            
            self.parentApp.switchForm("NO_JOBS")                                           
        else:                                      # If jobs were found, continue to next form
            # Setting the values of the job list widget                          
            self.parentApp.getForm('SHOW_JOBS').jobs.values = self.job_list_titles                             
            self.parentApp.getForm('SHOW_JOBS').nr_of_jobs.value = str(len(self.jobs_list)) 
            # Used for resetting jobs lists things in case the user returned to choose new search terms
            self.parentApp.getForm('SHOW_JOBS').jobs.value = []
            self.parentApp.getForm('SHOW_JOBS').chosen_job = []

            self.parentApp.switchForm("SHOW_JOBS")
  
# Form that will display the jobs that match search criteria and saves information about a job the user wants to see
class DisplayJobsForm(ActionForm_edited):
    def create (self):
        self.chosen_job =  []    
        self.nr_of_jobs = self.add(nps.TitleText, w_id = "nr jobs", name = "Jobs found: ", editable = False, begin_entry_at=12, use_two_lines = False)
        self.jobs       = self.add(nps.TitleSelectOne, scroll_exit=True, max_height=11,  name='Jobs') # Widget that allows user to see and pick available jobs                                                    
        self.addButtons("continue", "return", "exit")
        self.addAsciiArt("computer2_ascii")

    # Search for jobs whenever user pressed the "continue" button
    def contin_btn(self):
        if self.jobs.value:                                                                             # If there were actually any jobs
            self.chosen_job =  self.parentApp.getForm('MAIN').jobs_list[self.jobs.value[0]]             # Saving dictionary for chosen job
            # Adds values to the job information for chosen job
            self.parentApp.getForm('JOB_INFO').job_company.value  = self.chosen_job['company']       
            self.parentApp.getForm('JOB_INFO').job_title.value    = self.chosen_job['title']          
            self.parentApp.getForm('JOB_INFO').job_location.value = self.chosen_job['location']         
            self.parentApp.getForm('JOB_INFO').job_url.value      = self.chosen_job['url']             
            self.parentApp.switchForm('JOB_INFO')
        else:                                                                                            # In case no job from the list was selected
            self.parentApp.switchForm('NO_JOB_SELECTED')        




# Popup that shows information about the job the user picked in the DisplayJobsForm
class JobInformationForm(ActionPopupWide_edited):
    def create(self):
        # Widgets that will display the values assigned in DisplayJobsForm
        self.job_company      = self.createInfoLine("Company: ")
        self.job_title        = self.createInfoLine("Job Title: ")
        self.job_location     = self.createInfoLine("Location")
        self.job_url          = self.createInfoLine("Job url: ")
        self.job_url.editable = None
        self.copy_hint        = self.add(nps.FixedText, value = "Press CTRL+C / CMD+C to copy URL", 
                                     relx = 30, color = 'GOODHL', editable = False)                 # Hints user on copying URL
        self.add_handlers({"^C": self.clipboard})                                                   # Makes ctrl+c / cmd+c copy the job's github url
        self.addButtons("return", "exit")
    
    # Function that creates widgets for the jop information lines
    def createInfoLine(self, name):
        return self.add(nps.TitleText, name = name, editable = False, relx = 4)
    # Copies the url of the job  
    def clipboard(self, *args):                                                                     
        pyperclip.copy(self.job_url.value)      


# --------------- ERROR FORMS --------------------------------------

# Popup in case there were no jobs matching the search criteria
class NoJobsForm(ActionPopup_edited):
    def create(self):
        self.job_company = self.add(nps.MultiLineEdit, name = "Error", value = "No jobs found :-(\nTry again with other search terms.", editable = False)
        self.addButtons("return", "exit")

# Popup in case no jobs are chosen in the DisplayJobsForm
class NoSelectedJobForm(ActionPopup_edited):
    def create(self):
        self.add(nps.MultiLineEdit, name = 'Error', value = "No job selected.\nPlease select a job for more information.", editable = False)
        self.addButtons("return", "exit")


app = App()
app.run()

