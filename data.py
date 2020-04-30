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
import asyncio
import logging
import random
import sys
import time

from wasabi import msg

# Pywikibot
import pywikibot as pwb
import mwparserfromhell as mwp

# Módulos propios
from config import Config as config
from wikicorpus.data import Data
from wikicorpus.utils import Utils

logging.basicConfig(filename="data.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
logging.getLogger("asyncio").setLevel(logging.DEBUG)


class Extract:
    def __init__(self, project, wd_item):
        self.project = project
        self.eswiki = pwb.Site("es", "wikipedia")
        self.wd = pwb.Site("wikidata", "wikidata")
        self.wd_item = pwb.page.ItemPage(self.wd, wd_item)

        try:
            self.eswiki_art = pwb.Page(self.eswiki,
                                       self.wd_item.getSitelink(self.eswiki))
        except pwb.exceptions.NoPage:
            self.eswiki_art = None

        self.commons = pwb.Site("commons", "commons")

        self.utils = Utils(config=config)

    def title(self):
        return self.eswiki_art.title() \
                if self.eswiki_art is not None \
                else ""

    def bytes(self):
        return len(self.eswiki_art.get().encode("utf-8")) \
                if self.eswiki_art is not None \
                else ""

    def words(self):
        return len(mwp.parse(self.eswiki_art.get()).strip_code().split()) \
                if self.eswiki_art is not None \
                else ""

    def creation_date(self):
        return self.eswiki_art.oldest_revision.timestamp \
                if self.eswiki_art is not None \
                else ""

    def creation_oldid(self):
        return self.eswiki_art.oldest_revision.revid \
                if self.eswiki_art is not None \
                else ""

    def creation_url(self):
        return self.utils.oldid_url(self.eswiki_art.oldest_revision.revid) \
                if self.eswiki_art is not None \
                else ""

    def latest_revision_date(self):
        return self.eswiki_art.editTime() \
                if self.eswiki_art is not None \
                else ""

    def latest_revision_oldid(self):
        return self.eswiki_art.latest_revision_id \
                if self.eswiki_art is not None \
                else ""

    def latest_revision_url(self):
        return self.utils.oldid_url(self.eswiki_art.latest_revision_id) \
                if self.eswiki_art is not None \
                else ""

    def editors(self):
        anonymous = 0
        registered = 0

        if self.eswiki_art is None:
            return {"anonymous": "",
                    "registered": "",
                    "top_editor": [[""]]}

        for contributor in self.eswiki_art.contributors().items():
            try:
                contributor_page = pwb.User(self.project, contributor[0])
            # TODO: redefinir este "bare except"
            except:
                pass

            if contributor_page.isAnonymous():
                anonymous += 1
            else:
                registered += 1

        return {"anonymous": anonymous if self.eswiki_art is not None else "",
                "registered": registered if self.eswiki_art is not None else "",
                "top_editor": self.eswiki_art.contributors().most_common(1)}

    def talk_page(self):
        return self.utils.clean_wikitext(self.eswiki_art.toggleTalkPage()) \
                if self.eswiki_art is not None and \
                self.eswiki_art.toggleTalkPage().exists() \
                else ""

    def talk_page_bytes(self):
        return len(pwb.Page(self.eswiki_art.toggleTalkPage()).get().encode("utf-8")) \
                if self.eswiki_art is not None and \
                self.eswiki_art.toggleTalkPage().exists() \
                else ""

    def talk_page_words(self):
        return len(mwp.parse(pwb.Page(self.eswiki_art.toggleTalkPage())
                             .get()).strip_code().split()) \
                if self.eswiki_art is not None and \
                self.eswiki_art.toggleTalkPage().exists() \
                else ""

    def links_from(self):
        return sum(1 for link in self.eswiki_art.backlinks()) \
                if self.eswiki_art is not None \
                else ""

    def links_to(self):
        return sum(1 for link in self.eswiki_art.linkedPages()) \
                if self.eswiki_art is not None \
                else ""

    def images_used(self):
        return self.utils.count_files(self.eswiki_art) \
                if self.eswiki_art is not None \
                else ""

    def references(self):
        return self.utils.count_html_references(self.latest_revision_url()) \
                if self.eswiki_art is not None \
                else ""

    def bibliography(self):
        return self.utils.count_html_bibliography(self.eswiki_art) \
                if self.eswiki_art is not None \
                else ""

    def wikidata_id(self):
        return self.utils.clean_wikidata(self.wd_item.getID())

    def wikidata_labels(self):
        return sum(1 for label in self.wd_item.get()["labels"])

    def wikidata_descriptions(self):
        return sum(1 for desc in self.wd_item.get()["descriptions"])

    def wikidataAliases(self):
        return sum(1 for alias in self.wd_item.get()["aliases"])

    def wikidata_claims(self):
        return sum(1 for claim in self.wd_item.get()["claims"]
                   if "external-id" not in pwb.page.Property(self.wd, claim).type)

    def wikidata_identifiers(self):
        return sum(1 for claim in self.wd_item.get()["claims"]
                   if "external-id" in pwb.page.Property(self.wd, claim).type)

    def wikidata_references(self):
        item = pwb.ItemPage(self.wd, self.utils.clean_wikidata(self.wd_item.getID()))
        itemClaims = item.get()["claims"]

        sources = []
        sources_p143 = []

        for x in itemClaims:
            for y in itemClaims[x]:
                sources.append(sum(1 for s in y.getSources()
                                   if y.getSources()))
                sources_p143.append(sum(1 for s in y.getSources()
                                        if "P143" in s if y.getSources()))

        return sum(sources), sum(sources_p143)

    def wikidata_interwiki(self):
        return self.utils.interwiki(self.wd_item.getID())

    def wikidata_commons_category(self):
        commons_category = self.utils.commons_category(self.wd_item.getID())[0]
        commons_sitelink = self.utils.commons_category(self.wd_item.getID())[1]

        if commons_category is not None and commons_sitelink is not None:
            if commons_category not in commons_sitelink.replace("Category:", ""):
                commons_category = f"{commons_category};{commons_sitelink.replace('Category:', '')}"
        elif commons_category is None and commons_sitelink is not None:
            commons_category = commons_sitelink.replace("Category", "")

        return (commons_category if commons_category is not None else "")

    def commons_categories(self):
        if self.wikidata_commons_category():
            category = pwb.Category(self.commons, self.wikidata_commons_category())

            try:
                return sum(1 for subcat in category.members(recurse=3, namespaces="Category")) \
                        if category.members(recurse=3, namespaces="Category") is not None \
                        else "0"

            except RecursionError as error:
                msg.fail(f"Ha ocurrido un error de recursión: {error}")
                return "Demasiadas subcategorías"

            except (ValueError, AttributeError) as error:
                msg.fail(f"Ha ocurrido un error inespereado: {error}")
                return "0"

        else:
            return 0

    def commons_files(self):

        if self.wikidata_commons_category():
            category = pwb.Category(self.commons, self.wikidata_commons_category())

            try:
                return sum(1 for image in category.members(recurse=3, namespaces="File"))

            except RecursionError as error:
                msg.fail(f"Ha ocurrido un error de recursión: {error}")
                return "Demasiadas subcategorías"

            except (ValueError, AttributeError) as error:
                msg.fail(f"Ha ocurrido un error inespereado: {error}")
                return "0"
        else:
            return 0


class DataApp:
    def __init__(self):
        self.utils = Utils(config=config)

        self.project = pwb.Site("wikidata", "wikidata")
        self.wd_item = pwb.page.ItemPage(self.project, "Q3")

        self.corpus = Data(columns=["id", "qid"])
        self.corpus_articles = Data(columns=config.CORPUS_ARTICLES_HEADER)

    def insert(self, data, row, column, corpus=None):
        if corpus is None:
            return self.corpus_articles.insert_at(data, row, column)
        else:
            return corpus.insert_at(data, row, column)

    def export(self, corpus=None):
        if corpus is None:
            return self.corpus_articles.export(config.CORPUS_ARTICLES_FILE)
        else:
            return corpus.export("../corpus/corpus_enlaces_a.csv")

    def process_data(self, row, header_id, data=None):
        if data is None:
            data = row

        msg.info(f"id: {row['qid']}")
        msg.good(f"{data}")

        try:
            self.insert(data, row["id"], header_id)
            self.export()
        except pwb.exceptions.InvalidTitle:
            msg.warn("Título invalido: {row['qid']}")
            logging.error("Título invalido: {row['qid']}")
            self.utils.should_continue()
        except pwb.exceptions.NoPage:
            msg.warn("No tiene página en eswiki: {row['qid']}")
            logging.error("No tiene página en eswiki: {row['qid']}")

        except pwb.exceptions.IsRedirectPage:
            # TODO: Se debe añadir un sistema por el que detectar que es una redirección y obtener
            # la página de destino, y luego trabajar con ella.
            msg.warn(f"Es una redirección: {row['qid']}")
            logging.error(f"Es una redirección: {row['qid']}")
            pass
        # TODO: redefinir este "bare except"
        except:
            msg.warn(f"Error inesperado: {sys.exc_info()[0]}")
            logging.error(f"Error inesperado: {sys.exc_info()[0]}")
            pass

    async def insert_id(self, row, delay):
        await asyncio.sleep(delay)
        self.process_data(row,
                          config.CORPUS_ARTICLES_HEADER[0],
                          data=row["id"])
        self.utils.report_time(self.start_time)

    async def insert_article_name(self, row, delay):
        await asyncio.sleep(delay)
        self.process_data(row,
                          config.CORPUS_ARTICLES_HEADER[1],
                          data=Extract(self.project, row["qid"]).title())
        self.utils.report_time(self.start_time)

    async def insert_bytes(self, row, delay):
        await asyncio.sleep(delay)
        self.process_data(row,
                          config.CORPUS_ARTICLES_HEADER[2],
                          data=Extract(self.project, row["qid"]).bytes())
        self.utils.report_time(self.start_time)

    async def insert_words(self, row, delay):
        await asyncio.sleep(delay)
        self.process_data(row,
                          config.CORPUS_ARTICLES_HEADER[3],
                          data=Extract(self.project, row["qid"]).words())
        self.utils.report_time(self.start_time)

    async def insert_creation_date(self, row, delay):
        await asyncio.sleep(delay)
        self.process_data(row,
                          config.CORPUS_ARTICLES_HEADER[4],
                          data=Extract(self.project, row["qid"]).creation_date())
        self.utils.report_time(self.start_time)

    async def insert_creation_oldid(self, row, delay):
        await asyncio.sleep(delay)
        self.process_data(row,
                          config.CORPUS_ARTICLES_HEADER[5],
                          data=Extract(self.project, row["qid"]).creation_oldid())
        self.utils.report_time(self.start_time)

    async def insert_creation_url(self, row, delay):
        await asyncio.sleep(delay)
        self.process_data(row,
                          config.CORPUS_ARTICLES_HEADER[6],
                          data=Extract(self.project, row["qid"]).creation_url())
        self.utils.report_time(self.start_time)

    async def insert_revision_date(self, row, delay):
        await asyncio.sleep(delay)
        self.process_data(row,
                          config.CORPUS_ARTICLES_HEADER[7],
                          data=Extract(self.project, row["qid"]).latest_revision_date())
        self.utils.report_time(self.start_time)

    async def insert_revision_oldid(self, row, delay):
        await asyncio.sleep(delay)
        self.process_data(row,
                          config.CORPUS_ARTICLES_HEADER[8],
                          data=Extract(self.project, row["qid"]).latest_revision_oldid())
        self.utils.report_time(self.start_time)

    async def insert_revision_url(self, row, delay):
        await asyncio.sleep(delay)
        self.process_data(row,
                          config.CORPUS_ARTICLES_HEADER[9],
                          data=Extract(self.project, row["qid"]).latest_revision_url())
        self.utils.report_time(self.start_time)

    async def insert_anonymous(self, row, delay):
        await asyncio.sleep(delay)
        self.process_data(row,
                          config.CORPUS_ARTICLES_HEADER[10],
                          data=Extract(self.project, row["qid"]).editors()["anonymous"])
        self.utils.report_time(self.start_time)

    async def insert_registered(self, row, delay):
        await asyncio.sleep(delay)
        self.process_data(row,
                          config.CORPUS_ARTICLES_HEADER[11],
                          data=Extract(self.project, row["qid"]).editors()["registered"])
        self.utils.report_time(self.start_time)

    async def insert_top_editor(self, row, delay):
        await asyncio.sleep(delay)
        self.process_data(row,
                          config.CORPUS_ARTICLES_HEADER[12],
                          data=Extract(self.project, row["qid"]).editors()["top_editor"][0][0])
        self.utils.report_time(self.start_time)

    async def insert_talk_page(self, row, delay):
        await asyncio.sleep(delay)
        self.process_data(row,
                          config.CORPUS_ARTICLES_HEADER[13],
                          data=Extract(self.project, row["qid"]).talk_page())
        self.utils.report_time(self.start_time)

    async def insert_talk_page_bytes(self, row, delay):
        await asyncio.sleep(delay)
        self.process_data(row,
                          config.CORPUS_ARTICLES_HEADER[14],
                          data=Extract(self.project, row["qid"]).talk_page_bytes())
        self.utils.report_time(self.start_time)

    async def insert_talk_page_words(self, row, delay):
        await asyncio.sleep(delay)
        self.process_data(row,
                          config.CORPUS_ARTICLES_HEADER[15],
                          data=Extract(self.project, row["qid"]).talk_page_words())
        self.utils.report_time(self.start_time)

    # TODO: aún falta por crear los métodos para el corpus específico
    async def insert_links_to(self, row, delay):
        await asyncio.sleep(delay)
        self.process_data(row,
                          config.CORPUS_ARTICLES_HEADER[16],
                          data=Extract(self.project, row["qid"]).links_to())
        self.utils.report_time(self.start_time)

    # TODO: aún falta por crear los métodos para el corpus específico
    async def insert_links_from(self, row, delay):
        await asyncio.sleep(delay)
        self.process_data(row,
                          config.CORPUS_ARTICLES_HEADER[17],
                          data=Extract(self.project, row["qid"]).links_from())
        self.utils.report_time(self.start_time)

    async def insert_images_used(self, row, delay):
        await asyncio.sleep(delay)
        self.process_data(row,
                          config.CORPUS_ARTICLES_HEADER[18],
                          data=Extract(self.project, row["qid"]).images_used())
        self.utils.report_time(self.start_time)

    # TODO: aún falta por crear los métodos para el corpus específico
    async def insert_references(self, row, delay):
        await asyncio.sleep(delay)
        self.process_data(row,
                          config.CORPUS_ARTICLES_HEADER[19],
                          data=Extract(self.project, row["qid"]).references())
        self.utils.report_time(self.start_time)

    # TODO: aún falta por crear los métodos para el corpus específico
    async def insert_bibliography(self, row, delay):
        await asyncio.sleep(delay)
        self.process_data(row,
                          config.CORPUS_ARTICLES_HEADER[20],
                          data=Extract(self.project, row["qid"]).bibliography())
        self.utils.report_time(self.start_time)

    async def insert_wikidata_id(self, row, delay):
        try:
            await asyncio.sleep(delay)
            self.process_data(row,
                              config.CORPUS_ARTICLES_HEADER[21],
                              data=Extract(self.project, row["qid"]).wikidata_id())
            self.utils.report_time(self.start_time)
        except pwb.exceptions.NoPage:
            msg.warn(row)
            msg.warn("Sin elemento de Wikidata")
            self.utils.report_time(self.start_time)

    async def insert_wikidata_labels(self, row, delay):
        try:
            await asyncio.sleep(delay)
            self.process_data(row,
                              config.CORPUS_ARTICLES_HEADER[22],
                              data=Extract(self.project, row["qid"]).wikidata_labels())
            self.utils.report_time(self.start_time)
        except pwb.exceptions.NoPage:
            msg.warn("Sin elemento de Wikidata")
            self.utils.report_time(self.start_time)

    async def insert_wikidata_descriptions(self, row, delay):
        try:
            await asyncio.sleep(delay)
            self.process_data(row,
                              config.CORPUS_ARTICLES_HEADER[23],
                              data=Extract(self.project, row["qid"]).wikidata_descriptions())
            self.utils.report_time(self.start_time)
        except pwb.exceptions.NoPage:
            msg.warn("Sin elemento de Wikidata")
            self.utils.report_time(self.start_time)

    async def insert_wikidata_claims(self, row, delay):
        try:
            await asyncio.sleep(delay)
            self.process_data(row,
                              config.CORPUS_ARTICLES_HEADER[24],
                              data=Extract(self.project, row["qid"]).wikidata_claims())
            self.utils.report_time(self.start_time)
        except pwb.exceptions.NoPage:
            msg.warn("Sin elemento de Wikidata")
            self.utils.report_time(self.start_time)

    async def insert_wikidata_references(self, row, delay):
        try:
            await asyncio.sleep(delay)
            self.process_data(row,
                              config.CORPUS_ARTICLES_HEADER[26],
                              data=Extract(self.project, row["qid"]).wikidata_references()[0])
            self.utils.report_time(self.start_time)
        except pwb.exceptions.NoPage:
            msg.warn("Sin elemento de Wikidata")
            self.utils.report_time(self.start_time)

    async def insert_wikidata_references_p143(self, row, delay):
        try:
            await asyncio.sleep(delay)
            self.process_data(row,
                              config.CORPUS_ARTICLES_HEADER[25],
                              data=Extract(self.project, row["qid"]).wikidata_references()[1])
            self.utils.report_time(self.start_time)
        except pwb.exceptions.NoPage:
            msg.warn("Sin elemento de Wikidata")
            self.utils.report_time(self.start_time)

    async def insert_wikidata_identifiers(self, row, delay):
        try:
            await asyncio.sleep(delay)
            self.process_data(row,
                              config.CORPUS_ARTICLES_HEADER[27],
                              data=Extract(self.project, row["qid"]).wikidata_identifiers())
            self.utils.report_time(self.start_time)
        except pwb.exceptions.NoPage:
            msg.warn("Sin elemento de Wikidata")
            self.utils.report_time(self.start_time)

    # TODO: aún falta por crear los métodos para el corpus específico
    async def insert_wikidata_interwiki(self, row, delay):
        try:
            await asyncio.sleep(delay)
            self.process_data(row,
                              config.CORPUS_ARTICLES_HEADER[28],
                              data=Extract(self.project, row["qid"]).wikidata_interwiki())
            self.utils.report_time(self.start_time)
        except pwb.exceptions.NoPage:
            msg.warn("Sin elemento de Wikidata")
            self.utils.report_time(self.start_time)

    async def insert_commons_category(self, row, delay):
        try:
            await asyncio.sleep(delay)
            self.process_data(row,
                              config.CORPUS_ARTICLES_HEADER[29],
                              data=Extract(self.project, row["qid"]).wikidata_commons_category())
            self.utils.report_time(self.start_time)
        except pwb.exceptions.NoPage:
            msg.warn("Sin elemento de Wikidata")
            self.utils.report_time(self.start_time)

    async def insert_commons_files(self, row, delay):
        try:
            await asyncio.sleep(delay)
            self.process_data(row,
                              config.CORPUS_ARTICLES_HEADER[30],
                              data=Extract(self.project, row["qid"]).commons_files())
            self.utils.report_time(self.start_time)
        except pwb.exceptions.NoPage:
            msg.warn("Sin elemento de Wikidata")
            self.utils.report_time(self.start_time)

    # TODO: aún falta por crear los métodos para el corpus específico
    async def insert_commons_categories(self, row, delay):
        try:
            await asyncio.sleep(delay)
            self.process_data(row,
                              config.CORPUS_ARTICLES_HEADER[31],
                              data=Extract(self.project, row["qid"]).commons_categories())
            self.utils.report_time(self.start_time)
        except pwb.exceptions.NoPage:
            msg.warn("Sin elemento de Wikidata")
            self.utils.report_time(self.start_time)

    def task(self, action, row, delay):
        return asyncio.create_task(action(row, delay))

    async def main(self):
        self.corpus_content = self.corpus.read_data(config.ARTICLES_FILE_DEFINITIVE)

        for index, row in self.corpus_content.iterrows():
            tasks = [
                self.task(self.insert_id, row, 0.01),
                self.task(self.insert_article_name, row, 0.01),
                self.task(self.insert_bytes, row, random.uniform(1, 5)),
                self.task(self.insert_words, row, random.uniform(1, 5)),
                self.task(self.insert_creation_date, row, random.uniform(1, 5)),
                self.task(self.insert_creation_oldid, row, random.uniform(1, 5)),
                self.task(self.insert_creation_url, row, random.uniform(1, 5)),
                self.task(self.insert_revision_date, row, random.uniform(1, 5)),
                self.task(self.insert_revision_oldid, row, random.uniform(1, 5)),
                self.task(self.insert_revision_url, row, random.uniform(1, 5)),
                self.task(self.insert_anonymous, row, random.uniform(1, 5)),
                self.task(self.insert_registered, row, random.uniform(1, 5)),
                self.task(self.insert_top_editor, row, random.uniform(1, 5)),
                self.task(self.insert_talk_page, row, random.uniform(1, 5)),
                self.task(self.insert_talk_page_bytes, row, random.uniform(1, 5)),
                self.task(self.insert_talk_page_words, row, random.uniform(1, 5)),
                self.task(self.insert_links_to, row, random.uniform(1, 5)),
                self.task(self.insert_links_from, row, random.uniform(1, 5)),
                self.task(self.insert_images_used, row, random.uniform(1, 5)),
                self.task(self.insert_references, row, random.uniform(1, 5)),
                self.task(self.insert_bibliography, row, random.uniform(1, 5)),
                self.task(self.insert_wikidata_id, row, random.uniform(1, 5)),
                self.task(self.insert_wikidata_labels, row, random.uniform(1, 5)),
                self.task(self.insert_wikidata_descriptions, row, random.uniform(1, 5)),
                self.task(self.insert_wikidata_claims, row, random.uniform(1, 5)),
                self.task(self.insert_wikidata_references, row, random.uniform(1, 5)),
                self.task(self.insert_wikidata_references_p143, row, random.uniform(1, 5)),
                self.task(self.insert_wikidata_identifiers, row, random.uniform(1, 5)),
                self.task(self.insert_wikidata_interwiki, row, random.uniform(1, 5)),
                self.task(self.insert_commons_category, row, random.uniform(1, 5)),
                self.task(self.insert_commons_files, row, random.uniform(1, 5)),
                self.task(self.insert_commons_categories, row, random.uniform(1, 5))
            ]

            for task in tasks:
                await task

        # TODO: corpus específicos

    def run(self):
        msg.info("Extracción de datos de los artículos del corpus.")
        self.start_time = time.perf_counter()

        with msg.loading("Analizando..."):
            asyncio.run(self.main())


if __name__ == "__main__":
    app = DataApp()
    app.run()
