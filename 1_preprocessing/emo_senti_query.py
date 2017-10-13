# coding: utf-8

import os
import re
import json
import pytz
import requests
import numpy as np
import pandas as pd
import datetime
from EmotionDetection import EmotionDetection


# ## Read Patients
def readPatient(folder, filename):
    # print(folder + filename)
    with open('../0_dataset/diagnosedTweetsPatch0') as open_file:
        diagnosedTimeDict = dict()
        idToNameDict = dict()
        for line in open_file.readlines():
            line = line.strip().split('\t')
            diagnosedTimeDict[line[0]] = datetime.datetime.strptime(line[3], "%Y-%m-%d %H:%M:%S")
            idToNameDict[line[0]] = line[1]
    df = pd.read_csv(folder + filename, sep='\t',header=None,usecols=[0,1,2,3],names=['UserId','ScreenName','Date', 'Text'],quoting=3,error_bad_lines=False,encoding='utf-8').dropna(axis=0, how='any')
    df = df.drop_duplicates(subset='Date', keep='first')
    df = df.set_index('Date')
    df.index = pd.to_datetime(df.index)
    diagnosedTime = diagnosedTimeDict[filename]
    timeDuration = diagnosedTime - datetime.timedelta(days=90)

    df1 = df.loc[str(diagnosedTime):str(timeDuration)]
    if df1.empty:
            df1 = df.loc[str(timeDuration):str(diagnosedTime)]
    return df1


def readOrdinary(folder, filename):
    df = pd.read_csv(folder + filename, sep='\t',header=None,usecols=[0,1,2,3],names=['UserId','ScreenName','Date', 'Text'],quoting=3,error_bad_lines=False,encoding='utf-8').dropna(axis=0, how='any')
    df = df.drop_duplicates(subset='Date', keep='first')
    df = df.set_index('Date')
    df.index = pd.to_datetime(df.index)
    df = df.sort_index(ascending=False)
    newestTime = df.index[0]
    timeDuration = newestTime - datetime.timedelta(days=90)
     
    df1 = df.loc[str(newestTime):str(timeDuration)]
    if df1.empty:
        df1 = df.loc[str(timeDuration):str(newestTime)]

    return df1



def checkFolderFile(folder):
    return os.listdir(folder)


# ## Prepare File

print('\n Reading patient tweets...')
# folder = '../0_dataset/DepressionUsersTweets/Patch0_data/'
folder = '../0_dataset/OrdinaryUsersTweets/'

print(folder)
user_list = checkFolderFile(folder)
user_tweets_list = []
# for name in user_list:
#     user_tweets_list.append(readPatient(folder, name))

for name in user_list:
    try:
        user_tweets_list.append(readOrdinary(folder, name))
    except:
        print(name)
    # break

print(' User Number from tweets folder:' + str(len(user_tweets_list)))


# ## Query Emotion & Sentiment
# function to delete url
def del_url(line):
    return re.sub(r'(https\S+)|(http\S+)|(pic.twitter.com\S+)|(twitter.com/\S+)|(\S+/\S+)', "", line)
    # return re.sub(r'(\S*(\.com).*)|(https?:\/\/.*)', "", line)
# replace tag
def checktag(line): 
    return re.sub(r'\@|\#', "", line)
# Some special character
def checkSpecial(line):
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)
    mystery_patter = re.compile("[( ͡° ͜ʖ)♛∞ღღ∞ω＿⊃／_└＜⌒ヽ､⊕✿◠‿۳˚Д◡ﾉ◕ヮ: ･ﾟ✧●∇◕︵ƪ°͡▿╯︵╯｡]+")
    
    try:
        line = mystery_patter.sub('', line)
    except:
        pass

    line = emoji_pattern.sub('', line)
    return line.replace('♡', '').replace('\"','').replace('“','').replace('”','').replace('…','...').replace('|','').replace('—','-').replace('❤','').replace('️','')

def sendto140(line):
        query_string = '{"data": ['
        # username, date, datetime, content 
        query_string += '{"text": "' + checkSpecial(checktag(del_url(str(line).strip()))) + '"},'

        query_string = query_string[:-1] + ']}'
        try:
            response = requests.post('http://www.sentiment140.com/api/bulkClassifyJson', query_string) # request to server     
            query_result = response.json() # get the response     
            # print page # print the result     
            # query_result = json.loads(page) # parse the result. The result is in JSON format
            return sentiment_dict[int(query_result["data"][0]["polarity"])]
        except:
            print("Fail : "+query_string)
            return sentiment_dict[2]



sentiment_dict = {
                0:-1,
                2: 0,
                4: 1
                }

# Emotion query object
ed = EmotionDetection()


# output_folder = '../0_dataset/DepressionUsersTweets/Patch0_data_PoL/'
output_folder = '../0_dataset/OrdinaryUsersTweets_PoL/'

emptyDataframe = []


for i, user_tweets in enumerate(user_tweets_list):
    if user_tweets.empty == True:
        emptyDataframe.append(user_list[i])
        continue
    user_name = user_tweets['UserId'][0]
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("{0}\tProcessing {1} ({2}/{3})...".format(now, user_name, i+1, len(user_tweets_list)))
    length = len(user_tweets)

    senti_array, emo1_array, emo2_array, amb_array = [], [], [], []

    for line in user_tweets.iterrows():
        if (i+1) % 300 == 0:
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print("{0}\tUser {1}: {2}/{3} tweets finished".format(now, user_name, i+1, len(length)))
        senti_array.append(sendto140(line[1]['Text']))

        emotion_json = ed.get_emotion_json(line[1]['Text'])
        emotion1, ambiguous = emotion_json[u'groups'][0][u'name'], emotion_json[u'ambiguous']

        if len(emotion_json[u'groups']) == 2:
            emotion2 = emotion_json[u'groups'][1][u'name']
        else:
            emotion2 = emotion1
        emo1_array.append(emotion1)
        emo2_array.append(emotion2)
        amb_array.append(ambiguous)


    senti_array, emo1_array, emo2_array, amb_array = np.array(senti_array), np.array(emo1_array), np.array(emo2_array), np.array(amb_array)

    user_tweets['Sentiment'] = np.array(senti_array)
    user_tweets['emo1'] = np.array(emo1_array)
    user_tweets['emo2'] = np.array(emo2_array)
    user_tweets['ambiguous'] = np.array(amb_array)
          
    user_tweets.to_csv(output_folder+str(user_name), header=False, sep='\t')


print('Done!')




# —
# ( ͡° ͜ʖ ͡°)
# ♛
# ∞ღ 
# ღ∞
# /\ /\ 　 (　･ω･) 　 ＿|　⊃／(＿＿_ ／　└-(＿＿＿_／ 　＜⌒／ヽ-､_＿_ 
# ⊕
# (✿◠‿◠✿)
# (۳˚Д˚)۳
# (✿◠‿◠✿)
# (◡‿◡✿)
# (ﾉ◕ヮ◕)ﾉ*: ･ﾟ✧"
# ＼(●⌒∇⌒●)
#  (◕︵◕)
# ƪ(°͡▿▿▿▿▿▿° )͡ƪ
# (╯°□°）╯︵
# (｡ ‿ ｡)
# (✿◠‿◠)
# –



#### 
# 1486340545
# 173935927 (XXXXX)
# 70194445 (XXXXX)
# 1084422662





### ParseError possible malformed input file
# 598134714
# 320596946
# 588455163
# 624199231
# 477388137