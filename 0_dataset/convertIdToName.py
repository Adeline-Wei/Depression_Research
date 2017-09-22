sampleOrdinaryIDs = []
with open('sampleOrdinaryIDs') as open_file:
	for line in open_file:
		sampleOrdinaryIDs.append(line.strip())


with open('sampleOrdinaryIDtoName', 'a') as write_file:
	for userId in sampleOrdinaryIDs:
		with open('OrdinaryUsersTweets/' + userId) as open_file:
			name = open_file.readline().strip().split('\t')[1]
			write_file.write('{}\t{}\n'.format(userId, name))



#####################################################################

import random

ordinaryIDs = []
with open('../0_dataset/ordinaryIDs') as open_file:
    for line in open_file.readlines():
        ordinaryIDs.append(line.strip())
sampleOrdinary = random.sample(ordinaryIDs, 150)