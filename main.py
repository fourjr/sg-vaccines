from collections import UserString
import enum
import typing
from enum import IntEnum
from datetime import datetime

import pytz
import requests
from dateutil.relativedelta import relativedelta
from requests.models import DEFAULT_REDIRECT_LIMIT


# https://appointment.vaccine.gov.sg/api/v1/locations?startDate=2021-06-04&endDate=2021-09-30&patientGroupId=3

class Routes:
    BASE = 'https://appointment.vaccine.gov.sg/api/v1'
    APPOINTMENT = BASE + '/appointments/{nric}/{code}'
    LOCATIONS = BASE + '/locations?startDate={start_date}&endDate={end_date}&patientGroupId={group_id}'
    AVAILABILITY = BASE + '/availability/{hci_code}?startDate={start_date}&endDate={end_date}&isFirstAppt={first_dose}'


class Group(IntEnum):
    # GENERAL = 0
    GENERAL = 1
    MOM_FOREIGN_WORKER = 2
    MOE_STUDENT_BELOW_18 = 3
    MOE_STUDENT_ABOVE_18 = 4


class ExitNow(BaseException):
    pass


def get_dates(start_dt=None, first_dose=True) -> typing.Tuple[str, str]:
    if start_dt is None:
        tz = pytz.timezone('Asia/Singapore')
        start_dt = datetime.now(tz)

    if first_dose:
        first_boost = relativedelta(days=1)
        second_boost = relativedelta(months=3, days=31 - start_dt.day)
    else:
        first_boost = relativedelta(weeks=6)
        second_boost = relativedelta(weeks=2)

    start_dt += first_boost
    start_date = start_dt.strftime(r'%Y-%m-%d')

    end_dt = start_dt + second_boost
    end_date = end_dt.strftime(r'%Y-%m-%d')

    return (start_date, end_date)


def format_date(dt, *, strftime=False):
    if isinstance(dt, str):
        dt = datetime.strptime(dt, r'%Y-%m-%dT%H:%M:%S.%fZ')

        if strftime:
            return dt.strftime(r'%d/%m/%Y %H%Mh')

    return dt


def pretty_print(header: typing.Tuple[str], values: typing.List[typing.Tuple[str]]):
    maxlens = []
    for i in header:
        maxlens.append(len(i))

    for val in values:
        for n, i in enumerate(val):
            if len(str(i)) > maxlens[n]:
                maxlens[n] = len(str(i))

    fmt = ''
    for n, i in enumerate(header):
        i = str(i)
        fmt += f'{i:^{maxlens[n] + 3}}'
    print(fmt)

    fmt = ''
    for n in range(len(header)):
        fmt +=  '-' * (maxlens[n] + 2) + ' '
    print(fmt)

    for val in values:
        fmt = ''
        for n, i in enumerate(val):
            i = str(i)
            if n == 0:
                fmt += f'{i:<{maxlens[n] + 3}}'
            else:
                fmt += f'{i:^{maxlens[n] + 3}}'

        print(fmt)


def print_locations(group: Group):
    start, end = get_dates()

    locations = requests.get(Routes.LOCATIONS.format(start_date=start, end_date=end, group_id=int(group))).json()
    locations = sorted(locations, key=lambda x: format_date(x['earliestSlot']).timestamp() if x['earliestSlot'] else 10**10)
    # List[Dict['name', 'hci_code', 'address', 'latitude', 'longitude', 'earliestSlot', 'priority', 'minInterval', 'maxInterval', 'minClinicInterval', 'maxClinicInterval', 'vaccineType']]
    
    header = ('Location', 'ID', 'Earliest Slot', 'Vaccine Type')

    values = []
    for loc in locations:
        values.append((loc['name'], loc['hci_code'], format_date(loc['earliestSlot'], strftime=True), loc['vaccineType']))

    pretty_print(header, values)


def print_details(hci_code, start_dt=None, first_dose=True):
    start, end = get_dates(start_dt, first_dose)

    availability = requests.get(Routes.AVAILABILITY.format(start_date=start, end_date=end, hci_code=hci_code, first_dose=first_dose)).json()
    # Dict[date: Dict[id, time, capacity, count]]

    if not availability:
        print('No available timeslots')
        return

    print('Dates', ', '.join(availability.keys()), sep=': ')
    date = input('Pick a date from above: ')
    print()
    try:
        chosen = availability[date]
    except KeyError:
        print('Invalid choice')
        return

    header = ('Time', 'Availability')
    values = []
    for i in chosen:
        time = format_date(i['time']).strftime(r'%H%Mh')
        vals = (time, f"{i['count']}/{i['capacity']}")
        values.append(vals)

    pretty_print(header, values)


def get_locations():
    print('Which group?')
    for i in Group:
        print(f'{i.value}: {i.name}')

    try:
        group = Group(int(input()))
    except ValueError:
        print('Invalid group ID')
        raise ExitNow
    else:
        print(group.name)
        print()
        print_locations(group)


def main():
    try:
        get_locations()
    except ExitNow:
        return

    print()
    loc_id = input('Location ID: ')
    try:
        dose = int(input('1: First Dose\n2: Second Dose\nDose number: '))
    except ValueError:
        dose = -1

    if dose == 1:
        print_details(loc_id)
    elif dose == 2:
        date = input('Date of first dose in DD/MM/YYYY format: ')
        try:
            date = datetime.strptime(date, r'%d/%m/%Y')
        except ValueError:
            print('Invalid input')
        else:
            print_details(loc_id, start_dt=date, first_dose=False)
    else:
        print('Invalid input')


if __name__ == '__main__':
    main()
