import time
import json

from urllib.parse import urlparse
from requests.exceptions import Timeout, TooManyRedirects, RequestException, HTTPError
from bs4 import BeautifulSoup
import requests
import html2text
import lxml  # pylint: disable=unused-import

from links import get_links


all_links = []
error_links = []


def access_page(url):
    """
    - accesses the pages using requests and beautiful soup.
    - handles requests errors to the page and if the soup is None
    """
    while True:
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            soup = BeautifulSoup(r.content, "lxml")
            main_soup = soup.find(id="main-content")
            if main_soup is not None:
                return soup, main_soup
            else:
                continue
        except Timeout:
            print("Request timed out. Retrying...")
            continue
        except TooManyRedirects as e_tmr:
            error_links.append(url)
            print("Too many redirects.")
            raise TooManyRedirects(e_tmr) from e_tmr
        except HTTPError as e_http:
            if "599" in str(e_http):
                print("Internal Server Error, waiting 4 seconds and then retrying")
                time.sleep(4)
                continue
            else:
                error_links.append(url)
                print(f"HTTP error: {e_http}")
                raise HTTPError(e_http) from e_http
        except RequestException as e:
            error_links.append(url)
            print(f"An error occurred: {e}")
            raise RequestException(e) from e


def page_to_json(url):
    """
    - gets correct soup, main_soup from access_page method
    - converts main part of soup to markdown page
    - extracts the metadata from the soup
    - returns content and metadata
    """
    try:
        soup, main_soup = access_page(url)
    except Exception:  # pylint: disable=broad-exception-caught
        return

    for script in main_soup(["script", "style"]):
        script.extract()

    html = str(main_soup)
    html2text_instance = html2text.HTML2Text()
    html2text_instance.images_to_alt = True
    html2text_instance.body_width = 0
    html2text_instance.single_line_break = True
    text = html2text_instance.handle(html)

    # Extract page metadata
    try:
        page_title = soup.title.string.strip()
    except AttributeError:
        parsed_url = urlparse(url)
        page_title = parsed_url.path[1:].replace("/", "-")

    meta_description = soup.find("meta", attrs={"name": "description"})
    meta_keywords = soup.find("meta", attrs={"name": "keywords"})
    if meta_description:
        description = meta_description.get("content")
    else:
        description = page_title
    if meta_keywords:
        keywords = meta_keywords.get("content")
    else:
        keywords = ""

    metadata = {
        'title': page_title,
        'url': url,
        'description': description,
        'keywords': keywords
    }
    return {"content": text, "metadata": metadata}


def main(links_list: list):
    """
    - loops through links and creates a request out of them
    - creates data.json and errored_data.json for new data
    """
    for index, link in enumerate(links_list):
        print(index, link)
        link_dict = page_to_json(link)
        all_links.append(link_dict)
    with open("data_3.json", "w", encoding="utf-8") as f:  # remember to change name
        json.dump(all_links, f, indent=2)
    with open("errored_data_3.json", "w", encoding="utf-8") as f:  # change this too
        json.dump(error_links, f, indent=2)


if __name__ == "__main__":
    # for all links
    links = get_links()
    main(links)  # from the function in other links.py file

    # retry on errored links
    # with open("errored_data.json", "r", encoding="utf-8") as f:
    #     links = json.load(f)
    #     main(links)
