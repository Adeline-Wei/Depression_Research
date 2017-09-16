import sys, os
sys.path.append('GetOldTweets-python')
import got


sinceDate = '2009-01-01'
untilDate = '2011-12-31'
queryStatement = 'i diagnosed depression today'
notExpects = ['anxiety', 'bipolar', 'borderline', 'bpd', 'myself', 'manic']
tweetCriteria = got.manager.TweetCriteria().setQuerySearch(queryStatement).setSince(sinceDate).setUntil(untilDate)
print('Getting tweets...')
tweets = got.manager.TweetManager.getTweets(tweetCriteria)
print('Total {} tweets.'.format(len(tweets)))


filename = 'queryTweets_depression_explict_patch4.csv'

with open (filename, 'a') as open_file:
	print('Writing content...')
	count = 0
	for tweet in tweets:
		count += 1
		if (count % 100) == 0:
			print('Processing {}/{}...'.format(count, len(tweets)))
		continueFlag = False
		for notExpect in notExpects:
			if notExpect in tweet.text.lower():
				continueFlag = True
				break
		if continueFlag:
			continue
		else:
			try:
				content = '{}\t{}\t{}\t{}\t{}\n'.format(tweet.userid, tweet.username, tweet.text, tweet.date, tweet.id)
				open_file.write(content)
			except (AttributeError, UnicodeEncodeError) as e:
				# print(e)
				continue
