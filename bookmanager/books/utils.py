from datetime import date
from math import ceil
from typing import List

import requests
from django.conf import settings
from django.core.paginator import EmptyPage, Page, Paginator

DEFAULT_COVER_URI = "https://books.google.pl/googlebooks/images/no_cover_thumb.gif"
API = "https://www.googleapis.com/books/v1/volumes"

PAGINATE_BY = settings.PAGINATE_BY  # type: ignore
GOOGLE_API_QUERY_PARAMS = {"maxResults": PAGINATE_BY}


def identifiers_finder(identifiers):
    isbn_s = {"isbn_10": "", "isbn_13": ""}

    # Find isbn's in identifiers
    for identifier in identifiers:
        if identifier["type"].lower() == "isbn_10":
            isbn_s["isbn_10"] = identifier["identifier"]
        elif identifier["type"].lower() == "isbn_13":
            isbn_s["isbn_13"] = identifier["identifier"]

    return isbn_s


def google_book_parser(book):
    """Parse book item form google api response to Book model."""

    volume_info = book.get("volumeInfo", {})
    authors = volume_info.get("authors", [])
    authors = " ".join(authors) if len(authors) else ""
    cover_uri = volume_info.get("imageLinks", {}).get("thumbnail", DEFAULT_COVER_URI)
    published_date = volume_info.get("publishedDate", date.today().strftime("%Y-%m-%d"))
    language = volume_info.get("language", "")
    pages = volume_info.get("pageCount", "")
    identifiers = volume_info.get("industryIdentifiers", [])
    isbn_s = identifiers_finder(identifiers)

    book = {
        "title": volume_info.get("title", ""),
        "author": authors,
        "published_date": published_date,
        "language": language,
        "isbn_10": isbn_s["isbn_10"],
        "isbn_13": isbn_s["isbn_13"],
        "pages": pages,
        "id": book.get("id", "#"),
        "cover_uri": cover_uri,
        "self_link": volume_info.get("infoLink", ""),
    }
    return book


def get_paginator_page(paginator: Paginator, page: int) -> Page:
    """Get page results from given paginator and page."""
    try:
        items = paginator.page(page)
    except EmptyPage:
        index = 1
        for i, item in enumerate(paginator.object_list):
            if item:
                # if item is at index 0 return 1 so returned 'page' is not 0
                index = i + 1
                break

        page = ceil(index / PAGINATE_BY)
        items = paginator.page(page)

    return items


def create_paginator(items: list, total: int, page: int = 1) -> Paginator:
    """Create paginator for given total number of item.

    Google api returns total number and list of items where max is equal to
    PAGINATE_BY value. If e.g. total is 1000 and list of items contains 40
    items function creates list with lenght of total with items shifted to
    positions accorging to page:.
    """

    start_index = (page - 1) * PAGINATE_BY
    my_list = []
    top = PAGINATE_BY if PAGINATE_BY < len(items) else len(items)
    for i in range(total):
        if start_index <= i < start_index + top:
            my_list.append(items[i - start_index])
        else:
            my_list.append("")

    return Paginator(my_list, PAGINATE_BY)


def google_api_query(query_dict: dict) -> str:
    """Join given query args into one string.

    Return query string in format required by googlapis:
    https://developers.google.com/books/docs/v1/using#WorkingVolumes
    """
    if not query_dict:
        return ""

    def allowed_google_item():
        if item[1] and item[0] in ["intitle", "inauthor"]:
            return True
        return False

    query_string = f"q={query_dict.get('search', '')}"
    for i, item in enumerate(query_dict.items()):
        if allowed_google_item():
            query_string = f"{query_string}+{item[0]}:{item[1]}"
    return query_string


def get_google_api_books(query_dict: dict, params: dict = None, page: int = 1) -> tuple:
    """Get books from google api from given page."""
    query = google_api_query(query_dict)
    if not params:
        params = {}
    params.update(GOOGLE_API_QUERY_PARAMS)

    start_index = (page - 1) * PAGINATE_BY
    params.update({"startIndex": start_index})

    response = requests.get(f"{API}?{query}", params=params)
    books = []  # type: List[dict]
    total = 0
    if response.status_code == 200:
        result = response.json()
        total = result.get("totalItems", 0)
        for result in result.get("items", []):
            books.append(google_book_parser(result))

    return books, total, response.status_code
