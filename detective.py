import os
from datetime import datetime
from abc import ABC, abstractmethod
import argparse



"""Tipos de filstros para las busquedas"""
class FilterType:
    FILTER_NAME_CONTAINS = 2
    FILTER_WORD_INCLUDE = 4
    FILTER_DATE_CREATION = 6

"""Tipos de busque que puedes utilizar"""
class SearchTypes:
    FILE_SEARCH = 12


"""Buscar archivos por filtros"""
class FileBrowser:

    def searchWithFilter(self, **kwargs):
        """Buscar archivos con filtros correspondientes
           Parámetros: 
                filters:    list de FilterType
                pathBase:   Ruta de inicio de búsqueda
                pattern:    Patrón de búsqueda
                size:       (max, min) máximo y mínimo en bytes
                date:       Rango o fecha del archivo buscado(yyyy-mm-dd)
        """
        filters = kwargs.get("filters")
        pathBase = kwargs.get("base")
        pattern = kwargs.get("pattern")
        size = kwargs.get("size", {})
        dateSearchedStr = kwargs.get("date")
        startmiliseconds = datetime.now()

        print("`"*80)
        print("Search", "Pattern:", "'" + pattern + "'")

        for path, _, filenames in os.walk(pathBase):
            for name in filenames:
                filepath = path + "/" + name

                if len(size) != 0:
                   validsize = self.searchWithSize(size, filepath)
                   if not validsize:
                       break

                if FilterType.FILTER_NAME_CONTAINS in filters:
                    self.searchWithName(pattern, name, filepath)

                if FilterType.FILTER_WORD_INCLUDE in filters:
                    self.searchWithWordInclude(pattern, filepath)

                if FilterType.FILTER_DATE_CREATION in filters:
                    self.searchWithDateCreation(filepath, dateSearchedStr)

        endmiliseconds = datetime.now()
        time = endmiliseconds - startmiliseconds

        print("Time:", time, "\n")
        print("`"*80)

    def searchWithSize(self, size, filepath):
        maxbytes = size.get("max")
        minbytes = size.get("min")
        filesize = self.getFileSize(filepath)

        if maxbytes != 0:
            if not filesize <= maxbytes:
                return False

        if minbytes != 0:
            if not filesize >= minbytes:
                return False

    
    def searchWithName(self, pattern, filename, filepath):
        if filename.find(pattern) != -1:
            print(filepath)

    def searchWithWordInclude(self, pattern, filepath):
        try:
            f = open(filepath, "r")
        except Exception as e:
            print(e)
        else:
            lines = f.readlines()
            for n, line in enumerate(lines):
                if line.find(pattern) != -1:
                    print("Path",filepath)
                    print("Line:", n)
                    print("Content:", line)

    def searchWithDateCreation(self, filepath, dateSearchedStr):
        datecreation = self.getDateCreationFile(filepath)
        datesSearchedList = dateSearchedStr.split("/")

        if len(datesSearchedList) > 1:
            datestart = datetime.strptime(datesSearchedList[0], "%Y-%m-%d")
            dateend = datetime.strptime(datesSearchedList[1], "%Y-%m-%d")

            if datecreation.date() >= datestart.date() and datecreation.date() <= dateend.date():
                print("\nDate creation", datecreation.today())
                print("Path:", filepath)
            else:
                dateSearched = datetime.strptime(datesSearchedList[0], "%Y-%m-%d")
                if datecreation.date() == dateSearched.date():
                    print("\nDate creation", datecreation.date())
                    print("Path:", filepath)

    def getFileSize(self, filepath):
        """Obtener el size en bytes"""
        statinfo = os.stat(filepath)
        return statinfo.st_size
    
    def getDateCreationFile(self, filepath):
        """Obtener la fecha de creacion del archivo"""
        statinfo = os.stat(filepath)
        datecreation = datetime.fromtimestamp(statinfo.st_ctime)
        return datecreation


"""Herramientas que utilizará el detective"""
class Tools:
    filebrowser = FileBrowser()


"""Clase base para los tipos de detectives"""
class Detective(ABC):
    @abstractmethod 
    def search(self, **kwargs):
        """Método que permite realizar busquedas con respecto al detective"""
        raise NotImplementedError()


"""Detective que permita buscar archivos con filtros"""
class DetectiveFile(Detective):

    def __init__(self):
        self.tools = Tools()

    def search(self, **kwargs):
        """Buscar archivos con filtros"""
        typeSearch = kwargs.get("type")

        if typeSearch == SearchTypes.FILE_SEARCH:
            self.tools.filebrowser.searchWithFilter(**kwargs)

if __name__ == "__main__":
    messagefilters = "Search filter: 1. Name, 2. Word included"
    parse = argparse.ArgumentParser(description="-- Detective, perform file searches. --")
    parse.add_argument("path", metavar="path", type=str, nargs=1, help="Base path for search")
    parse.add_argument("pattern", metavar="pattern", type=str, nargs=1, help="Pattern to be searched")
    parse.add_argument("-f", metavar="filter", type=int, nargs="+", help=messagefilters, default=[1])
    parse.add_argument("-t", metavar="type", type=str, nargs=1, help="Search type: file", default="file")
    parse.add_argument("--daterange", metavar="daterange", type=str, help="Search by date range", default=None)
    parse.add_argument("-s", metavar="size", type=int, nargs="+", help="Size in bytes of the searched files", default=[])

    args = parse.parse_args()

    # Agregando filtros y variables
    filters = []
    typesearch = args.t
    daterange = ""

    for number in args.f:
        if number == 1:
            filters.append(FilterType.FILTER_NAME_CONTAINS)
        if number == 2:
            filters.append(FilterType.FILTER_WORD_INCLUDE)
    
    if args.daterange:
        filters.append(FilterType.FILTER_DATE_CREATION)

    if typesearch == "file":
        typesearch = SearchTypes.FILE_SEARCH
    
    detective = DetectiveFile()
    detective.search(filters=filters,
                     base=args.path[0],
                     pattern=args.pattern[0],
                     size=args.s,
                     date=daterange,
                     type=typesearch)