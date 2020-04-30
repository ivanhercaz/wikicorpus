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
import colorama as color
import inquirer
import json
import logging
import sys

# Pywikibot
import pywikibot as pwb

# Módulos propios
from config import Config as config
from wikicorpus.data import Data
from wikicorpus.utils import Utils


color.init(autoreset=True)


class App():
    def __init__(self, reuse_file_mode=False):
        self.project = pwb.Site("es", "wikipedia")
        self.reuse_file_mode = reuse_file_mode
        self.article_id = 0
        self.article_not_include_id = 0
        self.utils = Utils(config=config)

        with open(config.CATEGORIES_CONFIG_FILE_BACKUP, "r") as json_file:
            self.old_config = json.load(json_file)

        with open(config.CATEGORIES_CONFIG_FILE, "r") as json_file:
            self.categories_config = json.load(json_file)

        # Log config
        logging.basicConfig(format="%(asctime)s %(levelname)s:"
                            "\n>> %(message)s", level=logging.INFO)
        logging.info("Iniciando...")

    def check_article(self, data, data_not_included, category=""):
        status = None

        for category in self.categories_config["categories"]:
            cat = pwb.Category(self.project, category)

            for article in cat.articles():
                article_title = self.utils.clean_wikitext(article)
                article_category = self.utils.clean_wikitext(category)

                if data.is_duplicated("articulo", article_title):
                    logging.info(article_title +
                                 f": {color.Style.BRIGHT}{color.Fore.RED}"
                                 "duplicado" +
                                 article_category)
                    status = False

                elif data_not_included.is_duplicated("articulo", article_title):
                    logging.info(article_title +
                                 f": {color.Style.BRIGHT}{color.Fore.RED}"
                                 "duplicado (no)" +
                                 article_category)
                    status = False

                else:
                    status = True

                if status is not False:

                    logging.info(f"\n{color.Style.DIM}{article_title}"
                                 f"\n{color.Style.DIM}{article_category}")

                    if config.SELENIUM is True:
                        repeat = True
                        if data.frame.empty or data_not_included.frame.empty or repeat is False:
                            self.selenium.get(article.full_url())

                        else:
                            self.article_id = data.frame["id"].iat[-1]
                            self.article_not_include_id = data_not_included.frame["id"].iat[-1]
                            self.selenium.get("https://es.wikipedia.org/wiki/" +
                                              article_title.replace(" ", "_"))
                            repeat = False

                    question = [
                            inquirer.List("add",
                                          message="¿Añadir al estudio?",
                                          choices=["Sí", "No", "Excluir categoría", "Salir"])
                        ]

                    if status is True:
                        answers = inquirer.prompt(question)

                        if answers["add"] is "Sí":
                            self.article_id += 1
                            self.article_not_include_id += 0
                            values = [self.article_id,
                                      article_title,
                                      article_category]

                            data.insert([values])

                            logging.info(f"Log: #{self.article_id} <{article_title}>"
                                         f"({article_category}) {color.Style.BRIGHT}"
                                         f"{color.Fore.RED}añadido")

                        elif answers["add"] is "No":
                            self.article_id += 0
                            self.article_not_include_id += 1
                            values = [self.article_not_include_id,
                                      article_title,
                                      article_category]

                            data_not_included.insert([values])

                            logging.info(f"Log: <{article_title}> ({article_category})"
                                         f"{color.Style.BRIGHT}{color.Fore.RED} deshechado"
                                         f".")

                        elif answers["add"] is "Excluir categoría":
                            self.article_id += 0
                            self.article_not_include_id += 0

                            self.categories_config["excluded_categories"].append(
                                self.utils.clean_category(article_category)
                            )

                            logging.info(f"Log: <{article_category}>"
                                         f"{color.Style.BRIGHT}{color.Fore.RED} excluida.")

                        elif answers["add"] is "Salir":
                            data.export(self.articles_file)
                            data_not_included.export(self.articles_not_included_file)

                            self.selenium.quit()

                            with open(config.CATEGORIES_CONFIG_FILE, "w") as json_file:
                                if len(self.old_config["excluded_categories"]) \
                                   < len(self.categories_config["excluded_categories"]):
                                    logging.info(f"Log: guardando las nuevas categorías "
                                                 f"excluidas en "
                                                 f"{config.CATEGORIES_CONFIG_FILE}")

                                    json.dump(self.categories_config, json_file,
                                              indent="\t", ensure_ascii=False)

                                    logging.info(f"Log: categorías excluidas guardadas "
                                                 f"correctamente en "
                                                 f"{config.CATEGORIES_CONFIG_FILE}")

                            sys.exit(f"{color.Style.DIM}Saliendo del programa...")

                        return self.article_id

    def run(self, reuse_file_mode=False):
        if config.SELENIUM is True:
            self.selenium = self.utils.run_selenium()

        self.articles_file = self.utils.check_file(reuse_file_mode)
        self.articles_not_included_file = self.utils.check_file(reuse_file_mode,
                                                                suffix="no")

        data = Data(columns=["id", "articulo", "categoria"])
        data_not_included = Data(columns=["id", "articulo", "categoria"])

        if reuse_file_mode is True:
            data.reuse_data(self.articles_file)
            data_not_included.reuse_data(self.articles_not_included_file)

            self.check_article(data, data_not_included)

        with open(config.CATEGORIES_CONFIG_FILE, "w") as json_file:
            if len(self.old_config["excluded_categories"]) \
               < len(self.categories_config["excluded_categories"]):
                logging.info(f"Log: guardando las nuevas categorías "
                             f"excluidas en "
                             f"{config.CATEGORIES_CONFIG_FILE}")

                json.dump(self.categories_config, json_file,
                          indent="\t", ensure_ascii=False)

                logging.info(f"Log: categorías excluidas guardadas "
                             f"correctamente en "
                             f"{config.CATEGORIES_CONFIG_FILE}")

            else:
                logging.info(f"Log: \n"
                             f"{self.old_config}")
                json.dump(self.old_config, json_file,
                          indent="\t", ensure_ascii=False)
                logging.info(f"Log después: \n"
                             f"{self.old_config}")

        data.export(self.articles_file)
        data_not_included.export(self.articles_not_included_file)


if __name__ == "__main__":
    app = App()

    """
        El modo de reutilización de archivo no funciona. Aunque hay
         fragmentos de código que pertenecen a ese sistema, no debe de
         utilizarse hasta que esté completamente desarrollado porque no
         garantiza resultados.
    """

    question = [
        inquirer.Confirm("reuse",
                         message="¿Quieres reutilizar un archivo?",
                         default=False
                         ),
    ]

    answer = inquirer.prompt(question)

    if answer["reuse"] is True:
        app.run(reuse_file_mode=True)

    else:
        app.run()
