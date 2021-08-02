from datetime import datetime
import typing
from enum import IntEnum

import requests

from utils import parse_date, get_dates


__all__ = ('Routes', 'Group', 'Location', 'TimeSlot', 'API')


class Routes:
    BASE = 'https://appointment.vaccine.gov.sg/api/v1'
    APPOINTMENT = BASE + '/appointments/{nric}/{code}'
    LOCATIONS = BASE + '/locations?startDate={start_date}&endDate={end_date}&patientGroupId={group_id}'
    AVAILABILITY = BASE + '/availability/{hci_code}?startDate={start_date}&endDate={end_date}&isFirstAppt={first_dose}'


class Group(IntEnum):
    """Group of people from the vaccination drive"""
    # GENERAL = 0
    GENERAL = 1
    MOM_FOREIGN_WORKER = 2
    MOE_STUDENT_BELOW_18 = 3
    MOE_STUDENT_ABOVE_18 = 4


class VaccineType(IntEnum):
    Pfizer_Comirnaty = 1
    Moderna = 2


class Location:
    # List[Dict['name', 'hci_code', 'address', 'latitude', 'longitude', 'earliestSlot', 'priority', 'minInterval', 'maxInterval', 'minClinicInterval', 'maxClinicInterval', 'vaccineType']]
    def __init__(self, api: 'API', data: typing.Dict[str, typing.Union[int, str]]) -> None:
        self._api = api

        self.name = data.pop('name')
        self.hci_code = data.pop('hci_code')
        self.address = data.pop('address', None)
        self.latitude = data.pop('latitude', None)
        self.longitude = data.pop('longitude', None)
        self.earliest_slot = parse_date(data.pop('earliestSlot'))
        self.priority = data.pop('priority', None)
        self.min_interval = data.pop('minInterval', None)
        self.max_interval = data.pop('maxInterval', None)
        self.min_clinic_interval = data.pop('minClinicInterval', None)
        self.max_clinic_interval = data.pop('maxClinicInterval', None)
        self.vaccine_type = VaccineType[data.pop('vaccineType').replace('/', '_')]

    def get_date_slots(self, first_dose_date: datetime=None) -> typing.Dict[str, typing.List['TimeSlot']]:
        return self._api.get_date_slots(self.hci_code, first_dose_date)


class TimeSlot:
    def __init__(self, api: 'API', data: typing.Dict[str, typing.Union[int, str]]) -> None:
        self._api = api

        self.id = data.pop('id', None)
        self.time = parse_date(data.pop('time', None))
        self.has_capacity = data.pop('hasCapacity')


class API:
    def __init__(self) -> None:
        self.session = requests.Session()

    def request(self, endpoint: str, **kwargs: typing.Union[str, int]) -> typing.Dict[str, typing.Union[int, str]]:
        r = self.session.get(endpoint.format(**kwargs))
        return r.json()

    def get_locations(self, group: Group) -> typing.List[Location]:
        start, end = get_dates()
        locations = self.request(Routes.LOCATIONS, start_date=start, end_date=end, group_id=int(group))
        return [Location(self, x) for x in locations]

    def get_date_slots(self, hci_code: str, first_dose_date: datetime=None) -> typing.Dict[str, typing.List[TimeSlot]]:
        start, end = get_dates(first_dose_date)
        r = self.request(Routes.AVAILABILITY, hci_code=hci_code, start_date=start, end_date=end, first_dose=bool(first_dose_date))
        return {k: [TimeSlot(self, x) for x in v] for k, v in r.items()}


class ExitNow(BaseException):
    """Exit the program"""
    pass
