from datetime import datetime

from dateutil.relativedelta import relativedelta

sdate = '11/17/2023'

split_date = sdate.split('/')

date1 = datetime(int(split_date[2]), int(split_date[0]), int(split_date[1]))
date2 = date1 + relativedelta(months=1)

fdate1 = date1.strftime("%m/%d/%Y")
fdate2 = date2.strftime("%m/%d/%Y")

print(date1)
print(fdate1)
print(fdate2)
