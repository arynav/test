import requests
import json
import csv
from operator import itemgetter
from dateutil import parser


def book(search_string, filter=None):
    """
    Create book library based on input search string
    :param search_string: 
    :param filter: 
    :return: 
    """
    if (filter):
        filter = 'filter=%s' % filter
    else:
        filter = ""

    library = []
    try:
        #for i in range(5):
        for i in range(4):
            response = requests.get(
                #"https://www.googleapis.com/books/v1/volumes?q=%s&maxResults=40&startIndex=%s&%s" % (
                    #search_string, i * 40, filter)).json()
                "https://www.googleapis.com/books/v1/volumes?q=%s&maxResults=25&startIndex=%s&%s" % (
                    search_string, i * 25, filter)).json()

            library += response['items']
    except KeyError:
        return None

    saveToCSV(library,"BaseLibrary")
    return (library)


def saveToCSV(library, filename):
    """
    Save book library to a specified file
    :param library: 
    :param filename: 
    :return: 
    """
    keys = ['kind','volumeInfo','searchInfo','saleInfo','etag','accessInfo','id','selfLink']
    with open(filename + '.csv', 'wb') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(library)


def openCSV(pathToFile):
    """
    Open csv file from specified location
    :param pathToFile: 
    :return: 
    """
    with open(pathToFile) as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)


def groupByPublisher(filterName, bookList):
    """
    Group books by publisher and save filtered results to a csv file
    :param filterName: 
    :param bookList: 
    :return: 
    """
    filtered_list = []
    for book in bookList:
        entry=book['volumeInfo'].get('publisher')
        if (entry) and entry.lower() == filterName.lower():
            filtered_list.append(book)
    print filtered_list
    saveToCSV(filtered_list, "groupByPublisher-%s"%filterName.replace(" ", ""))

def groupByFormat(filterName, bookList):
    """
    Group books by format and save filtered results to a csv file
    :param filterName: 
    :param bookList: 
    :return: 
    """
    filtered_list = []
    for book in bookList:
        entry=book['accessInfo'].get(filterName).get('isAvailable')
        if (entry) :
            filtered_list.append(book)
    print filtered_list
    saveToCSV(filtered_list, "groupByFormat-%s"%filterName.replace(" ", ""))


def sort(sortByName, bookList):
    """
    Sort books by price, avg rating, page count, rating count, published date and save filtered results to a csv file
    :param sortByName: 
    :param bookList: 
    :return: 
    """
    if(sortByName == "price"):
        saleInfoList = []
        for entry in bookList:
            if entry.get('saleInfo'):
                if entry['saleInfo'].get('listPrice'):
                    saleInfoList.append(entry)
        sortedList = sorted(saleInfoList, key=lambda k: k['saleInfo']['listPrice'], reverse=False)

        print sortedList
        saveToCSV(sortedList, "sortBy-%s"%sortByName.replace(" ", ""))
    if (sortByName == "rating"):
        averageRatingList = []
        for entry in bookList:
            if entry.get('volumeInfo'):
                if entry['volumeInfo'].get('averageRating'):
                    averageRatingList.append(entry)
        averageRatingList = sorted(averageRatingList, key=lambda k: k['volumeInfo']['averageRating'], reverse=False)
        print averageRatingList
        saveToCSV(averageRatingList, "sortBy-%s"%sortByName.replace(" ", ""))

    if (sortByName == "page count"):
        pageCountList = []
        for entry in bookList:
            if entry.get('volumeInfo'):
                if entry['volumeInfo'].get('pageCount'):
                    pageCountList.append(entry)
        pageCountList = sorted(pageCountList, key=lambda k: k['volumeInfo']['pageCount'], reverse=False)
        print pageCountList
        saveToCSV(pageCountList, "sortBy-%s"%sortByName.replace(" ", ""))

    if (sortByName == "rating count"):
        ratingsCountList = []
        for entry in bookList:
            if entry.get('volumeInfo'):
                if entry['volumeInfo'].get('ratingsCount'):
                    ratingsCountList.append(entry)
        ratingsCountList = sorted(ratingsCountList, key=lambda k: k['volumeInfo']['ratingsCount'], reverse=False)
        print ratingsCountList
        saveToCSV(ratingsCountList, "sortBy-%s"%sortByName.replace(" ", ""))

    if (sortByName == "published date"):
        publishedDateList = []

        for entry in bookList:
            if entry.get('volumeInfo'):
                if entry['volumeInfo'].get('publishedDate'):
                    entry['volumeInfo']['publishedDate'] = parser.parse(entry['volumeInfo']['publishedDate'])
                    publishedDateList.append(entry)
        publishedDateList = sorted(publishedDateList, key=lambda k: k['volumeInfo']['publishedDate'], reverse=False)
        for i in publishedDateList:
            i['volumeInfo']['publishedDate']=str(i['volumeInfo']['publishedDate'])
        print publishedDateList
        saveToCSV(publishedDateList, "sortBy-%s" % sortByName.replace(" ", ""))

if __name__ == '__main__':

    # Command-line user interface queries google book api's based on the user search input.
    # Saves input into csv book library files.
    # Allows to group by or sort book libraries based on provided viewing options
    while (True):
        input = raw_input('Enter your book search string: \n')
        bookBase = book(input)
        #Check returned results > 100
        if (not bookBase ):
            print('Your string resulted in less then 100 results. Please enter another search string \n')
            continue

        input2 = raw_input('Select your viewing options: \n'
                           '\t1. Group by Publisher: enter 1 \n'
                           '\t2. Group by Format type: enter 2 \n'
                           '\t3. Sort: enter 3 \n')
        if (input2 == "1"):
            publisher = raw_input('Enter Publisher name: ')
            groupByPublisher(publisher, bookBase)

        if (input2 == "2"):
            formatType = raw_input('Enter your Format type, e.g: epub, pdf ' )
            groupByFormat(formatType,bookBase)
        if (input2 == "3"):
            sortType = raw_input('Enter your sort options, e.g: \n'
                                 'price, rating, rating count, page count, published date:  ')
            sort(sortType, bookBase)
