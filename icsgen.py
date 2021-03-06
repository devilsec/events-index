#!/usr/bin/python3

# ICS Generator

# Generates ICS files for a list of events according to an index
# and adds their respective URL to the index.

__author__ = 'Daylam Tayari'
__version__ = '1.0'
__copyright__ = 'Copyright (c) 2022 Daylam Tayari'
__license__ = 'GNU GPL v3'


# Imports

import re
import json
from collections import Counter
from typing import Type
from ics import Calendar, Event
from calendar import month_abbr
from datetime import datetime


ics_path = "ics/"


# Retrieve Indexes and Validate and Parse JSON:

def retrieve_validate(jfile):
    with open(jfile, 'r') as file:
        try:
            return json.load(file)
        except json.decoder.JSONDecodeError:
            raise TypeError(f"Invalid JSON in file {file}")


events = retrieve_validate('events.json').get('events')
speakers = retrieve_validate('speakers.json').get('speakers')
categories = retrieve_validate('categories.json').get('categories')


# Validate Index Data Syntax:

speaker_keys = ['id', 'name', 'description']
category_keys = ['id', 'name']
event_keys = ['name', 'date', 'duration', 'location', 'locationURL',
              'speakers', 'category', 'description', 'icsURL']


def validate_speaker(speaker):
    if Counter(speaker.keys()) != Counter(speaker_keys):
        raise KeyError('The keys for at least one speaker are not valid.')
    id = speaker.get('id')
    name = speaker.get('name')
    description = speaker.get('description')
    if not isinstance(id, int):
        raise TypeError(
            f"The ID of the speaker with ID '{id}' is not an integer.")
    if not isinstance(name, str):
        raise TypeError(
            f"The name of the speaker with ID '{id}' is not a string.")
    if not isinstance(description, str):
        raise TypeError(
            f"The description of the speaker with ID '{id}' is not a string.")
    # Return True if the speaker is valid.
    return True


def validate_category(category):
    if Counter(category.keys()) != Counter(category_keys):
        raise KeyError('The keys for at least one category are not valid.')
    id = category.get('id')
    name = category.get('name')
    if not isinstance(id, int):
        raise TypeError(
            f"The ID of the speaker with ID '{id}' is not an integer.")
    if not isinstance(name, str):
        raise TypeError(
            f"The name of the speaker with ID '{id}' is not a string.")
    # Return True if the category is valid.
    return True


speaker_ind = []
for s in speakers:
    validate_speaker(s)
    speaker_ind.append(s.get('id'))

category_ind = []
for c in categories:
    validate_category(c)
    category_ind.append(c.get('id'))


