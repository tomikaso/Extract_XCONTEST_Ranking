# Get Ranking, (c) Thomas Kamps with help of Danilo's code. Many thanks Danilo!!!
# parses XCONTEST-html and extracts the first 10 places
from datetime import date, timedelta
import requests
import ftplib
import constants
from PIL import Image, ImageDraw, ImageFont

# Parameters
RADIUS = 2000
XCONTEST_USER = constants.XC_user
XCONTEST_PASS = constants.XC_password

# Styles
styles = '<style> html {font-family: "brandon-grotesque-n7","brandon-grotesque", sans-serif; font-size: 10pt; ' \
         'background: #eef6fa; color: #4f5a80; } table, td, th, a, p {font-size: 10pt; padding: 4pt;} ' \
         'tr { background-color: aliceblue;} tr:not(:first-child):hover {background-color: skyblue;} ' \
         '.new{background-color: cornsilk;} a:link {color: darkred; text-decoration: none;} </style>'
ranking_path = 'ranking.html'  # adapt to file location
max_rank = 30
rank = 0
number = 0
# Variables
today = date.today()
# today = date(2025, 7, 31)

whole_content = ''
flight_type = ''
html_output = styles + '<a>Stand: ' + today.strftime(
    "%d.%m.%Y") + '</a><table><tr><td><b>Rang</td><td><b>Pilotin / Pilot</td>'
html_output += '<td><b>Distanz</td><td><b>Punkte</td><td><b>Datum</td><td><b>Aufgabe</td><td><b>XContest</td></tr>'


# function to get sums out of the status
def get_value(html_string, tag_name, tag_end):
    if html_string.find(tag_name) == -1:
        return ''
    value_start = html_string.find(tag_name)
    value_end = html_string.find(tag_end, value_start)
    return str(html_string)[value_start: value_end]


# function to query XContest
def query_xcontest(session0: requests.Session, lng0: float, lat0: float, startdt, enddt):
    url = f'https://www.xcontest.org/world/en/flights-search/?filter%5Bpoint%5D={lng0}+{lat0}' \
          f'&filter%5Bradius%5D={RADIUS}&filter%5Bdate_mode%5D=period&filter%5Bdate%5D={startdt}' \
          f'&filter%5Bdate_to%5D={enddt}2024-11&filter%5Bcatg%5D=FAI3&list%5Bsort%5D=pts&list%5Bdir%5D=down'

    print('Request: ', url)
    r = session0.get(url, headers={
        'user-agent': 'dczo_club_ranking_alp_scheidegg',
    })
    return r.text


# get the data and start here
# Authenticate against XContest
session = requests.Session()
auth_response = session.post('https://www.xcontest.org/world/en/', data={
    'login[username]': XCONTEST_USER,
    'login[password]': XCONTEST_PASS,
    'login[persist_login]': 'Y',
})
assert auth_response.status_code == 200, f'Auth failed, status code {auth_response.status_code}'
assert XCONTEST_USER in auth_response.text, 'Auth failed, username not found in auth response body'
# peek Scheidegg-Data
lng = 8.943117
lat = 47.304817

# calculate start-date. the season always begins in October 10th month.
if today.month >= 10:
    y = today.year
else:
    y = today.year - 1
startdate = date(y, 10, 1).strftime("%Y-%m-%d")
enddate = today.strftime("%Y-%m-%d")

print('Start: ', startdate, 'Enddate: ', enddate)

print(f'{lat},{lng}')
try:
    whole_content = query_xcontest(session, lng, lat, startdate, enddate)
except Exception as e:
    # went wrong somehow
    print(f'ERROR: {e}')
print('data-query finished')

# loop through the html
while rank < max_rank and len(get_value(whole_content, '<tr id="flight', "</tr>")) > 10:
    # We are looking for this: "<tr id="flight"
    ranking = get_value(whole_content, '<tr id="flight', "</tr>")
    rank += 1
    # cut of the result from the rest
    whole_content = str(whole_content)[whole_content.find('<tr id="flight') + 10:len(whole_content)]

    # get the pilot
    pilot = get_value(ranking, '<a class="plt"', '</a')
    pilot_name = str(pilot)[2 + pilot.find('">'):len(pilot)]

    # get the length
    length = get_value(ranking, 'class="km"', '</strong')
    length_km = str(length)[7 + length.find('strong>'):len(length)]

    # get the points
    points = get_value(ranking, 'class="pts"', '</strong')
    points_pts = str(points)[7 + points.find('strong>'):len(points)]

    # get the date
    date_rough = get_value(ranking, 'class="full"', '<em>')
    date_str = str(date_rough)[1 + date_rough.find('>'):len(date_rough) - 1]

    # new flight?
    flight_date = date(int(date_str[6: 8]) + 2000, int(date_str[3: 5]), int(date_str[0: 2]))
    delta_date = today - flight_date
    new_flag = ''
    new_tag = ''
    if delta_date.days <= 7:   # everything, newer than 1 week is taken as new.
        new_tag = ' (neu)'
        new_flag = ' class = "new"'
        number = number + 1

    # get the type
    type_rough = get_value(ranking, 'class="disc', '"><em')
    if str(type_rough)[7 + type_rough.find('title'):10 + type_rough.find('title')] == 'fre':
        flight_type = 'Freie Strecke'
    if str(type_rough)[7 + type_rough.find('title'):10 + type_rough.find('title')] == 'FAI':
        flight_type = 'FAI-Dreieck'
    if str(type_rough)[7 + type_rough.find('title'):10 + type_rough.find('title')] == 'fla':
        flight_type = 'Flaches Dreieck'

    # get the link
    flight_link = get_value(ranking, 'flight detail" href', ' >')
    flight_link = str(flight_link)[21:len(flight_link) - 0]

    print(rank, pilot_name, length_km, points_pts, date, flight_type, flight_link)
    # write out the html-code
    table_row = '<tr' + new_flag + '><td>' + str(rank) + new_tag + '</td><td>' + pilot_name + '</td><td>'
    table_row += length_km + ' km</td><td>' + points_pts + ' pts</td><td>'
    table_row += date_str + '</td><td>' + flight_type + '</td><td><a href="https://www.xcontest.org'
    table_row += flight_link + ' target="_blank">Details</a></td></tr>'
    html_output += table_row
