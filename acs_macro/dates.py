from datetime import datetime, date

from dateutil.relativedelta import relativedelta

date1 = date.fromisoformat('2023-01-16')
print(date1)
print(date1.strftime('%m/%d/%Y'))  # formatted date
print()

date1 = date(2023, 1, 16)
print(date1)
print(date1.strftime('%m/%d/%Y'))  # formatted date
print()

date2 = date.fromisoformat('2024-02-18')  # another way to create date
d = date2 - date1
print(f'Difference in days = {d.days}')
print()

date1 = date(1972, 3, 30)
date2 = date.today()
diff_years = relativedelta(date2, date1).years
print(f'Difference in years = {diff_years}')
print(relativedelta(date2, date1))
print()

date1 = date.today()
new_date = date1 + relativedelta(months=1)
print(f'Add 1 month to todays date = {new_date}')
print()

###############################################################################

sdate = '11/17/2023'
split_date = sdate.split('/')

date1 = datetime(int(split_date[2]), int(split_date[0]), int(split_date[1]))
date2 = date1 + relativedelta(months=1)

fdate1 = date1.strftime("%m/%d/%Y")
fdate2 = date2.strftime("%m/%d/%Y")

print(date1)
print(fdate1)
print(fdate2)
