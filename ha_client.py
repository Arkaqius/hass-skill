from requests import get, post
import json
from requests.exceptions import Timeout, RequestException

__author__ = 'origin = btotharye, Arkaqius (changes)'

# Timeout time for HA requests
TIMEOUT = 10

class HomeAssistantClient(object):

    def __init__(self,url,port,token, ssl=False, verify=True):
        self.ssl = ssl
        self.verify = verify
        portnum = port
        host = url
        
        if self.ssl:
            self.url = "https://{}".format(host)
        else:
            self.url = "http://{}".format(host)
        if portnum:
            self.url = "{}:{}".format(self.url, portnum)
        self.headers = {
            'Authorization': 'Bearer '+f'{token}',
            'Content-Type': 'application/json'
        }

    def _get_state(self,entity_id=None):
        """Get state object

        Throws request Exceptions
        (Subclasses of ConnectionError or RequestException,
          raises HTTPErrors if non-Ok status code)
        """

        if entity_id is None: #Fetch all entities
            if self.ssl:
                req = get("{}/api/states".format(self.url), headers=self.headers,
                        verify=self.verify, timeout=TIMEOUT)
            else:
                req = get("{}/api/states".format(self.url), headers=self.headers,
                        timeout=TIMEOUT)
            req.raise_for_status()
        else:
            if self.ssl:
                req = get("{}/api/states/{}".format(self.url,entity_id), headers=self.headers,
                        verify=self.verify, timeout=TIMEOUT)
            else:
                req = get("{}/api/states/{}".format(self.url,entity_id), headers=self.headers,
                        timeout=TIMEOUT)
            req.raise_for_status()

        return req.json()
        
    def connected(self):
        try:
            self._get_state()
            return True
        except (Timeout, ConnectionError, RequestException):
            return False

    def execute_service(self, domain, service, data):
        """Execute service at HAServer

        Throws request Exceptions
        (Subclasses of ConnectionError or RequestException,
          raises HTTPErrors if non-Ok status code)
        """
        if self.ssl:
            r = post("{}/api/services/{}/{}".format(self.url, domain, service),
                     headers=self.headers, data=json.dumps(data),
                     verify=self.verify, timeout=TIMEOUT)
        else:
            r = post("{}/api/services/{}/{}".format(self.url, domain, service),
                     headers=self.headers, data=json.dumps(data),
                     timeout=TIMEOUT)
        r.raise_for_status()
        return r