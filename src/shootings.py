#!/usr/bin/env python

# -*- coding: utf-8 -*-

import argparse
import csv
import datetime
import logging
import time

from urllib.parse import urljoin, urlparse, parse_qs

import requests

from bs4 import BeautifulSoup
from dateutil.parser import parse

from incident import Incident
import license
import logger


BASE_URL = 'http://www.gunviolencearchive.org'
REPORTS_PRE_2016 = 'reports/mass-shootings/<year>'
REPORTS = 'reports/mass-shooting?year=<year>'
PAGE_ARG_PRE_2016 = '?page=<num_page>'
PAGE_ARG = '&page=<num_page>'

VERSION = '0.0.1'
USER_AGENT = 'shootings/{}'.format(VERSION)


class ShootingsCrawler:
    def __init__(self, args):
        level = logging.INFO
        if args.debug:
            level = logging.DEBUG

        self._logger = logger.get_logger(level=level, maxbytes=1024 * 1024)
        self._logger.info('==========================================')
        self._logger.debug('arguments: {}'.format(args))

        current_year = datetime.datetime.now().year
        if not args.year:
            self.year = current_year
        else:
            year = args.year
            if year >= 2013 and year <= current_year:
                self.year = year
            else:
                raise Exception("Year [{}] must be between 2013 and {}.".format(args.year, current_year))

        if not args.tbr or args.tbr < 0:
            self._tbr = 10
        else:
            self._tbr = args.tbr

        if not args.tries or args.tries < 0:
            self._tries = 3
        else:
            self._tries = args.tries

        self._last_request = 0
        self.__create_base_url()

    def __create_base_url(self):
        if self.year < 2016:
            base_url = urljoin(BASE_URL, REPORTS_PRE_2016) + PAGE_ARG_PRE_2016
        else:
            base_url = urljoin(BASE_URL, REPORTS) + PAGE_ARG

        self._base_url = base_url.replace('<year>', str(self.year))
        self._logger.debug("Base URL: {}".format(self._base_url))

    def get_logger(self):
        return self._logger

    def __get_num_pages(self, data):
        self._logger.debug("getting num of pages")
        a = data.find('li', attrs={'class': 'pager-last'}).find('a')
        url = urljoin(BASE_URL, a['href'])
        p = urlparse(url)
        q = parse_qs(p.query)
        pages = int(int(q['page'][0]))
        self._logger.debug("# of pages to fetch: %d" % pages)
        return pages

    def __make_request(self, url):
        """
        Make a request with the given user-agent.

        Takes care to honor time between requests.
        """
        while True:
            t = int(time.time())
            if t - self._last_request >= self._tbr:
                self._last_request = t
                break
            time.sleep(1)

        headers = {'user-agent': USER_AGENT}
        r = requests.get(url=url, headers=headers)
        return r

    def __fetch_page(self, page=0, tries=3):
        url = self._base_url.replace('<num_page>', str(page))
        self._logger.debug('fetching page {}'.format(url))

        if tries < 0:
            raise Exception("Could not fetch the URL: {}".format(url))

        r = self.__make_request(url)
        if not r.ok:
            print("Could not fetch url {}. Response code: {}. Retrying in {} seconds.".format(
                url,
                r.status_code,
                self._tbr
            ))
            self._logger.warning("Could not fetch url {}. Response code: {}. Retrying in {} seconds.".format(
                url,
                r.status_code,
                self._tbr
            ))
            self.__fetch_page(page=page, tries=tries - 1)

        return BeautifulSoup(r.text, 'html.parser')

    def __extract_data(self, data):
        self._logger.debug("extracting data")
        rows = data.find_all('tbody')[0].find_all('tr')

        for row in rows:
            incident = Incident()
            columns = row.find_all('td')
            date = parse(columns[0].text)
            incident.year = date.year
            incident.month = date.month
            incident.day = date.day
            incident.state = columns[1].text
            incident.city_or_county = columns[2].text
            incident.address = columns[3].text
            incident.num_killed = columns[4].text
            incident.num_injured = columns[5].text
            incident_link = columns[6].find('ul').find('li').find('a')['href']  # link to incident
            incident.incident_link = urljoin(BASE_URL, incident_link)
            # TODO: Create CSV file
            print('{}, {}, {}, "{}", "{}", "{}", {}, {}, "{}"'.format(
                incident.year,
                incident.month,
                incident.day,
                incident.state,
                incident.city_or_county,
                incident.address,
                incident.num_killed,
                incident.num_injured,
                incident.incident_link,
            ))

    def run(self):
        self._logger.debug('running')
        data = self.__fetch_page(page=0)
        pages = self.__get_num_pages(data)
        self.__extract_data(data)
        for i in range(1, pages + 1):
            data = self.__fetch_page(page=i)
            self.__extract_data(data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("-w", "--warranty", help="Check out the warranty summary.", action="store_true")
    parser.add_argument("-c", "--conditions", help="Check out the conditions summary.",
                        action="store_true")
    parser.add_argument("-y", "--year", help="Year of the shootings. Must be on or over 2013.", type=int)
    parser.add_argument("-t", "--tbr", help="Time elapsed between requests in seconds (default 10).", type=int)
    parser.add_argument("-T", "--tries", help="Number of times trying to fetch the page (default 3).", type=int)
    parser.add_argument("-D", "--debug", help="Sets logger to log debug events.", action="store_true")

    args = parser.parse_args()

    if args.warranty:
        license.show_warranty()
    elif args.conditions:
        license.show_contitions()
    else:
        try:
            r = ShootingsCrawler(args=args)
            r.run()
        except Exception as ex:
            print("Error: {}".format(ex))
            logger.get_logger(maxbytes=1024 * 1024).error("Error: {}".format(ex))
