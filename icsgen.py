#!/usr/bin/python3

# ICS Generator

# Generates ICS files for a list of events according to an index
# and adds their respective URL to the index.

__author__ = 'Daylam Tayari'
__version__ = '0.1'
__copyright__ = 'Copyright (c) 2022 Daylam Tayari'
__license__ = 'GNU GPL v3'


# Imports

import re
import json


# Retrieve Indexes and Validate and Parse JSON:

def retrieve_validate(jfile):
    with open(jfile, 'r') as file:
        try:
            return json.load(file)
        except json.decoder.JSONDecodeError:
            print(f"Invalid JSON in file {file}")


events = retrieve_validate('events.json').get('events')
speakers = retrieve_validate('speaker-index.json').get('speakers')
categories = retrieve_validate('categories.json').get('categories')


# Validate Index Data Syntax:

speaker_ind = []
for s in speakers:
    speaker_ind.append(s.get('id'))

category_ind = []
for c in categories:
    category_ind.append(c.get('id'))


def validate_event(event):
    # Retrieve all values for reuse:
    name = event.get('name')
    date = event.get('date')
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
    if not isinstance(date, str) or date_reg.search(date) is None:
        if not isinstance(date, str):
            raise TypeError(f"Date value '{date}' is not a string.")
        raise ValueError(
            f"Date value '{date}' is not a valid ISO 8601 2019 format.'")
    if not isinstance(location, str):
        raise TypeError(f"Location name '{location}' is not a string.")
    if not isinstance(location_url, str) or re.search(r"http[s]?://(www\.)?.*", location_url) is None:
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


for event in events:
    validate_event(event)
