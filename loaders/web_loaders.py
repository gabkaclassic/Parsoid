from abc import ABC
from enum import Enum
from typing import Dict
import re
import httpx
import json

from loaders.base import Loader


class Method(Enum):
    POST = "POST"
    GET = "GET"


class WebPageLoader(Loader, ABC):

    def __init__(
        self,
        url: str,
        method: Method = Method.GET,
        headers: Dict[str, str] = None,
        body: Dict[str, str] = None,
    ):
        self.url = url
        self.headers = headers or dict()
        self.body = body or dict()
        self.method = method

    def load_data(self):
        self.setup_cookies()

        with httpx.Client() as client:
            if self.method == Method.GET:
                response = client.get(self.url, headers=self.headers)
            else:
                response = client.post(self.url, headers=self.headers, data=self.body)

            try:
                return json.loads(response.text)
            except Exception as e:
                print("Failed to parse response:", e)
                return response.text

    def setup_cookies(self):
        pass


class MIETScheduleLoader(WebPageLoader):

    def __init__(self, group: str):
        super().__init__(
            url="https://miet.ru/schedule/data",
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "DNT": "1",
                "Sec-GPC": "1",
                "Connection": "keep-alive",
                "Referer": "https://miet.ru/schedule/",
                "Cookie": "",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Priority": "u=0, i",
                "TE": "trailers",
            },
            body={"group": group},
            method=Method.POST,
        )
        self.group = group

    def setup_cookies(self):
        with httpx.Client() as client:
            response = client.get(
                f"https://miet.ru/schedule/#{self.group}", headers=self.headers
            )
            wl = self.__get_wl(response.text)
            self.headers["Cookie"] = f"wl={wl}"
            response = client.get(
                f"https://miet.ru/schedule/#{self.group}", headers=self.headers
            )
            cookie = response.cookies.get("MIET_PHPSESSID")
            self.headers["Cookie"] = (
                f"{self.headers['Cookie']}; MIET_PHPSESSID={cookie}"
            )

    def __get_wl(self, html_content: str):
        pattern = r'document\.cookie="wl=([^;]+);'
        match = re.search(pattern, html_content)
        if match:
            wl_value = match.group(1)
            return wl_value
