# coding: utf-8
"""
    This file is part of WikiCorpus.

    WikiCorpus is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    WikiCorpus is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with WikiCorpus.  If not, see <https://www.gnu.org/licenses/>.
"""
import inquirer
from pathlib import Path
import logging
import re
from wasabi import msg
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import sys
import time


class Utils:
    def __init__(self, config):
        self.articles_file_id = 0
        self.c = config

    def check_file(self, reuse_file_mode=False, suffix=None):
        suffix = "-" + suffix if suffix is not None else ""
        csv_file = Path(self.c.ARTICLES_FILE +
                        str(self.articles_file_id) +
                        suffix + "." +
                        self.c.ARTICLES_FILE_FORMAT)

        if reuse_file_mode is True:
            files = Path("../csv").glob("*.csv")
            question = [
                inquirer.List("files",
                              message="¿Qué archivo desea utilizar?",
                              choices=list(files)
                              ),
            ]

            answers = inquirer.prompt(question)

            return answers["files"]

        while csv_file.exists():
            self.articles_file_id += 1
            csv_file = Path(self.c.ARTICLES_FILE +
                            str(self.articles_file_id) +
                            suffix + "." +
                            self.c.ARTICLES_FILE_FORMAT)

        if not csv_file.exists():
            with open(csv_file, "w"):
                logging.info(f"{csv_file} creado")

        return csv_file

    def clean_wikitext(self, to_clean):
        return str(to_clean).replace("[[wikipedia:es:", "").replace("]]", "")

    def clean_wikidata(self, to_clean):
        return str(to_clean).replace("[[wikidata:", "").replace("]]", "")

    def clean_category(self, to_clean):
        return self.clean_wikitext(str(to_clean).replace("Categoría:", ""))

    def oldid_url(self, oldid):
        return ("https://es.wikipedia.org/w/index.php?oldid=" +
                str(oldid))

    def html_object(self, url):
        return BeautifulSoup(requests.get(url).text, "html.parser")

    def count_html_references(self, url):
        tag = "div"
        tag_class = "listaref"

        if not self.html_object(url).find("div", "listaref"):
            tag = "ol"
            tag_class = "references"

            if not self.html_object(url).find(tag, tag_class):
                return 0

            # return "<references/>"

        return sum(1 for reference in self.html_object(url).find(
            tag, tag_class).find_all("li", id=re.compile("cite_note")))\
            if self.html_object(url).find("li", id=re.compile("cite_note")) else 0

    def count_files(self, article):
        params = (("action", "parse"),
                  ("utf8", "1"),
                  ("format", "json"),
                  ("pageid", str(article.pageid)),
                  ("prop", "wikitext"))
        request = requests.get(self.c.ESWIKI_API, params=params)

        json_data = request.json()
        pattern = re.compile("\.((jpg|png|gif|svg|JPG|PNG|GIF|SVG))\|?\]?")

        # Falta implementar el conteo de imágenes en plantillas o en tablas
        return sum(1 for image in re.finditer(pattern, json_data["parse"]["wikitext"]["*"]))

    def check_bibliography_index_section(self, article):
        params = (("action", "parse"),
                  ("format", "json"),
                  ("utf8", "1"),
                  ("pageid", str(article.pageid)),
                  ("prop", "sections"))
        request = requests.get(self.c.ESWIKI_API, params=params)

        json_data = request.json()

        for section in json_data["parse"]["sections"]:
            if "Bibliografía" in section["line"]:
                return section["index"]

    def count_html_bibliography(self, article):
        index_section = self.check_bibliography_index_section(article)
        params = (("action", "parse"),
                  ("format", "json"),
                  ("utf8", "1"),
                  ("pageid", str(article.pageid)),
                  ("prop", "wikitext"),
                  ("section", index_section))
        request = requests.get(self.c.ESWIKI_API, params=params)

        if index_section is not None:
            json_data = request.json()
            pattern = re.compile("(\*|\{\{[C|c]it|\n(\w|\[\[\w))(?!\[\[Categor)")

            return sum(1 if pattern.match(item) else 0
                       for item in json_data["parse"]["wikitext"]["*"].split("\n"))
        else:
            return 0

    def interwiki(self, wd_item):
        params = (("action", "wbgetentities"),
                  ("format", "json"),
                  ("utf8", "1"),
                  ("ids", wd_item),
                  ("props", "sitelinks"))
        request = requests.get(self.c.WIKIDATA_API, params=params)

        json_data = request.json()

        return sum(1 if len(interwiki) >= 1 else 0
                   for interwiki in json_data["entities"][wd_item]["sitelinks"])

    def commons_category_p373(self, wd_item):
        params = (("action", "wbgetclaims"),
                  ("format", "json"),
                  ("utf8", "1"),
                  ("property", "P373"),
                  ("entity", wd_item))
        request = requests.get(self.c.WIKIDATA_API, params=params)

        json_data = request.json()

        return (json_data["claims"]["P373"][0]["mainsnak"]["datavalue"]["value"]
                if "P373" in json_data["claims"] else None)

    def commons_category_sitelink(self, wd_item):
        params = (("action", "wbgetentities"),
                  ("format", "json"),
                  ("utf8", "1"),
                  ("ids", wd_item),
                  ("props", "sitelinks"))
        request = requests.get(self.c.WIKIDATA_API, params=params)

        json_data = request.json()

        try:
            return json_data["entities"][wd_item]["sitelinks"]["commonswiki"]["title"]
        except KeyError:
            pass

    def commons_category(self, wd_item):
        return (self.commons_category_p373(wd_item),
                self.commons_category_sitelink(wd_item))

    def run_selenium(self):
        return webdriver.Firefox()

    def report_time(self, start_time):
        elapsed_time = time.perf_counter() - start_time
        msg.info(f"Tiempo de ejecución: {elapsed_time:0.2f} segundos")

    def should_continue():
        question = [inquirer.confirm("continue",
                                     message="¿Debería continuar?")]

        answers = inquirer.prompt(question)

        if answers is True:
            pass

        else:
            sys.exit(0)
