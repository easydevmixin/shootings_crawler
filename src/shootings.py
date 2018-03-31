#!/usr/bin/env python

# -*- coding: utf-8 -*-

import argparse
import csv
import datetime
import os
import hashlib
import time

import license
import logger

sl = logger.get_logger()


class ShootingsCrawler:
    BASE_URL = 'http://www.gunviolencearchive.org'
    REPORTS_PRE_2016 = 'reports/mass-shootings/<year>'
    REPORTS = 'reports/mass-shooting?year=<year>'
    PAGE_ARG_PRE_2016 = '?page=<num_page>'
    PAGE_ARG = '&page=<num_page>'

    def __init__(self, args):
        sl.info('arguments: {}'.format(args))
        current_year = datetime.datetime.now().year
        if not args.year:
            self.year = current_year
        else:
            year = args.year
            if year >= 2013 and year <= current_year:
                self.year = year
            else:
                sl.info("Year not in range [{}]. Will fetch data for the current year [{}].".format(
                    year,
                    current_year
                ))
                self.year = current_year

        sl.info(self.year)
        pass

    def __get_num_pages(self):
        sl.info("getting num of pages")
        pass

    def __fetch_data(self):
        sl.info("fetching data")
        pass

    def run(self):
        sl.info('running')
        self.__get_num_pages()
        self.__fetch_data()
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("-w", "--warranty", help="Check out the warranty summary.", action="store_true")
    parser.add_argument("-c", "--conditions", help="Check out the conditions summary.",
                        action="store_true")
    parser.add_argument("-y", "--year", help="Year of the shootings. Must be on or over 2013.", type=int)

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
            sl.error("Error checking robots.txt file: {}".format(ex))
