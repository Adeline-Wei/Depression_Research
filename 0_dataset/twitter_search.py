import sys, os
sys.path.append('GetOldTweets-python')
import got


sinceDate = '2017-01-01'
untilDate = '2017-06-30'
queryStatement = 'diagnosed mania'	# Tried: depression, mania
tweetCriteria = got.manager.TweetCriteria().setQuerySearch(queryStatement).setSince(sinceDate).setUntil(untilDate).setMaxTweets(0)
print('Getting tweets...')
tweets = got.manager.TweetManager.getTweets(tweetCriteria)
print('Total {} tweets.'.format(len(tweets)))

folders = ['Output']
filename = 'queryTweets_mania_test.csv'
path = ''
for folder in folder:
	path = path + folder + '/' 
path += filename

with open (path, 'a') as open_file:
	print('Writing content...')
	count = 0
	for tweet in tweets:
		count += 1
		if (count % 100) == 0:
			print('Processing {}/{}...'.format(count, len(tweets))) 
		content = '{}\t{}\t{}\n'.format(tweet.text, tweet.author_id, tweet.date)
		open_file.write(content)
