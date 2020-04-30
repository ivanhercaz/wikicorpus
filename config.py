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


class Config:
    APP_NAME = "WikiCorpus"
    APP_VERSION = "0.1.0"

    # APIs
    ESWIKI_API = "https://es.wikipedia.org/w/api.php?"
    WIKIDATA_API = "https://wikidata.org/w/api.php?"

    # TODO: redefinir la estructura de archivos
    # Artículos
    ARTICLES_FILE = "corpus/articulos_0" # Archivo para almacenar los artículos seleccionados
    ARTICLES_FILE_FORMAT = "csv"
    ARTICLES_FILE_DEFINITIVE = "corpus/articulos_definitivo.csv" # Archivo del que se seleccionan los archivos

    CATEGORIES_CONFIG_FILE = "categories.json"
    CATEGORIES_CONFIG_FILE_BACKUP = "categories_backup.json"

    # Selenium
    SELENIUM = True

    # Corpus
    CORPUS_ARTICLES_FILE = "corpus/corpus_wikidata_commons_eswiki.csv"
    CORPUS_ARTICLES_HEADER = ["id", "articulo", "tamano_bytes", "tamano_palabras",
                              "fecha_creacion", "id_creacion", "url_creacion",
                              "fecha_ultima_revision", "id_ultima_revision", "url_ultima_revision",
                              "editores_anonimos", "editores_registrados", "editor_principal",
                              "discusion", "discusion_tamanho_bytes", "discusion_tamanho_palabras",
                              "enlaces_a", "enlaces_de", "imagenes_cantidad",
                              "referencias", "bibliografía", "wikidata_id", "wikidata_etiquetas",
                              "wikidata_descripciones", "wikidata_declaraciones",
                              "wikidata_declaraciones_referencias_P143",
                              "wikidata_declaraciones_referencias",
                              "wikidata_identificadores_externos", "wikidata_interwiki",
                              "commons_categoria",
                              "commons_archivos", "commons_subcats"]
