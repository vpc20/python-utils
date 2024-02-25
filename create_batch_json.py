import os


# write json file for musescore batch conversion to pdf
def write_json(filename):
    json_filenames = f'''
    {{
    \"in\": \"{filename}.mscz\",
    \"out\": \"{filename}.pdf\"
    }},
    '''
    outf.write(json_filenames)


dirpath = r'C:\Users\vpc\OneDrive\Documents\MuseScore4\Scores'

outf = open('musescore_batch.json', 'w')

outf.write('[')
for dirpath, dirnames, filenames in os.walk(dirpath):
    for filename in filenames:
        write_json(filename)
outf.write(']')

outf.close()
