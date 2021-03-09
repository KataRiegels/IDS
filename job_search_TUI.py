
import npyscreen
import requests

# sending get request and saving the response as response object 


# Returns string with the stuff we want to search for.
def search(**kwargs):
    payload = ""
    for key, value in kwargs.items():
        payload += "{}={}".format(str(key),value)
        payload += "&"
    payload = payload.rstrip(payload[-1])

    return payload
        
#askdj



searching = search( location = "europe",  description = "microsoft java")
url_ = "https://jobs.github.com/positions.json?"

r = requests.get(url = url_ + searching) 
response = r.json() 

size = 50
pages = 2   
more_pages = len(response) >= size and pages < 6
print(len(response))
while (more_pages):
    url__ = url_  + searching + '&page=' + str(pages)
    print(url__)
    r = requests.get(url = url__) 

    response = response + r.json()
    pages += 1
    size += 50
    more_pages = len(response) >= size and pages < 6


for q in range(len(response)):
    print(response[q]['title'])


"""
fix to search multiple pages if length returns 50



"""


print("done")