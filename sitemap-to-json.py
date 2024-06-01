import json
import requests
from bs4 import BeautifulSoup
import html2text
from urllib.parse import urlparse


def page_to_json(url):
    r = requests.get(url=url, timeout=10)
    soup = BeautifulSoup(r.content, "html.parser")
    for script in soup(["script", "style"]):
        script.extract()

    main_soup = soup.find(id="et-main-area")

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


if __name__ == "__main__":
    with open("all_links.json", "r", encoding="utf-8") as f:
        links = json.load(f)
        all_info = []
        try:
            for link in links[7:]:
                print(link)
                all_info.append(page_to_json(link))
        finally:
            with open("data.json", "w", encoding="utf-8") as f:
                json.dump(all_info, f, indent=2)
