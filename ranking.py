# Get Ranking, (c) Thomas Kamps
# parses XCONTEST-html and extracts the first 10 places
from datetime import date
import time
today = date.today()
# Variables
ranking_path = 'ranking.html'  # adapt to file location
max_rank = 10
rank = 0
whole_content = ''
flight_type = ''
html_output = '<p>Stand: ' + today.strftime("%d.%m.%Y") + '<table><tr><td><b>Rang</td><td><b>Pilot</td>'
html_output += '<td><b>Länge</td><td><b>Datum</td><td><b>Aufgabe</td><td><b>Link Xcontest</td></tr>'
# function to get sums out of the status
def get_value(html_string, tag_name, tag_end):
    if html_string.find(tag_name) == -1:
        return ''
    value_start = html_string.find(tag_name)
    value_end = html_string.find(tag_end, value_start)
    return str(html_string)[value_start: value_end]
# Info for the user
print('HTML-Sourcecode expectet in file: <ranking.html>')

# Sample the file to one string
ranking_file = open(ranking_path, 'r', encoding="utf-8")
file_content = ranking_file.readline()
while file_content:
    file_content = ranking_file.readline()
    whole_content += file_content.strip()

while rank < max_rank:
    # We are looking for this: "<tr id="flight"
    if len(get_value(whole_content, '<tr id="flight', "</tr>")) > 10:
        ranking = get_value(whole_content, '<tr id="flight', "</tr>")
        rank += 1
        # cut of the result from the rest
        whole_content = str(whole_content)[whole_content.find('<tr id="flight')+10:len(whole_content)]

        # get the pilot
        pilot = get_value(ranking, '<a class="plt"', '</a')
        pilot_name = str(pilot)[2 + pilot.find('">'):len(pilot)]

        # get the length
        length = get_value(ranking, 'class="km"', '</strong')
        length_km = str(length)[7 + length.find('strong>'):len(length)]

        # get the date
        date_rough = get_value(ranking, 'class="full"', '<em>')
        date = str(date_rough)[1 + date_rough.find('>'):len(date_rough) - 1]

        # get the type
        type_rough = get_value(ranking, 'class="disc', '"><em')
        if str(type_rough)[7 + type_rough.find('title'):10 + type_rough.find('title')] == 'fre':
            flight_type = 'Freie Strecke'
        if str(type_rough)[7 + type_rough.find('title'):10 + type_rough.find('title')] == 'FAI':
            flight_type = 'FAI-Dreieck'
        if str(type_rough)[7 + type_rough.find('title'):10 + type_rough.find('title')] == 'fla':
            flight_type = 'Flaches Dreieck'

        # get the link
        flight_link = get_value(ranking, 'flight detail" href', '><')
        flight_link = str(flight_link)[21:len(flight_link) - 1]

        print(rank, pilot_name, length_km, date, flight_type, flight_link)
        table_row = '<tr><td>' + str(rank) + '</td><td>' + pilot_name + '</td><td>' + length_km + ' km</td><td>'
        table_row += date + '</td><td>' + flight_type + '</td><td><a href="https://www.xcontest.org'
        table_row += flight_link + ' target="_blank">Details</a></td></tr>'
        html_output += table_row
print('HTML-result. To be copied into CMS:')
html_output += '</table>'
print(html_output)
# write out status
result_file = open('ranking_result_' + today.strftime("%d%m%Y") + '.html', 'w')
result_file.write(html_output)
result_file.close()
print('result written to: ranking_result_' + today.strftime("%d%m%Y") + '.html')
# close window after 10 seconds
time.sleep(10)