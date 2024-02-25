from datetime import date
import time
today = date.today()
ranking_path = 'club_ranking.html'  # adapt to file location
max_rank = 10
rank = 0
points_sum = 0
whole_content = ''
html_output = '<table><tr><td><b>Rang</td><td><b>Pilot</td><td><b>Punkte</td><td><b>relevant</td></tr>'

# function to get sums out of the status
def get_value(html_string, tag_name, tag_end):
    if html_string.find(tag_name) == -1:
        return ''
    value_start = html_string.find(tag_name)
    value_end = html_string.find(tag_end, value_start)
    return str(html_string)[value_start: value_end]

# Info for the user
print('HTML-Sourcecode expectet in file: <club_ranking.html>')
time.sleep(1)

# Sample the file to one string
ranking_file = open(ranking_path, 'r', encoding="utf-8")
file_content = ranking_file.readline()
while file_content:
    file_content = ranking_file.readline()
    whole_content += file_content.strip()

# parse the content
while rank < max_rank:
    # We are looking for this: class="pilot"
    if len(get_value(whole_content, 'class="pilot"', "</strong>")) > 10:
        ranking = get_value(whole_content, 'class="pilot"', "</strong>")
        rank += 1
        # get the pilot
        pilot = get_value(ranking, '<a class="name"', '<em>')
        pilot_name = str(pilot)[2 + pilot.find('">'):len(pilot)]

        # get the length
        points = str(ranking)[ranking.find('class="pts"')+20:len(ranking)]
        # ranked?
        counting=''
        if ranking.find('not-ranked') == -1:
            counting = 'zählt'
            points_sum += float(points)

        # cut of the result from the rest
        whole_content = str(whole_content)[whole_content.find('class="pilot"')+10:len(whole_content)]
        # get the date
        date_rough = get_value(ranking, 'class="full"', '<em>')
        date = str(date_rough)[1 + date_rough.find('>'):len(date_rough) - 1]
        # create html
        table_row = '<tr><td>' + str(rank) + '</td><td>' + pilot_name + '</td><td>' + points + ' pts</td><td>'
        table_row += counting + '</td></tr>'
        html_output += table_row
html_output = '<p>Stand: ' + today.strftime("%d.%m.%Y") + ' Punkte: ' + str(points_sum) + '</p>' + html_output
print('HTML-result. To be copied into CMS:')
html_output += '</table>'
print(html_output)
# write out status
result_file = open('club_ranking_result_' + today.strftime("%Y%m%d") + '.html', 'w')
result_file.write(html_output)
result_file.close()
print('result written to: club_ranking_result' + today.strftime("%Y%m%d") + '.html')
# close window after 10 seconds
time.sleep(10)
