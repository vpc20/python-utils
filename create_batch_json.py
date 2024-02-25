import os

#
# def list_dir_recursive(path):
#     try:
#         dir_list = os.listdir(path)
#     except WindowsError:
#         pass
#
#     for dir_entry in dir_list:
#         complete_dir_entry = join(path, dir_entry)
#         if isdir(complete_dir_entry):
#             list_dir_recursive(complete_dir_entry)
#         else:
#             print(complete_dir_entry)  # print filenames

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
