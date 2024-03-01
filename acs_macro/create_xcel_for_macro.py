from datetime import date

import openpyxl
from dateutil.relativedelta import relativedelta

polnum = '12345678'
str_date = date(2020, 12, 28)
end_date = date(2032, 12, 28)
curr_date = str_date

wb1 = openpyxl.load_workbook("jobs.xlsx")
ws1 = wb1.worksheets[0]
# ws1 = wb1['Sheet1']
# ws1 = wb1.get_sheet_by_name('Sheet1')
i = 1
j = 1

while curr_date <= end_date:
    print(curr_date)
    ws1.cell(row=i, column=1).value = 'l2polrnwl'
    ws1.cell(row=i, column=2).value = curr_date
    ws1.cell(row=i, column=3).value = polnum
    i += 1
    ws1.cell(row=i, column=1).value = 'l2newunitd'
    ws1.cell(row=i, column=2).value = curr_date
    ws1.cell(row=i, column=3).value = polnum
    i += 1
    curr_date = curr_date + relativedelta(months=1)

wb1.save("jobs.xlsx")
