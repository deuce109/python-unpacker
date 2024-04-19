import requests
import bs4 as bs


class PlexAPI:
    def __init__(self,  token: str, base_url:str ="localhost", port:int =32400):
        self.token = token
        self.base_url = base_url
        self.port = port

    token: str
    base_url: str
    port: int

    def _generate_library_info(self, libraries):
        for library in libraries:
            library_info = {}
            library_info['title'] = library['title']
            library_info['key'] = library['key']
            library_info['path'] = library.find('location')['path']
            yield library_info

    def get_libraries(self):
        # http://[PMS_IP_Address]:32400/library/sections?X-Plex-Token=YourTokenGoesHere

        request_url = f"http://{self.base_url}:{self.port}/library/sections?X-Plex-Token={self.token}"
        response = requests.get(request_url)
        library_info = bs.BeautifulSoup(response.text, 'lxml')

        return self._generate_library_info(library_info.find_all("directory"))


    def refresh_library(self, id):
        # http://[PMS_IP_ADDRESS]:32400/library/sections/29/refresh?X-Plex-Token=YourTokenGoesHere
        request_url = f"http://{self.base_url}:{self.port}/library/sections/{id}/refresh?X-Plex-Token={self.token}"
        requests.get(request_url)
