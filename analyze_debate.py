import sys
import nltk
from nltk.corpus import stopwords

# Input - transcript .txt file
#       - (optional) candidate to analyze

candidate_key = ''

if len(sys.argv) < 2:
    print('No transcript provided')
    sys.exit()
elif len(sys.argv) == 3:
    candidate_key = sys.argv[2]

top_words = {}

# December 15 debate candidates and moderators

CANDIDATES = {
            'trump':[],
            'cruz':[],
            'carson':[],
            'paul':[],
            'christie':[], 
            'kasich':[],
            'fiorina':[],
            'rubio':[],
            'bush':[]
            }

MODERATORS = {
            'blitzer' : [],
            'hewitt' : [],
            'bash' : []
            }

try:
    fh = open(sys.argv[1], 'r')
except IOError:
    print('File does not exist')
    sys.exit()

# Parse transcript
def parse(data):
    return [n for n in data if n.lower() not in stopwords.words('english') and n.isalnum()]

current_speaker = ''
for line in fh:
    try:
        line = line.encode('ascii','ignore')
    except UnicodeError:
        templine = ''
        for c in list(line):
            try:
                templine += c.encode('ascii','ignore')
            except:
                pass
        line = templine
    data = line.split(':')
    if len(data) < 1:
        pass
    elif len(data) == 2:
        current_speaker = data[0].lower()
        if current_speaker in CANDIDATES.keys():
            if data[1] != '\n':
                CANDIDATES[current_speaker] = CANDIDATES[current_speaker] + parse(nltk.word_tokenize(data[1]))
        elif current_speaker in MODERATORS.keys():
            if data[1] != '\n':
                MODERATORS[current_speaker] = MODERATORS[current_speaker] + parse(nltk.word_tokenize(data[1]))
    elif len(data) == 1 and line != '':
        if current_speaker in CANDIDATES.keys():
            if data[0] != '\n':
                CANDIDATES[current_speaker] = CANDIDATES[current_speaker] + parse(nltk.word_tokenize(data[0]))
        elif current_speaker in MODERATORS.keys():
            if data[0] != '\n':
                MODERATORS[current_speaker] = MODERATORS[current_speaker] + parse(nltk.word_tokenize(data[0]))
    else:
        pass
fh.close()


common_terms = {}
# Create word list
for person in CANDIDATES.keys():
    fdist = nltk.FreqDist(CANDIDATES[person])
    common_terms[person] = fdist

# Print sorted words
#for key in CANDIDATES.keys():
if candidate_key in CANDIDATES.keys():
    common_terms[candidate_key].plot(25, cumulative=False, title=candidate_key)
