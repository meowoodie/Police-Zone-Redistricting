import xlrd
import arrow
import numpy as np

calls = []
fname = "Jan-APR-2019-PD"
wb    = xlrd.open_workbook("data/%s.xls" % fname)
sheet = wb.sheet_by_index(0) 
for i in range(1, sheet.nrows): 
    row = sheet.row_values(i)
    call_t   = row[4]
    lat, lng = row[8], row[9]
    travel_t = row[12]
    serv_t   = row[13]
    if call_t != "" and lat != "" and lng != "" and travel_t != "" and serv_t != "":
        call_t = arrow.get(call_t, "MM/DD/YYYY HH:mm:ss")
        calls.append([ call_t.timestamp, float(lng), float(lat), float(travel_t), float(serv_t) ])

calls = np.array(calls)
print(calls)
np.save("data/%s.npy" % fname, calls)
