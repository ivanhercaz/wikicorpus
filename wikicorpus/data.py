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
import pandas


class Data:
    def __init__(self, columns, data=[]):
        self.columns = columns
        self.data = data
        self.frame = pandas.DataFrame(self.data, columns=self.columns)

    def insert(self, data):
        data = pandas.DataFrame(data, columns=self.columns)
        self.frame = self.frame.append(data)

    def insert_at(self, data, row, cell):
        self.frame.at[row, [cell]] = [data]

    def is_duplicated(self, column, value):
        return self.frame[column].isin([value]).any()

    def export(self, csv_file):
        data_csv = self.frame.to_csv(index=False)
        with open(csv_file, "w") as csv:
            csv = csv.write(data_csv)

    def reuse_data(self, csv_file):
        self.csv_readed = pandas.read_csv(csv_file)
        self.frame = self.frame.append(self.csv_readed)

    def read_data(self, csv_file):
        return pandas.read_csv(csv_file)
