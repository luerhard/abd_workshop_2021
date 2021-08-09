import datetime as dt


def strpdate(date_string, dateformat):
    with_time = dt.datetime.strptime(date_string, dateformat)
    return with_time.date()
