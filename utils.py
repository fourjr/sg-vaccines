import typing
from datetime import datetime

import pytz
from dateutil.relativedelta import relativedelta


__all__ = ('get_dates', 'parse_date', 'pretty_print')


def get_dates(first_dose_date: typing.Optional[datetime]=None) -> typing.Tuple[str, str]:
    """Calculates the dates required for API requests

    Arguments
    ---------
    first_dose_date: datetime.datetime - Optional
        The date of the first dose
        Expected to be included if first_dose=False
        Should be None if there is no first dose

    Returns
    -------
    Tuple[str, str] -> (start_date, end_date)
    """

    if first_dose_date is None:
        tz = pytz.timezone('Asia/Singapore')
        start_dt = datetime.now(tz)
    else:
        start_dt = first_dose_date

    if first_dose_date:
        first_boost = relativedelta(weeks=6)
        second_boost = relativedelta(weeks=2)
    else:
        first_boost = relativedelta(days=1)
        second_boost = relativedelta(months=3, days=31 - start_dt.day)

    start_dt += first_boost
    start_date = start_dt.strftime(r'%Y-%m-%d')

    end_dt = start_dt + second_boost
    end_date = end_dt.strftime(r'%Y-%m-%d')

    return (start_date, end_date)


def parse_date(dt: typing.Optional[str]) -> typing.Optional[typing.Union[datetime, str]]:
    """Formats the date from a `%Y-%m-%dT%H:%M:%S.%fZ` format

    Arguments
    ---------
    dt: Optional[str]
        Datetime formatted as `%Y-%m-%dT%H:%M:%S.%fZ`.
        If dt is not a str, dt is returned as-is.

    Returns
    -------
    A `datetime.datetime` object or a str or the original type
    """
    if isinstance(dt, str):
        dt = datetime.strptime(dt, r'%Y-%m-%dT%H:%M:%S.%fZ') + relativedelta(hours=8)  # convert to UTC+8

    return dt


def pretty_print(header: typing.Tuple[str], values: typing.List[typing.Tuple[str]]) -> None:
    """Prints the given data formatted as a nice table into stdout

    Arguments
    --------
    header: Tuple[str]
        Should have the same length as a data entry

    values: List[Tuple[str]]
        List of rows, each tuple is a data entry

    Example
    -------
    ```python
        pretty_print(('Name', 'Class'), [('Tom', '1A'), ('Tim', '1B')])
    ```
    """

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
        fmt += '-' * (maxlens[n] + 2) + ' '
    print(fmt)

    for val in values:
        fmt = ''
        for n, i in enumerate(val):
            i = str(i)
            fmt += f'{i:^{maxlens[n] + 3}}'

        print(fmt)
