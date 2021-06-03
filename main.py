from datetime import datetime

from models import API, ExitNow, Group
from utils import pretty_print


client = API()


def print_locations(group: Group) -> None:
    """Prints out the locations for a specific group

    Arguments
    ---------
    group: Group
        Group from the vaccination drive
    """
    locations = client.get_locations(group)
    locations = sorted(locations, key=lambda x: x.earliest_slot.timestamp() if x.earliest_slot else 10**10)

    header = ('ID', 'Location', 'Earliest Slot', 'Vaccine Type')

    values = []
    for loc in locations:
        if loc.earliest_slot:
            earliest_slot = loc.earliest_slot.strftime(r'%d/%m/%Y %H%Mh')
        else:
            earliest_slot = None

        values.append((loc.hci_code, loc.name, earliest_slot, loc.vaccine_type.name))

    pretty_print(header, values)


def print_details(hci_code: str, first_dose_date: datetime=None) -> None:
    """Prints out the availability details of a timeslot

    Arguments
    ---------
    hci_code: str
        Vaccination center code

    first_dose_date: datetime.datetime - Optional
        The date of the first dose
        Expected to be included if first_dose=False
        Should be None if there is no first dose
    """

    dateslots = client.get_date_slots(hci_code, first_dose_date)

    if not dateslots:
        print('No available timeslots')
        return

    print('Dates', ', '.join(dateslots.keys()), sep=': ')
    date = input('Pick a date from above: ')
    print()
    try:
        chosen = dateslots[date]
    except KeyError:
        print('Invalid choice')
        return

    header = ('Time', 'Availability')
    values = []
    for i in chosen:
        time = i.time.strftime(r'%H%Mh')
        vals = (time, str(i))
        values.append(vals)

    pretty_print(header, values)


def get_locations() -> None:
    """Gets the location from user input"""
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


def main() -> None:
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
            print_details(loc_id, date)
    else:
        print('Invalid input')


if __name__ == '__main__':
    main()
