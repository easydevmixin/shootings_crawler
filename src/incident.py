# -*- coding: utf-8 -*-

import hashlib


class Incident:
    def __init__(self, *args, **kwargs):
        self.year = kwargs.get('year', 1970)
        self.month = kwargs.get('month', 1)
        self.day = kwargs.get('day', 1)
        self.state = kwargs.get('state', '')
        self.city_or_county = kwargs.get('city_or_county', '')
        self.address = kwargs.get('address', '')
        self.num_killed = kwargs.get('num_killed', 0)
        self.num_injured = kwargs.get('num_injured', 0)
        self.incident_link = kwargs.get('incident_link', '')
        self.sha256 = ''
        self.lat = kwargs.get('lat', 0)
        self.lon = kwargs.get('lon', 0)
        self.participants = []  # list of dictionaries
        self.characteristics = []  # list
        self.notes = ''
        self.guns_involved = []  # list of dictionaries
        self.district = {}  # dictionary

    def __str__(self):
        return "{}/{}/{}, {}".format(self.year, self.month, self.day, self.incident_link)
    __repr__ = __str__

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, val):
        self._year = val
        if hasattr(self, 'sha256'):
            self.sha256 = 1

    @property
    def month(self):
        return self._month

    @month.setter
    def month(self, val):
        self._month = val
        if hasattr(self, 'sha256'):
            self.sha256 = 1

    @property
    def day(self):
        return self._day

    @day.setter
    def day(self, val):
        self._day = val
        if hasattr(self, 'sha256'):
            self.sha256 = 1

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, val):
        self._state = val
        if hasattr(self, 'sha256'):
            self.sha256 = 1

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, val):
        self._state = val
        if hasattr(self, 'sha256'):
            self.sha256 = 1

    @property
    def city_or_county(self):
        return self._city_or_county

    @city_or_county.setter
    def city_or_county(self, val):
        self._city_or_county = val
        if hasattr(self, 'sha256'):
            self.sha256 = 1

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, val):
        self._address = val
        if hasattr(self, 'sha256'):
            self.sha256 = 1

    @property
    def num_killed(self):
        return self._num_killed

    @num_killed.setter
    def num_killed(self, val):
        self._num_killed = val
        if hasattr(self, 'sha256'):
            self.sha256 = 1

    @property
    def num_injured(self):
        return self._num_injured

    @num_injured.setter
    def num_injured(self, val):
        self._num_injured = val
        if hasattr(self, 'sha256'):
            self.sha256 = 1

    @property
    def incident_link(self):
        return self._incident_link

    @incident_link.setter
    def incident_link(self, val):
        self._incident_link = val
        if hasattr(self, 'sha256'):
            self.sha256 = 1

    @property
    def sha256(self):
        return self._sha256

    @sha256.setter
    def sha256(self, val):
        st = "{}{}{}{}{}{}{}{}{}".format(
            self.year, self.month, self.day, self.state, self.city_or_county,
            self.address, self.num_killed, self.num_injured, self.incident_link
        )
        self._sha256 = hashlib.sha256(st.encode(encoding='utf_8')).hexdigest()

    @property
    def lat(self):
        return self._lat

    @lat.setter
    def lat(self, val):
        self._lat = val

    @property
    def lon(self):
        return self._lon

    @lon.setter
    def lon(self, val):
        self._lon = val

    @property
    def participants(self):
        return self._participants

    @participants.setter
    def participants(self, val):
        self._participants = val

    @property
    def characteristics(self):
        return self._characteristics

    @characteristics.setter
    def characteristics(self, val):
        self._characteristics = val

    @property
    def notes(self):
        return self._notes

    @notes.setter
    def notes(self, val):
        self._notes = val

    @property
    def guns_involved(self):
        return self._guns_involved

    @guns_involved.setter
    def guns_involved(self, val):
        self._guns_involved = val

    @property
    def district(self):
        return self._district

    @district.setter
    def district(self, val):
        self._district = val

    def to_csv(self):
        return [self.sha256, self.year, self.month, self.day, self.state, self.city_or_county,
                self.address, self.num_killed, self.num_injured, self.incident_link,
                self.lat, self.lon, self.participants, self.characteristics, self.notes,
                self.guns_involved, self.district]

    def __eq__(self, other):
        return self.sha256 == other.sha256
