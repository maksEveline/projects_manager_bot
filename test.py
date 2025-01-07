import time
from datetime import datetime, timedelta


def decode_unix_time(unix_time):
    return datetime.fromtimestamp(unix_time).strftime("%Y-%m-%d %H:%M:%S")


# Текущее время
now = datetime.now()

# Через месяц в 21:30
future_time = now + timedelta(days=30)
future_time = future_time.replace(hour=21, minute=30, second=0, microsecond=0)

# Unix время
future_unix_time = int(time.mktime(future_time.timetuple()))

print(future_unix_time)
print(decode_unix_time(future_unix_time))
