import argparse
import sys
from googleapiclient import sample_tools
import shutil
import glob
import os
import re
import time
import collections
#import MySQLdb
import warnings
import csv

# Declare command-line flags.
argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('property_id', type=str,
                       help=('Site dwh id).'))
argparser.add_argument('property_uri', type=str,
                       help=('Site or app URI to query data for (including '
                             'trailing slash).'))
argparser.add_argument('start_date', type=str,
                       help=('Start date of the requested date range in '
                             'YYYY-MM-DD format.'))
argparser.add_argument('end_date', type=str,
                       help=('End date of the requested date range in '
                             'YYYY-MM-DD format.'))

rowcounter = 0
maxrows = 25000

def main(argv, rowcounter):
    service, flags = sample_tools.init(
        argv, 'webmasters', 'v3', __doc__, __file__, parents=[argparser],
        scope='https://www.googleapis.com/auth/webmasters.readonly')

    while True:
        # Get the queries for the date range, sorted by click count, descending.
        request = {
            'startDate': flags.start_date,
            'endDate': flags.end_date,
            'dimensions': ['date', 'page', 'country', 'device'],
            'rowLimit': maxrows,
            'startRow': rowcounter*maxrows
        }
        filename_1 = "C:/Talend/JobFiles/GSC/Export/Page_Search_Analytics/" + sys.argv[1] + "_gsc_page_search_analytics_file_"+ str(rowcounter) + "_" + sys.argv[3] + ".csv"
        filename = filename_1
        response = execute_request(service, flags.property_uri, request)
        print_table(filename, flags.property_id, flags.property_uri, flags.start_date, response,'Export to CSV complete')
        rowcounter = rowcounter+1
        if 'rows' not in response:
            break


def execute_request(service, property_uri, request):
    '''Executes a searchAnalytics.query request.

    Args:
        service: The webmasters service to use when executing the query.
        property_uri: The site or app URI to request data for.
        request: The request to be executed.

    Returns:
        An array of response rows.
    '''
    return service.searchanalytics().query(
        siteUrl=property_uri, body=request).execute()


def print_table(filename, property_id, property_uri, start_date, response, title):
    '''Prints out a response table.

    Each row contains key(s), clicks, impressions, CTR, and average position.

    Args:
        response: The server response to be printed as a table.
        title: The title of the table.
    '''
    # print title + ':'

    if 'rows' not in response:
        print('Empty response')
        return

    rows = response['rows']
    # row_format = '{:<20}' + '{:>20}' * 4
    # print row_format.format('Keys', 'Clicks', 'Impressions', 'CTR', 'Position')
    f = open(filename, 'wt', newline='')
    writer = csv.writer(f)
    writer.writerow(('property_id', 'property_uri', 'dimensions', 'impressions', 'clicks', 'ctr', 'position'))
    for row in rows:
        keys = ''
        # Keys are returned only if one or more dimensions are requested.
        if 'keys' in row:
            keys = u'|'.join(row['keys']).encode('utf-8').rstrip()
        # print row_format.format(
        # keys, row['clicks'], row['impressions'], row['ctr'], row['position'])
        writer.writerow((property_id, property_uri, keys, row['impressions'], row['clicks'], row['ctr'], row['position']))
    f.close()

if __name__ == '__main__':
  main(sys.argv, rowcounter)