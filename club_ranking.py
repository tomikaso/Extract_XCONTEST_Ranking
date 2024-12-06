from datetime import date
import ftplib
import constants
import requests
today = date.today()
max_rank = 20
rank = 0
points_sum = 0
whole_content = ''
# Styles
styles = '<style> html {font-family: "brandon-grotesque-n7","brandon-grotesque", sans-serif; font-size: 10pt; ' \
         'background: #eef6fa; color: #4f5a80; } table, td, th, a, p {font-size: 10pt; padding: 4pt;} ' \
         'tr { background-color: aliceblue;} tr:not(:first-child):hover {background-color: skyblue;} ' \
         '.new{background-color: cornsilk;} a:link {color: darkred; text-decoration: none;} </style>'
html_output = '<table><tr><td><b>Rang</td><td><b>Pilotin / Pilot</td><td><b>Punkte</td><td><b>relevant</td>' \
         '<td><b>Details</td></tr>'
url = 'https://www.xcontest.org/switzerland/en/ranking-pg-club:1383'
# function to get sums out of the status
def get_value(html_string, tag_name, tag_end):
    if html_string.find(tag_name) == -1:
        return ''
    value_start = html_string.find(tag_name)
    value_end = html_string.find(tag_end, value_start)
    return str(html_string)[value_start: value_end]

# try to get the data
session = requests.Session()
r = session.get(url, headers={'user-agent': 'dczo_club_ranking_alp_scheidegg'})
whole_content = r.text

print('Call response: ', whole_content)

# parse the content
while rank < max_rank and len(get_value(whole_content, 'class="pilot"', "</strong>")) > 10:
    # We are looking for this: class="pilot"
    ranking = get_value(whole_content, 'class="pilot"', "</strong>")
    rank += 1
    # get the pilot
    pilot = get_value(ranking, '<a class="name"', '<em>')
    pilot_name = str(pilot)[2 + pilot.find('">'):len(pilot)]
    pilot_name = pilot_name.strip()

    # get the link to the pilot
    pilot_link = 'https://www.xcontest.org/' + str(pilot)[7 + pilot.find('href='):pilot.find('">')]
    print ('Pilot-Link: ', pilot_link)
# get the length
    points = str(ranking)[ranking.find('class="pts"')+20:len(ranking)]
    # ranked?
    counting = ''
    new_flag = ''
    if ranking.find('not-ranked') == -1:
        counting = 'zählt'
        new_flag = ' class = "new"'
        points_sum += float(points)

    # cut of the result from the rest
    whole_content = str(whole_content)[whole_content.find('class="pilot"')+10:len(whole_content)]
    # get the date
    date_rough = get_value(ranking, 'class="full"', '<em>')
    date = str(date_rough)[1 + date_rough.find('>'):len(date_rough) - 1]
    # create html
    table_row = '<tr' + new_flag + '><td>' + str(rank) + '</td><td>' + pilot_name + '</td><td>' + points
    table_row += ' pts</td><td>' + counting + '</td><td><a href="' + pilot_link + '" target="_blank">Flüge '
    table_row += str(pilot_name)[0:pilot_name.find(' ')] + '</a></td></tr>'
    html_output += table_row
html_output = styles + '<p>Stand: ' + today.strftime("%d.%m.%Y") + ' Punkte: ' + str(round(points_sum, 2)) + '</p>' \
              + html_output + '</table>'
# write out status
result_file = open('/home/solarmanager/xc_ranking/club_ranking.html', 'w', encoding='utf8')
result_file.write(html_output)
result_file.close()
print("ranking created")

# send it to DCZO-webserver
session = ftplib.FTP('ftp.dczo.ch', constants.ftp_user, constants.ftp_pw)
file = open('/home/solarmanager/xc_ranking/club_ranking.html', 'rb')  # file to send
session.storbinary('STOR club_ranking.html', file)  # send the file
file.close()  # close file and FTP
session.quit()
print('result written to: club_ranking.html')

