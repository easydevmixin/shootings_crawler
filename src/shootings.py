#!/usr/bin/env python

# -*- coding: utf-8 -*-

import argparse
import csv
import datetime
import logging
import os
import hashlib
import time

import requests

from bs4 import BeautifulSoup

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
        self._logger.debug('arguments: {}'.format(args))

        current_year = datetime.datetime.now().year
        if not args.year:
            self.year = current_year
        else:
            year = args.year
            if year >= 2013 and year <= current_year:
                self.year = year
            else:
                self._logger.info("Year not in range [{}]. Will fetch data for the current year [{}].".format(
                    year,
                    current_year
                ))
                self.year = current_year

        if not args.tbr:
            self._tbr = 10
        else:
            self._tbr = args.tbr

        self.__create_base_url()

    def __create_base_url(self):
        if self.year < 2016:
            base_url = os.path.join(BASE_URL, REPORTS_PRE_2016) + PAGE_ARG_PRE_2016
        else:
            base_url = os.path.join(BASE_URL, REPORTS) + PAGE_ARG

        self._base_url = base_url.replace('<year>', str(self.year))
        self._logger.debug("Base URL: {}".format(self._base_url))

    def get_logger(self):
        return self._logger

    def __get_num_pages(self):
        self._logger.debug("getting num of pages")
        pass

    def __make_request(self, url):
        headers = {'user-agent': USER_AGENT}
        r = requests.get(url=url, headers=headers)
        return r

    def __fetch_page(self, url, page=0, tries=0):
        self._logger.debug('fetching page {}'.format(url))
        url = url.replace('<num_page>', page)

        if tries < 0:
            raise Exception("Could not fetch the URL: {}".format(url))

        r = self.__make_request(url)
        if not r.ok:
            time.sleep(self._tbr)
            self.__fetch_page(url=url, page=page, tries=tries - 1)

        return BeautifulSoup(r.text, 'html.parser')

    def __extract_data(self, data):
        self._logger.debug("extracting data")
        pass

    def run(self):
        self._logger.debug('running')
        self.__get_num_pages()
        self.__extract_data(None)
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("-w", "--warranty", help="Check out the warranty summary.", action="store_true")
    parser.add_argument("-c", "--conditions", help="Check out the conditions summary.",
                        action="store_true")
    parser.add_argument("-y", "--year", help="Year of the shootings. Must be on or over 2013.", type=int)
    parser.add_argument("-t", "--tbr", help="Time elapsed between requests in seconds (default 10).", type=int)
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
            r.get_logger().error("Error: {}".format(ex))
