#!/usr/bin/env python

# -*- coding: utf-8 -*-

import argparse
import csv
import datetime
import logging
import os
import re
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
    def __init__(self, args=None):
        level = logging.INFO
        if args is not None and args.debug:
            level = logging.DEBUG

        self._logger = logger.get_logger(level=level, maxbytes=1024 * 1024)
        self._logger.info('==========================================')
        self._logger.debug('arguments: {}'.format(args))

        current_year = datetime.datetime.now().year

        if args is not None:
            if args.year:
                year = args.year
                if year >= 2013 and year <= current_year:
                    self.year = year
                else:
                    raise Exception("Year [{}] must be between 2013 and {}.".format(args.year, current_year))
            else:
                self.year = current_year

            if args.tbr:
                self._tbr = args.tbr
            else:
                self._tbr = 10

            if args.tries:
                self._tries = args.tries
            else:
                self._tries = 3

            if args.output:
                if args.output.endswith('.csv'):
                    self._output = args.output
                else:
                    self._output = "{}.csv".format(args.output)
            else:
                self._output = 'output.csv'
        else:
            self.year = current_year
            self._tbr = 10
            self._tries = 3
            self._output = 'output.csv'

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

    def __make_soup(self, data, parser='html.parser'):
        return BeautifulSoup(data, parser)

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

        return self.__make_soup(r.text)

    def __get_lat_lon(self, data, incident):
        lat, lon = 0, 0
        geo = data.find('span', text=re.compile('Geolocation*'))
        if geo:
            geo = geo.text.split(':')[1].strip().replace(' ', '')
            lat, lon = geo.split(',')
        incident.lat = lat
        incident.lon = lon

    def __get_participants(self, data, incident):
        participants = data.find('h2', text=re.compile('Participants*'))
        list_of_participants = []
        uls = participants.parent.find_all('ul')
        for ul in uls:
            kvs = {}
            lis = ul.find_all('li')
            for li in lis:
                k, v = li.text.strip().split(':')
                kvs[k] = v.strip()
            list_of_participants.append(kvs)
        incident.participants = list_of_participants

    def __get_characteristics(self, data, incident):
        incident_characteristics = data.find('h2', text=re.compile('Incident Characteristics*'))
        list_of_characteristics = []
        ul = incident_characteristics.parent.find('ul')
        lis = ul.find_all('li')
        for li in lis:
            k = li.text.strip()
            list_of_characteristics.append(k)
        incident.characteristics = list_of_characteristics

    def __get_notes(self, data, incident):
        notes = data.find('h2', text=re.compile('Notes*'))
        detail = notes.parent.find('p').text.strip()
        incident.notes = detail

    def __get_guns_involved(self, data, incident):
        guns = data.find('h2', text=re.compile('Guns Involved*'))
        list_of_guns_involved = []
        uls = guns.parent.find_all('ul')
        for ul in uls:
            kvs = {}
            lis = ul.find_all('li')
            for li in lis:
                k, v = li.text.strip().split(':')
                kvs[k] = v.strip()
            list_of_guns_involved.append(kvs)
        incident.guns_involved = list_of_guns_involved

    def __fetch_additional_info(self, incident):
        r = self.__make_request(incident.incident_link)
        data = self.__make_soup(r.text)
        self.__get_lat_lon(data=data, incident=incident)
        self.__get_participants(data=data, incident=incident)
        self.__get_characteristics(data=data, incident=incident)
        self.__get_notes(data=data, incident=incident)
        self.__get_guns_involved(data=data, incident=incident)
    additional_info = __fetch_additional_info

    def __extract_data(self, data):
        self._logger.debug("extracting data")
        rows = data.find_all('tbody')[0].find_all('tr')

        incidents = []

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

            self.__fetch_additional_info(incident)

            incidents.append(incident)

        return incidents

    def run(self):
        self._logger.debug('running')
        filename = os.path.join('..', 'out', self._output)
        with open(filename, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['sha256', 'year', 'month', 'day', 'state', 'city_or_county', 'address', 'num_killed', 'num_injured', 'incident_link'])

            data = self.__fetch_page(page=0)
            pages = self.__get_num_pages(data)
            incidents = self.__extract_data(data)
            self._write_incidents(writer, incidents)
            for i in range(1, pages + 1):
                data = self.__fetch_page(page=i)
                incidents = self.__extract_data(data)
                self._write_incidents(writer, incidents)

    def _write_incidents(self, csvwriter, incidents):
        for incident in incidents:
            csvwriter.writerow(incident.to_csv())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--conditions", help="Check out the conditions summary.",
                        action="store_true")
    parser.add_argument("-D", "--debug", help="Sets logger to log debug events.", action="store_true")
    parser.add_argument("-o", "--output", help="Output filename (default is output.csv).")
    parser.add_argument("-t", "--tbr", help="Time elapsed between requests in seconds (default 10).", type=int)
    parser.add_argument("-T", "--tries", help="Number of times trying to fetch the page (default 3).", type=int)
    parser.add_argument("-w", "--warranty", help="Check out the warranty summary.", action="store_true")
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
            print("Error: {}".format(ex))
            logger.get_logger(maxbytes=1024 * 1024).error("Error: {}".format(ex))
