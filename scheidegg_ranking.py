# Get Ranking, (c) Thomas Kamps with help of Danilo's code. Many thanks Danilo!!!
# parses XCONTEST-RSS-Feed and extracts the first 30 places Many thanks to XContest team helping me :-)!!!
from datetime import date, timedelta
import datetime
import requests
import ftplib
from PIL import Image, ImageDraw, ImageFont
import csv
import constants


# get the old flights stored in a csv.
flights = []
csvfile = open('/home/solarmanager/xc_ranking/scheidegg_flights.csv', newline='', encoding='utf-8-sig')
reader = csv.DictReader(csvfile, delimiter=';')
# Put each flight as a dictionary in the flights-list.
for row in reader:
    flights.append(row)
# save and close the file
csvfile.close()

url = 'https://www.xcontest.org/rss/flights/?world/en&site=Scheidegg&faiclass=3'
max_rank = 30
rank = 0
rss_flights = []
f_type = 'UND'


# function to extract an XML-tag
def get_value(html_string, tag_name, tag_end):
    if html_string.find(tag_name) == -1:
        return ''
    value_start = html_string.find(tag_name) + len(tag_name)
    value_end = html_string.find(tag_end, value_start)
    return str(html_string)[value_start: value_end]


# try to get the data from the RSS-Feed
session = requests.Session()
r = session.get(url, headers={'user-agent': 'dczo_club_ranking_alp_scheidegg'})
whole_content = r.text
print('Call response: ', whole_content)

# loop through the RSS-feed
while len(get_value(whole_content, '<item>', '</item>')) > 10:
    # return the item
    item = get_value(whole_content, '<item>', '</item>')
    link = get_value(item, '<link>', '</link>')
    f_date = get_value(item, '<title>', ' [')
    name = get_value(item, '] ', '</title>')
    distance = get_value(item, ' [', 'km ::')
    pre_type = get_value(item, ':: ', ' ::')
    if pre_type.find('free_flight') >= 0:
        f_type = 'STR'
    elif pre_type.find('free_triangle') >= 0:
        f_type = 'FLD'
    elif pre_type.find('fai_triangle') >= 0:
        f_type = 'FAI'
    points = get_value(item, pre_type + ' ::', 'p]')
    rank += 1
    # cut of the result from the rest
    whole_content = str(whole_content)[whole_content.find('</item>') + 5:len(whole_content)]
    print(rank, ': ', f_date, ', ', name, ', ', distance, ', ', f_type, ', ', points, ', ', link)
    rss_flights.append({'flight_date': f_date.strip(), 'pilot': name.strip(), 'flight_type': f_type,
                        'distance': distance.strip(), 'points': points.strip(), 'link': link.strip()})

for flight in rss_flights:
    print(flight)


# Definition of the sorting
def sorting_points(e):
    return float(e['points'])


def flight_svg(ftype):
    svg = ftype
    if ftype == "FAI":
        svg = '<img src="/images/thomaskamps/svg/fai.svg">'
    if ftype == "STR":
        svg = '<img src="/images/thomaskamps/svg/str.svg">'
    if ftype == "FLD":
        svg = '<img src="/images/thomaskamps/svg/fld.svg">'
    return svg


# merge rss_flights into flights
rss_index = 0
new_flight = 1
print('merging results')
while rss_index < len(rss_flights):
    rss_link = rss_flights[rss_index]['link']
    for flight in flights:  # does the rss_flight already exist?
        if flight['link'] == rss_link:
            new_flight = 0
    if new_flight == 1:
        flights.append(rss_flights[rss_index])
    rss_index = rss_index + 1
print(len(flights))

flights.sort(reverse=True, key=sorting_points)  # sorting so easy :-)

for flight in flights:
    print(flight)

# saving the updated file
csvfile = open('/home/solarmanager/xc_ranking/scheidegg_flights.csv', 'w', newline='', encoding='utf-8-sig')
headers = ['flight_date', 'pilot', 'flight_type', 'distance', 'points', 'link']
c = csv.DictWriter(csvfile, fieldnames=headers, delimiter=';')
# write a header row
c.writeheader()
# write all rows from list to file and close it
c.writerows(flights)
csvfile.close()


# Styles
styles = '<style> html {font-family: "brandon-grotesque-n7","brandon-grotesque", sans-serif; font-size: 10pt; ' \
         'background: #eef6fa; color: #4f5a80; } table, td, th, a, p {font-size: 10pt; padding: 4pt;} ' \
         'tr { background-color: aliceblue;} tr:not(:first-child):hover {background-color: skyblue;} ' \
         '.new{background-color: cornsilk;} a:link {color: darkred; text-decoration: none;} </style>'
ranking_path = 'ranking.html'  # adapt to file location
max_rank = 30
rank = 0
new_flights = []
# Variables
today = date.today()
time_now = datetime.datetime.now()
whole_content = ''
flight_type = ''
html_output = styles + '<a>Stand: ' + today.strftime("%d.%m.%Y") + ' ' + time_now.strftime("%H:%M") + ' Uhr' \
              + '</a><table><tr><td><b>Rang</td><td><b>Pilotin / Pilot</td>'
