import datetime

previous_week_start = (datetime.datetime.now().date() - datetime.timedelta(days=datetime.datetime.now().weekday())) - datetime.timedelta(days=7)
current_week_end = previous_week_start + datetime.timedelta(days=13)

print(previous_week_start)
print(current_week_end)