def validate_event(event):
    # Check if the keys are the same:
    if Counter(event.keys()) != Counter(event_keys):
        raise KeyError('The keys for at least one event are not valid.')
        # Retrieve all values for reuse:
    name = event.get('name')
    date = event.get('date')
    duration = event.get('duration')
    location = event.get('location')
    location_url = event.get('locationURL')
    speakers = event.get('speakers')
    category = event.get('category')
    description = event.get('description')
    date_reg = re.compile(
        r"^(\-\-|[0-9]{4}[\-]?)([0-1][0-9])[\-]?[0-3][0-9]T[0-2][0-9](:[0-6][0-9])?(:[0-6][0-9])?(:[0-9]{2})?([+-][0-2][0-9](:[0-6][0-9])?)?$")
    # Validate the values:
    if not isinstance(name, str):
        print(type(name))
        raise TypeError(f"Event name '{name}' is not a string.")
    if not isinstance(date, str):
        raise TypeError(f"Date value '{date}' is not a string.")
    elif date_reg.fullmatch(date) is None:
        raise ValueError(
            f"Date value '{date}' is not a valid ISO 8601 2019 format.'")
    if not isinstance(duration, str):
        raise TypeError(f"Duration value '{duration} is not a string.'")
    elif re.fullmatch(r"^([0-9]*[dhms])([0-9]+h)?([0-9]+m)?([0-9]+s)?$", duration) is None:
        raise ValueError(
            f"Duration value '{duration}' is not in a valid format.")
    if not isinstance(location, str):
        raise TypeError(f"Location name '{location}' is not a string.")
    if not isinstance(location_url, str) or re.fullmatch(r"http[s]?://(www\.)?.*", location_url) is None:
        if not isinstance(location_url, str):
            raise TypeError(f"Location URL {location_url} is not a string.")
        raise ValueError(f"Location URL '{location_url}' is not a valid URL.")
    if not isinstance(speakers, list):
        raise TypeError(f"Speakers for event with name {name} is not a list.")
    else:
        for s in speakers:
            if isinstance(s, int):
                if s not in speaker_ind:
                    raise IndexError(
                        f"Speaker index {s} for event with name {name} is not a valid speaker index.")
            else:
                raise TypeError(f"Speaker index '{s}' is not an integer.")
    if not isinstance(category, int):
        raise TypeError(
            f"Category '{category}' for event with name {name} is not an integer.")
    else:
        if category not in category_ind:
            raise IndexError(
                f"Category {category} is not a valid category index.")
    if not isinstance(description, str):
        raise TypeError(
            f"Description for event with name {name} is not a string.")
    # Return True if the syntax of the event name is valid:
    return True


def ics_duration(event):
    duration_groups = re.search(
        "^([0-9]*[dhms])([0-9]+h)?([0-9]+m)?([0-9]+s)?$", event.get('duration'))
    days = None
    hours = None
    minutes = None
    seconds = None
    duration_dict = {}
    if duration_groups is None:
        raise ValueError(
            f"Invalid duration for event with ID {event.get('id')}.")
    for g in duration_groups.groups():
        if g is not None:
            spec = g[-1].lower()
            if spec == 'd':
                days = g
            elif spec == 'h':
                hours = g
            elif spec == 'm':
                minutes = g
            else:
                seconds = g
    if days is not None:
        duration_dict['days'] = int(days[:-1])
    if hours is not None:
        duration_dict['hours'] = int(hours[:-1])
    if minutes is not None:
        duration_dict['minutes'] = int(minutes[:-1])
    if seconds is not None:
        duration_dict['seconds'] = int(seconds[:-1])
    return duration_dict


def valid_path_name(name):
    name.replace(' ', '_')  # Not invalid, stylistic inclusion.
    name.replace('\"', '-')
    name.replace('\\', '-')
    name.replace('/', '-')  # Not invalid, stylistic inclusion.
    name.replace('\'', '-')  # Not invalid, stylistic inclusion.
    name.replace('>', '-')
    name.replace('<', '-')
    name.replace('|', '-')
    return name


def export_ics(cal, event_dict):
    event = list(cal.events)[0]
    file_name = f"{ics_path}DevilSec-{valid_path_name(event.name)}-{event.begin.day}-{month_abbr[event.begin.month]}-{event.begin.year}.ics"
    with open(file_name, 'w') as f:
        f.writelines(cal)
    event_dict[
        'icsURL'] = f"https://raw.githubusercontent.com/devilsec/events-index/master/{file_name}"


def gen_ics(event):
    cal = Calendar()
    ev = Event()
    ev.name = event.get('name')
    ev.begin = event.get('date')
    ev.duration = ics_duration(event)
    ev.location = event.get('location')
    ev.url = 'https://devilsec.org'
    ev.description = f"Location: {ev.location} - {event.get('locationURL')}\n{event.get('description')}"
    ev.status = "CONFIRMED"
    ev.created = datetime.utcnow()
    cal.events.add(ev)
    export_ics(cal, event)


for event in events:
    validate_event(event)
    gen_ics(event)


events = {"events": events}

with open('events.json', 'w') as f:
    json.dump(events, f, indent=4)
