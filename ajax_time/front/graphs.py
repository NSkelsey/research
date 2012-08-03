import os
import sys
import matplotlib
import matplotlib.pyplot as plt
import StringIO
import urllib, base64
from datetime import date




def make_img_tag(fig):

    imgdata = StringIO.StringIO()
    fig.savefig(imgdata, format='png', bbox_inches="tight")
    imgdata.seek(0)  # rewind the data

    uri = 'data:image/png;base64,' + urllib.quote(base64.b64encode(imgdata.buf))
    html = '<img src = "%s"/>' % uri
    return html

def segment_mr_month(mr_list, start_date=date(1996,12,12), end_date=date(2012,12,12)):
    e_key = {}
    for i in mr_list:
        if e_key.get(i.event_key) is not None:
            pass
        else:
            e_key[i.event_key] = i
    mr_list = e_key.values()
    date_list = [i.date_event for i in mr_list if i.date_event]
    date_list.sort()
    print len(date_list)
    cdate = start_date
    cdate = cdate.replace(day=1)
    bucket_list = []
    while cdate < end_date:
        bucket_list.append(cdate)
        if cdate.month == 12:
            cdate = cdate.replace(month=1, year=cdate.year+1)
        else: 
            cdate = cdate.replace(month=cdate.month+1)
    count_li = []
    pos = 0
    for date in bucket_list:
        count = 0
        try:
            while date_list[pos] < date:
                count += 1
                pos += 1
        except (IndexError):
            pass
        count_li.append(count)


    return (bucket_list, count_li)

