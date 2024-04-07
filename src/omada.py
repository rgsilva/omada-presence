import requests
import datetime
from typing import Optional

# Suppress InsecureRequestWarning
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def _fail(resp):
    raise Exception(f"unexpected: {resp.status_code}, {resp.text}")

def validate_response(resp):
    if resp.status_code != 200 or "application/json" not in resp.headers["Content-Type"]:
        _fail(resp)

class Omada:
    def __init__(self, host: str, username: str, password: str):
        self._host = host
        self._username = username
        self._password = password

        self._session = requests.session()
        self._session.verify = False
        self._endpoint: Optional[str] = None
        self._token: Optional[str] = None

    def _fail_if_not_ready(self):
        if self._endpoint is None:
            raise Exception("not ready")

    def _headers(self):
        return {"Csrf-Token": self._token}

    def login(self):
        resp = self._session.get(f"https://{self._host}", allow_redirects=False)
        if resp.status_code != 302:
            _fail(resp)
        self._endpoint = resp.headers["Location"].split("/login")[0]

        payload = {"username": self._username, "password": self._password}
        resp = self._session.post(f"{self._endpoint}/api/v2/login", json=payload)
        validate_response(resp)

        self._token = resp.json()["result"]["token"]

    def logout(self):
        self._fail_if_not_ready()

        resp = self._session.post(f"{self._endpoint}/api/v2/logout", headers=self._headers())
        validate_response(resp)

        self._endpoint = None
        self._token = None

    def sites(self):
        self._fail_if_not_ready()

        resp = self._session.get(f"{self._endpoint}/api/v2/sites?currentPageSize=1000&currentPage=1", headers=self._headers())
        validate_response(resp)

        return resp.json()["result"]["data"]
    
    def clients(self, site: str):
        self._fail_if_not_ready()

        now = datetime.datetime.now().timestamp()
        resp = self._session.get(f"{self._endpoint}/api/v2/sites/{site}/clients?currentPageSize=1000&currentPage=1&filters.active=true&_={now}", headers=self._headers())
        validate_response(resp)

        return resp.json()["result"]["data"]