html_output += '<td><b>Distanz</td><td><b>Punkte</td><td><b>Datum</td><td><b>Typ</td><td><b>XContest</td></tr>'


# loop through the flights
while rank < min(max_rank, len(flights)):
    # new flight?
    flight_date = date(int(flights[rank]['flight_date'][6: 8]) + 2000, int(flights[rank]['flight_date'][3: 5]),
                       int(flights[rank]['flight_date'][0: 2]))
    delta_date = today - flight_date
    new_flag = ''
    new_tag = ''
    if delta_date.days <= 7:   # everything, newer than 1 week is taken as new.
        new_tag = ' (neu)'
        new_flag = ' class = "new"'
        new_flights.append(flights[rank]['points'])
    # write out the html-code
    table_row = '<tr' + new_flag + '><td>' + str(rank + 1) + new_tag + '</td><td>' + flights[rank]['pilot']
    table_row += '</td><td>' + flights[rank]['distance'] + ' km</td><td>' + flights[rank]['points'] + ' pts</td><td>'
    table_row += flights[rank]['flight_date'] + '</td><td>' + flight_svg(flights[rank]['flight_type'])
    table_row += '</td><td><a href="' + flights[rank]['link'] + '" target="_blank">Details</a></td></tr>'
    html_output += table_row
    rank += 1
html_output += '</table>'
print(html_output)
# write out status
result_file = open('/home/solarmanager/xc_ranking/ranking_result.html', 'w')
result_file.write(html_output)
result_file.close()
print("ranking created")

# -------------------------------------------------------------------------------
# get monthly champion. Use the consolidated data with focus on the current month
# -------------------------------------------------------------------------------
yesterday = date.today() - timedelta(days=1)
y = yesterday.year
m = yesterday.month
startdate = date(y, m, 1).strftime("%Y-%m-%d")  # always the first day of the month


# loop through the monthly-champions-html
html_output = yesterday.strftime("%B-%y") + ','
rank = 0
champions = 0
while rank < len(flights) and champions < 5:
    flight_date = date(int(flights[rank]['flight_date'][6: 8]) + 2000, int(flights[rank]['flight_date'][3: 5]),
                       int(flights[rank]['flight_date'][0: 2]))
    if flight_date > date(y, m, 1):   # everything, in this month is relevant.
        # write out the csv-data
        table_row = flights[rank]['pilot'] + ',' + flights[rank]['flight_date'] + ',' + flights[rank]['distance'] \
                    + ' km,' + flights[rank]['points'] + ' p,' + flights[rank]['flight_type']
        table_row += ',<a href="' + flights[rank]['link'] + '" target="_blank">Details</a>,'
        html_output += table_row
        champions += 1
        delta_date = today - flight_date
        if delta_date.days <= 7:   # everything, newer than 1 week is taken as new.
            new_flights.append(flights[rank]['points'])
    rank += 1
while champions < 5:
    table_row = '-,-,-,-,-,-,'  # just dashes, if there is no flight
    html_output += table_row
    champions += 1
print(html_output)
# read existing champions
champions_file = open('/home/solarmanager/xc_ranking/champions_data.txt', "r")
file_content = champions_file.readline()
if file_content.find(yesterday.strftime("%B-%y")) > 0:  # find the name of the actual month and cut it off
    file_content = str(file_content)[0:file_content.find(yesterday.strftime("%B-%y"))]

# write out status
champions_file = open('/home/solarmanager/xc_ranking/champions_data.txt', 'w')
champions_file.write(file_content + html_output)
champions_file.close()
print("champion ranking created")

# create new-flights-button.
new_flights = list(set(new_flights))  # Number of new flights is in the length of this list
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 42)
img = Image.new("RGB", (960, 100), color=(254, 254, 254, 254))
img1 = ImageDraw.Draw(img)  # image to represent the bottom with the number of new flights
img1.text((160, 24), 'AKTUELLE FLÜGE (NEU: ' + str(len(new_flights)) + ')', (50, 60, 120), font=font)
img.save('/home/solarmanager/xc_ranking/new_flights_button.png')

# send it to DCZO-webserver
session = ftplib.FTP('ftp.dczo.ch', constants.ftp_user, constants.ftp_pw)
file0 = open('/home/solarmanager/xc_ranking/ranking_result.html', 'rb')  # file to send
file1 = open('/home/solarmanager/xc_ranking/new_flights_button.png', 'rb')  # file to send
file2 = open('/home/solarmanager/xc_ranking/champions_data.txt', 'rb')  # file to send
session.storbinary('STOR ranking_result.html', file0)  # send the file
session.storbinary('STOR new_flights_button.png', file1)  # send the file
session.storbinary('STOR champions_data.txt', file2)  # send the file
file0.close()  # close file and FTP
file1.close()
file2.close()
session.quit()
print("files sent to DCZO")
