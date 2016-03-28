'''
The purpose of this program is to clean json files that are common in the dataset. 
'''

sample = 'C:24:"Vreasy\Models\RoomConfig":1106:{a:5:{i:0;C:18:"Vreasy\Models\Room":170:{a:4:{s:4:"type";s:0:"";s:4:"beds";s:75:"a:1:{i:0;C:17:"Vreasy\Models\Bed":35:{a:1:{s:4:"type";s:10:"Double bed";}}}";s:11:"description";s:7:"Room #5";s:8:"bathroom";b:1;}}i:1;C:18:"Vreasy\Models\Room":170:{a:4:{s:4:"type";s:0:"";s:4:"beds";s:75:"a:1:{i:0;C:17:"Vreasy\Models\Bed":35:{a:1:{s:4:"type";s:10:"Double bed";}}}";s:11:"description";s:7:"Room #4";s:8:"bathroom";b:1;}}i:2;C:18:"Vreasy\Models\Room":170:{a:4:{s:4:"type";s:0:"";s:4:"beds";s:75:"a:1:{i:0;C:17:"Vreasy\Models\Bed":35:{a:1:{s:4:"type";s:10:"Double bed";}}}";s:11:"description";s:7:"Room #3";s:8:"bathroom";b:1;}}i:3;C:18:"Vreasy\Models\Room":170:{a:4:{s:4:"type";s:0:"";s:4:"beds";s:75:"a:1:{i:0;C:17:"Vreasy\Models\Bed":35:{a:1:{s:4:"type";s:10:"Double bed";}}}";s:11:"description";s:7:"Room #2";s:8:"bathroom";b:0;}}i:4;C:18:"Vreasy\Models\Room":240:{a:4:{s:4:"type";s:0:"";s:4:"beds";s:144:"a:2:{i:0;C:17:"Vreasy\Models\Bed":35:{a:1:{s:4:"type";s:10:"Single bed";}}i:1;C:17:"Vreasy\Models\Bed":35:{a:1:{s:4:"type";s:10:"Single bed";}}}";s:11:"description";s:7:"Room #1";s:8:"bathroom";b:0;}}}}'
sample = sample.replace(':', ' ')
sample = sample.replace('{','')
sample = sample.replace('"', '')

'''
This function finds the number of rooms in the listing
'''
def find_number_of_rooms(string):
	number_rooms = ''
	for n in range(0, 40):
		if string[n:n+3] == ' a ':
			number_rooms = float(string[n+3])
	return number_rooms

def parse_bed(string):
	marker = 0
	for n in range(0,len(string)-len('Vreasy\Models\Bed')):
		if string[n:len('Vreasy\Models\Bed')] == 'Vreasy\Models\Bed':
			marker = n
	
	beginning = 0
	end = 0
	for n in range(marker, len(string)):
		if string[n:len('type;s ')] == 'type;s '
			beginning = n + len('type;s ')
		if string[n:len(';}')]
	segment = 

'''
Parses the string to give back final array data. listing 
'''
def find_a_room(string, listing):
	data = []
	segments_with_rooms = []
	last_segment = 0
	for n in range(0,len(string)):
		if string[n:n+19] == 'Vreasy\Models\Room ':
			segments_with_rooms.append(string[last_segment:n])
			n+=19
			last_segment = n
	#add last one
	segments_with_rooms.append(string[last_segment:len(string)])
	#get rid of excess
	segments_with_rooms.pop(0)


	for seg in segments_with_rooms:
		print seg
'''
The main function
'''
def main():
	rooms = find_number_of_rooms(sample)
	room_bits = find_a_room(sample, 2001)

main()


