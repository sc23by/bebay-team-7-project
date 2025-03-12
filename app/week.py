from datetime import datetime, timedelta

def split_into_weeks(start_date):
    weeks = []
    current_date = start_date

    while current_date.weekday() != 6:
        current_date -= timedelta(days = 1)

    for i in range(4):
        week_start = current_date
        week_end = current_date + timedelta(days = 6)
        weeks.append({
            'week_start': week_start.strftime('%Y-%m-%d'),
            'week_end' : week_end.strftime('%Y-%m-%d') 
        })

        current_date = week_end + timedelta(days=1)

    return weeks