import sys,os
# get old tweets lib
sys.path.append('GetOldTweets-python/')
import got
import tweepy
import time
from datetime import datetime, timedelta

# consumer_key = 'JJlLNjcvAgJBTmxAqThcQlxTI'
# consumer_secret = 'pG5ZGYhJs8BfTFX13cxcRcTxtHLBXb2CTGEG44G1PpJ4RT3TGJ'
# access_token = '1473637831-7X2s2eeNYlevjxnvcAG4Zw6eY5aORDO2aoqZn8v'
# access_token_secret = 'V1D4mMm8or4yTHmJx0s9ZaTXy2Etsdpql7CZ8tiKsKcNV'

consumer_key = 'PIziw3AXDXIgnJfDJPDeJWLVP'
consumer_secret = 'oAvfoRttcWJQhuTVPFx8ZnSVtmDYpabpqvFxvVrMv7pJzfHpnm'
access_token = '1473637831-pJ30e5bAbOsmCOKSooH0RGi3KRpqxIH6BJ1vmQ2'
access_token_secret = 'UXnKINVjCUO7iY3knQvpPNLv7bhtUCHXFVsuPR4sjRpD5'

count_num = 0

def getUsername(api, userid):
    with open('userInfo','a') as write_file:
        user = api.get_user(userid)
        write_file.write('{0}\t{1}\n'.format(userid, user.screen_name))
    return user.screen_name


def getEachTweet(userID, username, tweet):
    out_format = "{}\t{}\t{}\t{}\n".format(userID, username, str(tweet.date), str(tweet.text.encode('utf-8')))
    return(out_format)
    # Possible entry
    # tweet.id
    # tweet.permalink
    # tweet.username
    # tweet.text
    # tweet.date
    # tweet.retweets
    # tweet.favorites
    # tweet.mentions
    # tweet.hashtags
    # tweet.geo

def getUserIdList():
    userListFilename = sys.argv[1]
    ''' Return user id and their diagnosed time ''' 
    userIds = []
    with open(userListFilename) as open_file:
        for line in open_file.readlines():
            eles = line.split('\t')
            userId = eles[0]
            diagnosedTime = datetime.strptime(eles[3][0:10], '%Y-%m-%d')
            userIds.append((userId, diagnosedTime))
        return userIds

def timeout(STime):
    print('Sleep for ' + str(STime) + ' seconds..')
    time.sleep(STime)
    print('\n\n')

def main():
    #twitter api setup
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    user_list = getUserIdList()
    # Check every user in your list
    for i, id_num_tuple in enumerate(user_list):
        global count_num
        count_num = 0
        userID = id_num_tuple[0]
        diagnosedTime = id_num_tuple[1]
        try:
            username = getUsername(api, userID)
            print('{0}\tUsername: {1}'.format(i, username))
            # print(str(user_list.index(id_num_tuple)+1) + '\t' + username + '\t' + id_num_tuple[1])
        except:
            print('UserID ' + userID + ' is not found on Twitter..')
            continue
#         To show the process start time    
        print(str(datetime.now())[:-7])
        print('Crawling every tweets of ' + username + ' ..')
        # To detect if the file has been collect before
        # If repeat, continue to next one
        out_folder = 'Output'
        if os.path.exists(out_folder + '/' + userID):
            # print('Duplicate user: ' + userID +'\n')
            with open(out_folder + '/' + userID) as open_file:
                last_line = open_file.readlines()[-1].strip().split('\t')
            from_time = str(diagnosedTime - timedelta(days=365*1))[0:10]
            print('Collecting data from {0} to {1}...'.format(from_time[0:10], last_line[2][0:10])) 
            tweetCriteria = got.manager.TweetCriteria().setUsername(username).setSince(from_time).setUntil(last_line[2][0:10])

            # continue
        else:
            # print('{0} diagnosed at {1}'.format(username, diagnosedTime))
            from_time = str(diagnosedTime - timedelta(days=365*1))[0:10]
            until_time = str(diagnosedTime + timedelta(days=30))[0:10]
            print('{0} diagnosed at {1}, crawling from {2}'.format(username, until_time, from_time))
            tweetCriteria = got.manager.TweetCriteria().setUsername(username).setSince(from_time).setUntil(until_time)
            
        # Method to handle the tweet buffer
        # From got.manager.TweetManager.getTweets(tweetCriteria, tweetsToFile, 100)
        def tweetsToFile(tweets):
            # make sure have output folder
            if not os.path.exists(out_folder):
                os.makedirs(out_folder)
                
            output_content = ''
            with open(out_folder + '/' + userID,'a') as output_file:
                for tweet in tweets:
                    output_content += getEachTweet(userID, username, tweet)
                output_file.write(output_content)

            global count_num
            count_num += len(tweets)
            
            # Show how many tweets you have collected, also show the time (You can check the time to decide restart time)
            
            print('{}\tTotal {} tweets in {}/{}\tCurrent oldest tweet {}'.format(str(datetime.now())[:-7], str(count_num), out_folder, userID, tweets[-1].date))
            

        # Weird code here <tab> or not
        got.manager.TweetManager.getTweets(tweetCriteria, tweetsToFile, 100)
        
        print('\n\n')
        # Time out to prevend IP ban
        timeout(count_num/60)

        

if __name__ == '__main__':

    main()
