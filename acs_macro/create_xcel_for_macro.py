from datetime import date

from dateutil.relativedelta import relativedelta
from openpyxl import Workbook

polnum = '07329178'
str_date = date(2031, 6, 17)
end_date = date(2033, 6, 17)
curr_date = str_date

wb = Workbook()
ws = wb.active
# ws1.delete_cols(1,3) # delete 3 columns

i = 1
j = 1
while curr_date <= end_date:
    print(curr_date)
    ws.cell(row=i, column=1).value = 'l2polrnwl'
    ws.cell(row=i, column=2).value = curr_date
    ws.cell(row=i, column=3).value = polnum
    i += 1
    ws.cell(row=i, column=1).value = 'l2newunitd'
    ws.cell(row=i, column=2).value = curr_date
    ws.cell(row=i, column=3).value = polnum
    i += 1
    curr_date = curr_date + relativedelta(months=1)

xl_filename = "jobs" + '-' + polnum + '-' + str(str_date) + '-' + str(end_date) + ".xlsx"
wb.save(xl_filename)
