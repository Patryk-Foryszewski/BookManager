from datetime import date

from bookmanager.books.utils import DEFAULT_COVER_URI


class RequestResponseMock:
    def __init__(self, json_data=None, status_code=200):
        if not json_data:
            json_data = {}
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


GOOGLE_API_JSON_RESPONSES_MOCK = {
    "empty": {
        "title": "",
        "author": "",
        "published_date": date.today().strftime("%Y-%m-%d"),
        "language": "",
        "isbn_10": "",
        "isbn_13": "",
        "pages": "",
        "id": "#",
        "cover_uri": DEFAULT_COVER_URI,
        "self_link": "",
    },
    "correct": {
        "title": "Mock",
        "author": "PF",
        "published_date": "2021-09-07",
        "language": "en",
        "isbn_10": "8365970392",
        "isbn_13": "9788365970398",
        "pages": "1",
        "id": "#",
        "cover_uri": DEFAULT_COVER_URI,
        "self_link": "",
    },
}
