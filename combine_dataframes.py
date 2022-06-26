import pandas as pd
import glob, sys, csv, json, os

def clean_csv_dfs_(indir, tag, outdir, stat_dir):
	print("********************Tag:{}***********************".format(tag))
	dfs = [pd.read_csv(file, lineterminator='\n') for file in \
			glob.glob('{}/tweets-search-{}*.csv'.format(indir, tag))]
	if len(dfs)==0:    
		print("No data found.")
		return
	print("tweet dataframes:{}, tweets:{}, combined shape:{}".format(len(dfs), 
		sum([len(df) for df in dfs]), pd.concat(dfs).shape))

	df = pd.concat(dfs)
	df = df[df.apply(lambda tweet: tweet.text.startswith("RT")==False, axis=1 )]
	df['tweetid'] = df.tweetid.astype(str)
	df = df[df.tweetid!='nan']
	df.set_index("tweetid", inplace=True)
	df[~df.index.duplicated(keep='first')]
	df['author_id'] = df.author_id.astype('str')
	print("number of unique tweets: {}".format(len(df)))
	
	df.to_csv('{}/tweets-search-{}.csv'.format(outdir, tag))
	latest_tweet = df[df.index>=df.index.max()].iloc[0]
	
	with open('tweet_count.txt', 'a') as f:
		f.write('tag: {}, count: {}\n'.format(tag, len(df)))
	
	with open('{}/tweet-stat-{}.json'.format(stat_dir, tag), 'w') as fp:
		json.dump(latest_tweet.to_json(), fp)


	dfs = [pd.read_csv(file, lineterminator='\n') for file in \
			glob.glob('{}/users-search-{}*.csv'.format(indir, tag))]
	
	if len(dfs)>0:
		df = pd.concat(dfs)
		df['userid'] = df.userid.astype(str)
		df = df[df.userid!='nan']
		df.set_index('userid', inplace=True)
		df = df[~df.index.duplicated(keep='first')]
		print("number of unique users: {}".format(len(df)))
		df.to_csv('{}/users-search-{}.csv'.format(outdir, tag))

	dfs = [pd.read_csv(file, lineterminator='\n') for file in \
			glob.glob('{}/inc-tweets-search-{}*.csv'.format(indir, tag))]
	if len(dfs)>0:
		df = pd.concat(dfs)
		df['tweetid'] = df.tweetid.astype(str)
		df = df[df.tweetid!='nan']
		df.set_index('tweetid', inplace=True)
		df[~df.index.duplicated(keep='first')]
		print("number of inc. unique tweets: {}".format(len(df)))
		df.to_csv('{}/inc-tweets-search-{}.csv'.format(outdir, tag))

	dfs = [pd.read_csv(file, lineterminator='\n') for file in \
			glob.glob('{}/media-search-{}*.csv'.format(indir, tag))]
	if len(dfs)>0:
		df = pd.concat(dfs)
		df['media_key'] = df.media_key.astype(str)
		df = df[df.media_key!='nan']
		df.set_index('media_key', inplace=True)
		df[~df.index.duplicated(keep='first')]
		df.to_csv('{}/media-search-{}.csv'.format(outdir, tag))

def clean_csv_dfs(indir, outdir, tag_file, stat_dir):
	print('cleaning csv dfs. indir:{}, outdir:{}, tag_file:{}, stat_dir:{}'.format(indir, outdir, tag_file, stat_dir))
	if not os.path.exists(outdir):
        	os.makedirs(outdir)

	tags = set([])
	with open(tag_file) as csv_file:
		reader = csv.reader(csv_file)
		tags = set(list(reader)[0])

	for tag in tags:
		clean_csv_dfs_(indir, tag.strip().lower(), outdir, stat_dir)


def merge_dfs(indir, outdir):
	print('merging dfs')
	tweet_files = glob.glob('{}/tweets-search-*.csv'.format(indir))
	tweet_dfs = []
	for file in tweet_files:
		df= pd.read_csv(file)
		df['search_term'] = file.split('-')[-1][:-4].strip()
		tweet_dfs.append(df)

	tweet_df=pd.concat(tweet_dfs)
	tweet_df = tweet_df[~tweet_df.index.duplicated(keep='first')]
	tweet_df.to_csv('{}/tweets-all.csv'.format(outdir))

	users_files = glob.glob('{}/users-search-*.csv'.format(indir))
	users_dfs = []
	for file in users_files:
		df= pd.read_csv(file)
		df['search_term'] = file.split('-')[-1][:-4].strip()
		users_dfs.append(df)
  
	# pd.concat(users_dfs).to_csv('{}/users-all.csv'.format(outdir))
	users_dfs=pd.concat(users_dfs)
	users_dfs = users_dfs[~users_dfs.index.duplicated(keep='first')]
	users_dfs.to_csv('{}/users-all.csv'.format(outdir))
 
 
 
 
#  def merge_dfs(indir, outdir):
#     	print('merging dfs')
# 	tweet_files = glob.glob('{}/tweets-search-*.pkl'.format(indir))
# 	tweet_dfs = []
# 	for file in tweet_files:
# 		df= pd.read_pickle(file)
# 		df['search_term'] = file.split('-')[-1][:-4].strip()
# 		tweet_dfs.append(df)

# 	tweet_df=pd.concat(tweet_dfs)
# 	tweet_df = tweet_df[~tweet_df.index.duplicated(keep='first')]
# 	tweet_df.to_pickle('{}/tweets-all.pkl'.format(outdir))

# 	users_files = glob.glob('{}/users-search-*.pkl'.format(indir))
# 	users_dfs = []
# 	for file in users_files:
# 		df= pd.read_pickle(file)
# 		df['search_term'] = file.split('-')[-1][:-4].strip()
# 		users_dfs.append(df)
# 	pd.concat(users_dfs).to_pickle('{}/users-all.pkl'.format(outdir))