# Command line arguments for filename, output directory, and summary index
input_file = sys.argv[1]
output_dir = sys.argv[3]
summary_index = sys.argv[2]

# Initial input initialization
content = open(fname).read()
fname = getFilename(fname)

ext = ext+"/"+str(summary_index)

if not os.path.exists(ext):
    os.makedirs(ext)

soup = BeautifulSoup(content,'lxml')

basic = []
for links in soup.find_all("dependencies"):
    if links.get("type") == "enhanced-dependencies":
        basic.append(links)

parse = []
for links in soup.find_all("parse"):
    parse.append(links)

tokens = soup.find_all("tokens")

###################################################################################################
# Processing
###################################################################################################

sentence_segmentations = []
dep_sentences = get_depparse(basic)

# Insert write logs?

# Variable Declaration. Check usage

# segments = {}
idseg = {}
# count
lists_nodes = {}
segment_set = {}

output = open(ext+'/'+fname+".segs", 'w')