html_output += '</table>'
print(html_output)
# write out status
result_file = open('/home/solarmanager/xc_ranking/ranking_result.html', 'w')
result_file.write(html_output)
result_file.close()
print("ranking created")

# ------------------------------------------------------------
# get monthly champion. Query XContest with the current month
# ------------------------------------------------------------
yesterday = date.today() - timedelta(days=1)
y = yesterday.year
m = yesterday.month
startdate = date(y, m, 1).strftime("%Y-%m-%d")  # always the first day of the month
enddate = today.strftime("%Y-%m-%d")  # end date = current data

print('Month-Champions-Start: ', startdate, 'Enddate: ', enddate)

try:
    whole_content = query_xcontest(session, lng, lat, startdate, enddate)
except Exception as e:
    # went wrong somehow
    print(f'ERROR: {e}')
print('data-query finished')

# loop through the monthly-champions-html
html_output = yesterday.strftime("%B") + ','
rank = 0
while rank < 5:
    rank += 1
    if len(get_value(whole_content, '<tr id="flight', "</tr>")) > 10:
        # We are looking for this: "<tr id="flight"
        ranking = get_value(whole_content, '<tr id="flight', "</tr>")
        # cut of the result from the rest
        whole_content = str(whole_content)[whole_content.find('<tr id="flight') + 10:len(whole_content)]

        # get the pilot
        pilot = get_value(ranking, '<a class="plt"', '</a')
        pilot_name = str(pilot)[2 + pilot.find('">'):len(pilot)]

        # get the length
        length = get_value(ranking, 'class="km"', '</strong')
        length_km = str(length)[7 + length.find('strong>'):len(length)]

        # get the points
        points = get_value(ranking, 'class="pts"', '</strong')
        points_pts = str(points)[7 + points.find('strong>'):len(points)]

        # get the date
        date_rough = get_value(ranking, 'class="full"', '<em>')
        date_str = str(date_rough)[1 + date_rough.find('>'):len(date_rough) - 1]

        # new flight?
        flight_date = date(int(date_str[6: 8]) + 2000, int(date_str[3: 5]), int(date_str[0: 2]))
        delta_date = today - flight_date
        if delta_date.days <= 7:   # everything, newer than 1 week is taken as new.
            number = number + 1

        # get the type
        type_rough = get_value(ranking, 'class="disc', '"><em')
        if str(type_rough)[7 + type_rough.find('title'):10 + type_rough.find('title')] == 'fre':
            flight_type = 'STR'
        if str(type_rough)[7 + type_rough.find('title'):10 + type_rough.find('title')] == 'FAI':
            flight_type = 'FAI'
        if str(type_rough)[7 + type_rough.find('title'):10 + type_rough.find('title')] == 'fla':
            flight_type = 'FLD'

        # get the link
        flight_link = get_value(ranking, 'flight detail" href', ' >')
        flight_link = str(flight_link)[21:len(flight_link) - 0]
        print(rank, pilot_name, length_km, points_pts, date_str, flight_type, flight_link)
        # write out the csv-data
        table_row = pilot_name + ',' + date_str + ',' + length_km + ' km,' + points_pts + ' pts,'
        table_row += flight_type + ',<a href="https://www.xcontest.org' + flight_link + ' target="_blank">Details</a>,'
    else:
        table_row = '-,-,-,-,-,-,'  # just dashes, if there is no flight
    html_output += table_row
print(html_output)
# read existing champions
champions_file = open('/home/solarmanager/xc_ranking/champions_data.txt', "r")
file_content = champions_file.readline()
if file_content.find(today.strftime("%B")) > 0:  # find the name of the actual month and cut it off
    file_content = str(file_content)[0:file_content.find(today.strftime("%B"))]

# write out status

champions_file = open('/home/solarmanager/xc_ranking/champions_data.txt', 'w')
# champions_file = open('champions_data.txt', 'w')
champions_file.write(file_content + html_output)
champions_file.close()
print("champion ranking created")

# create new-flights-button. Number of new flights is in 'number'
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 42)
img = Image.new("RGB", (960, 100), color=(254, 254, 254, 254))
img1 = ImageDraw.Draw(img)  # image to represent the bottom with the number of new flights
img1.text((160, 24), 'AKTUELLE FLÜGE (NEU: ' + str(int(number)) + ')', (50, 60, 120), font=font)
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
