import pandas as pd
import strenkcloud
# from email_template import text_template, html_template
from pymongo import MongoClient

from connstring import conn_string_mongo


client = MongoClient(conn_string_mongo)
db = client.test_database
stockData = db.stockData
sectorData = db.sectorData


def get_sector_data():
    data = sectorData.find_one()
    sectors = []
    deltas = []
    for items in data['data']:
        sectors.append(items['Sector'])
        deltas.append(items['pct_delta'])
    return sectors, deltas


# data = [1, 6, 3, 4]
# labels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday']
# title = 'some Test numbers'

sectors, deltas = get_sector_data()
# labels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday']
title = 'Testing Pandas datasource'
print(sectors)
print(deltas)

table_df = pd.DataFrame(zip(sectors, deltas), columns=['Sectors', '% Change'])
print(table_df.dtypes)

chart_name = 'img1'
plt.bar(data)
plt.xlabel(xlabel)
plt.ylabel(ylabel)
plt.savefig(f'{chart_name}.png')
filename = f'{chart_name}.png'

# img1 = strenkcloud.generate_jpg('img1', table_df, title)


# Email template setup
text_template = '''Hi!\nThis is a test email\nI hope it is working!'''

html_template = '''
<!DOCTYPE HTML>
<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"><title></title>
  <style type="text/css">
    #outlook a {padding:0;}
    body{width:100% !important; -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; margin:0; padding:0;} /* force default font sizes */
    .ExternalClass {width:100%;} .ExternalClass, .ExternalClass p, .ExternalClass span, .ExternalClass font, .ExternalClass td, .ExternalClass div {line-height: 100%;} /* Hotmail */
    table td {border-collapse: collapse;}
    @media only screen and (min-width: 600px) { .maxW { width:600px !important; } }
  </style>
</head>
<body style="margin: 0px; padding: 0px; -webkit-text-size-adjust:none; -ms-text-size-adjust:none;" leftmargin="0" topmargin="0" marginwidth="0" marginheight="0" bgcolor="#FFFFFF"><table bgcolor="#FFFFFF" width="100%" border="0" align="center" cellpadding="0" cellspacing="0"><tr><td valign="top">
<!--[if (gte mso 9)|(IE)]>
<table width="600" align="center" cellpadding="0" cellspacing="0" border="0"><tr><td valign="top">
<![endif]-->
<table width="100%" class="maxW" style="max-width: 600px; margin: auto;" border="0" align="center" cellpadding="0" cellspacing="0"><tr><td valign="top" align="center">
'''

# Add an image
html_template += '<img src="cid:' + f'{filename}' + '">'

html_template += table_df.to_html(index=False,
                                  justify='center',
                                  bold_rows=True)

# End of the html template
html_template += '''
</td></tr></table>
<!--[if (gte mso 9)|(IE)]>
</td></tr></table>
<![endif]-->
</td></tr></table></body></html>
'''


strenkcloud.send(
    subject='Notification Test',
    text_template=text_template,
    html_template=html_template,
    image=img1)
