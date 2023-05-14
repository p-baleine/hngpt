import datetime
import logging
import requests
from bs4 import BeautifulSoup
from firebase import firebase
from pydantic import BaseModel
from tqdm.auto import tqdm
from typing import List, Optional

from .memory import memory

HN_BASE_URL = "https://hacker-news.firebaseio.com"

logger = logging.getLogger(__name__)


class HackerNewsStory(BaseModel):

    title: str
    id: int
    by: str
    score: int
    time: int
    type: str
    url: Optional[str] = None
    descendants: Optional[int] = None
    kids: Optional[List[int]] = []

    soup: Optional[BeautifulSoup] = None

    class Config:
        arbitrary_types_allowed = True

    @property
    def posted_at(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self.time).strftime("%Y/%m/%d %H:%M")

    def _repr_html_(self) -> str:
        return (
            "<div>"
            f"  <a href=\"{self.url}\" target=\"_blank\">{self.title}</a>&nbsp;"
            f"  <span class=\"score\">&nbsp;{self.score}&nbsp;points</span>"
            f"  <span class=\"by\">&nbsp;by &nbsp{self.by}</span>"
            f"  <span class=\"time\">&nbsp;at {self.posted_at}</span>"
            "</div>"
        )

    @classmethod
    def from_firebase_result(cls, result: dict) -> "HackerNewsStory":
        soup = None

        if "url" in result:
            resp = requests.get(result["url"])
            soup = BeautifulSoup(resp.content, "lxml")

        return cls(**result, soup=soup)


@memory.cache
def get_hn_topstories(n: int = 50) -> List[HackerNewsStory]:
    fb = firebase.FirebaseApplication(HN_BASE_URL)
    topstorie_ids = fb.get('/v0/topstories', None)

    return [
        HackerNewsStory.from_firebase_result(fb.get('/v0/item', id))
        for id in tqdm(topstorie_ids[:n])
    ]
