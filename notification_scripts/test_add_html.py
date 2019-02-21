# from matplotlib import pyplot as plt
from report_builder import Email
from pymongo import MongoClient
import pandas as pd
from config import sender, username, password

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

# table_df = pd.DataFrame(deltas)

# chart_name = 'img1'
# plt.figure()

# table_df.plot(kind='bar')
# plt.xlabel("X Label")
# plt.ylabel("Y Label")

# plt.savefig(f'{chart_name}.png')
# image_filename = f'{chart_name}.png'


sample_report = Email(debug=True)

try:
    html_template = 'html_templates/sample_email.html'
    sample_report.append_html(html_template)

    sample_report.send()

except:
    sample_report.send_notification(f'Error sending the email for {__name__}.')
