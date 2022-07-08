'''
code to prepare datasets
'''
import glob, sys,os, re, itertools
from tqdm import tqdm
sys.path.append('helpers/')
from tweetokenize import *
import text_processing
from constants import *
import spacy
lemmatizer = spacy.load('en_core_web_sm')
curdir = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
from nltk.corpus import stopwords
nltk_stopwords = set(stopwords.words('english'))
profile_stopwords = set([line.strip() for line in open(os.path.join(curdir, 'stopwords-twitter-profile.txt'))])
topic_stopwords = set([line.strip() for line in open(os.path.join(curdir, 'stopwords-twitter-topic.txt'))])
senti_stopwords = set([line.strip() for line in open(os.path.join(curdir, 'stopwords-en-senti.txt'))])
profile_stopwords.update(set(nltk_stopwords))
topic_stopwords.update(set(nltk_stopwords))

tqdm.pandas()

def detect_profile_lang(lang1, lang2, lang3):
	if lang1==lang2:
		return lang1
	if lang1==lang3:
		return lang1
	if lang2==lang3:
		return lang2
	return 'NA'


def combine_dfs(src_path, dest_path):
	'''
	Combine tweet, user, etc. dataframes
	'''

	print('combining user dataframes...')	
	files = glob.glob(src_path+'/users-search-*.pkl')

	all_df=[]
	for i in tqdm(range(len(files))):
		df = pd.read_pickle(files[i])
		df.reset_index(inplace=True)
		df.set_index("userid", inplace=True)
		df[~df.index.duplicated(keep='first')]
		df['search_term'] =  os.path.basename(file[i]).split('.')[0].split('-')[-1]
		all_df.append(df)

	all_df = pd.concat(all_df)
	all_df.to_pickle(dest_path+'/ed-users-all.pkl')

	print('combining tweet dataframes...')	
	files = glob.glob(src_path+'/tweets-search-*.pkl')

	all_df=[]
	for i in tqdm(range(len(files))):
		df = pd.read_pickle(files[i])
		df.reset_index(inplace=True)
		df.set_index("tweetid", inplace=True)
		df[~df.index.duplicated(keep='first')]
		df = df[df.apply(lambda tweet: tweet.text.startswith("RT")==False, axis=1 )]
		df['search_term'] =  os.path.basename(file[i]).split('.')[0].split('-')[-1]
		all_df.append(df)

	all_df = pd.concat(all_df)
	all_df.to_pickle(dest_path+'/ed-tweets-all.pkl')

def preprocess_profile_desc(profile, lemmatize=False):
	# Remove all the special characters
    profile = re.sub(r'\W', ' ', str(profile))
    # Remove all numbers
    profile = re.sub(r"^\d+\s|\s\d+\s|\s\d+$", " ", profile)


    if lemmatize:
    	profile = ' '.join([w.lemma_.strip() for w in lemmatizer(profile)])

    tokens = [word.strip() for word in profile.lower().split() \
    				 if word not in profile_stopwords and len(word)>2]

    return ' '.join(tokens)

'''custom tokenizer for sentiment analysis that removes @mentions and urls'''
senti_tokenizer = Tokenizer(usernames="", urls='', hashtags=False, phonenumbers='', 
                times='', numbers='', ignorequotes=False, ignorestopwords=False, lowercase=True) 

topic_tokenizer = Tokenizer(usernames="username", urls='', hashtags=False, phonenumbers='', 
                times='', numbers='', ignorequotes=False, ignorestopwords=False, lowercase=True) 

def preprocess_tweet_topic(tweet, lemmatize=True, tokenizer = topic_tokenizer):
	# tokenize using tweetokenizer 
	tokens = tokenizer.tokenize(tweet)
	#replace contractions: https://en.wikipedia.org/wiki/Contraction_%28grammar%29
	tokens = [contractions_dict[word] if word in contractions_dict else word for word in tokens] 
	#contractions replacement can create multiple word
	tokens = list(itertools.chain(*[token.strip().split(' ') for token in tokens])) 

	# Remove remaining special characters
	tweet = re.sub(r'\W', ' ', ' '.join(tokens))

	# remove stopwords
	tweet = ' '.join([word.lower() for word in tweet.split() if word not in topic_stopwords and len(word)>2])

	if lemmatize:
		tweet = ' '.join([w.lemma_.strip() for w in lemmatizer(tweet)])
	return tweet

def preprocess_tweet_senti(tweet, lemmatize=True, tokenizer = senti_tokenizer):
	# tokenize using tweetokenizer 
	tokens = tokenizer.tokenize(tweet)
	# replace emoticons, source: https://en.wikipedia.org/wiki/List_of_emoticons
	tokens = [smileys_dict[word] if word in smileys_dict else word for word in tokens] 
	#replace contractions: https://en.wikipedia.org/wiki/Contraction_%28grammar%29
	tokens = [contractions_dict[word] if word in contractions_dict else word for word in tokens] 
	#contractions replacement can create multiple word
	tokens = list(itertools.chain(*[token.strip().split(' ') for token in tokens])) 

	# Remove remaining special characters
	tweet = re.sub(r'\W', ' ', ' '.join(tokens))

	# remove stopwords
	tweet = ' '.join([word.lower() for word in tweet.split() if word not in senti_stopwords and len(word)>1])
	

	if lemmatize:
		tweet = ' '.join([w.lemma_.strip() for w in lemmatizer(tweet)])
	return tweet

def preprocess_user_df(infile, outfile):
	user_df = pd.read_pickle(infile)

	user_df['profile_desc_clean']= user_df.progress_apply(lambda row: 
		preprocess_profile_desc(row.profile_desc, lemmatize=True)\
		 if isinstance(row.profile_desc, str) else '', axis=1)
	print('detecting profile language...')
	user_df['lang1'] = user_df.progress_apply(lambda row: text_processing.detect_lang(row.profile_desc_clean, detector='langid') \
									if len(row.profile_desc_clean)>3 else 'NA', axis=1)
	user_df['lang2'] = user_df.progress_apply(lambda row: text_processing.detect_lang(row.profile_desc_clean, detector='fasttext') \
									if len(row.profile_desc_clean)>3 else 'NA', axis=1)
	user_df['lang3'] = user_df.progress_apply(lambda row: text_processing.detect_lang(row.profile_desc_clean, detector='cld3') \
									if len(row.profile_desc_clean)>3 else 'NA', axis=1)
	user_df['profile_lang'] = user_df.progress_apply(lambda row: detect_profile_lang(row.lang1, row.lang2, row.lang3), axis=1)
	print('saving dataframe...')
	user_df.to_pickle(outfile)
	print('done')

def write_user_profile_des(infile, outfile, append=False):
	user_df = pd.read_pickle(infile)
	mode = 'a' if append else 'w'
	with open(outfile, mode) as file:
		user_df.progress_apply(lambda row: file.write(row.profile_desc_clean+'\n'), axis=1)
		file.close()