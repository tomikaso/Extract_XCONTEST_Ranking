# Get Ranking, (c) Thomas Kamps
# parses XCONTEST-html and extracts the first 10 places
# Variables
ranking_path = 'C:/Users/Kunterbunt/Documents/Thomas/DCZO/Ideen/Ranking20240217.html'  # adapt to file location
max_rank = 10
rank = 0
flight_type = ''
html_output = '<table><tr><td><b>Rang</td><td><b>Pilot</td><td><b>Länge</td><td><b>Datum</td><td><b>Aufgabe</td></tr>'


# function to get sums out of the status
def get_value(html_string, tag_name, tag_end):
    if html_string.find(tag_name) == -1:
        return ''
    value_start = html_string.find(tag_name)
    value_end = html_string.find(tag_end, value_start)
    return str(html_string)[value_start: value_end]


# get the HTML-File
ranking_file = open(ranking_path, 'r', encoding="utf-8")
file_content = ranking_file.readline()
while file_content and rank < max_rank:
    file_content = ranking_file.readline()
    # We are looking for this: "<tr id="flight"
    if len(get_value(file_content, '<tr id="flight', "</tr>")) > 10:
        ranking = get_value(file_content, '<tr id="flight', "</tr>")
        rank += 1
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

        print(rank, pilot_name, length_km, date, flight_type)
        table_row = '<tr><td>' + str(rank) + '</td><td>' + pilot_name + '</td><td>' + length_km + ' km</td><td>'
        table_row += date + '</td><td>' + flight_type + '</td></tr>'
        html_output += table_row
print('HTML-result. To be copied into CMS:')
html_output += '</table>'
print(html_output)