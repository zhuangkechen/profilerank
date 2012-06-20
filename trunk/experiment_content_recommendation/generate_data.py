import sys
import operator
from math import ceil
import getopt

def get_valid_users_init(input_file_name, min_freq_user):
    """
        Gets the set of users from the input database
    """
    input_file = open(input_file_name, 'r')
    users = {}

    for line in input_file:
        line = line.rstrip()
	vec = line.rsplit(',')
        user = vec[0]
	content = vec[1]
       
        if user not in users:
            users[user] = 1
	else:
            users[user] = users[user] + 1

    input_file.close
    
    num = 0

    for user in users:
        if users[user] < min_freq_user:
	    users[user] = 0
	else:
	    num = num + 1

    return users, num
        
def get_valid_users(input_file_name, tweets, min_freq_user, min_freq_content):
    """
        Gets the set of users from the input database, only tweets in the dict 'tweets' are considered
    """
    input_file = open(input_file_name, 'r')
    users = {}

    for line in input_file:
        line = line.rstrip()
	vec = line.rsplit(',')
        user = vec[0]
	content = vec[1]
       
        if content in tweets and tweets[content] >= min_freq_content:
            if user not in users:
                users[user] = 1
	    else:
                users[user] = users[user] + 1

    input_file.close
    
    num = 0
    for user in users:
        if users[user] < min_freq_user:
	    users[user] = 0
	else:
	    num = num + 1

    return users, num

def get_valid_tweets(input_file_name,users, min_freq_content, min_freq_user):
    """
        Gets the set of tweets from users in the input database
    """
    input_file = open(input_file_name, 'r')
    tweets = {}
    
    for line in input_file:
        line = line.rstrip()
	vec = line.rsplit(',')
        user = vec[0]
	content = vec[1]
       
        if user in users and users[user] >= min_freq_user:
	    if content not in tweets:
	        tweets[content] = 1
	    else:
	        tweets[content] = tweets[content] + 1

    input_file.close
    
    num = 0

    for content in tweets:
        if tweets[content] < min_freq_content:
	    tweets[content] = 0
	else:
	    num = num + 1

    return tweets, num

def generate_data(input_file_name, train_file_name, test_file_name, train_rate, min_freq_content, min_freq_user):
    """
        Generates input data for the content recommendation experiment
    """
    (users,prev_num_users) = get_valid_users_init(input_file_name, min_freq_user)
    (tweets,prev_num_tweets) = get_valid_tweets(input_file_name,users,min_freq_content,min_freq_user)

    num_tweets = 0
    num_users = 0

    #Users and tweets are removed till min_freq_content and min_freq_user hold
    while num_users != prev_num_users or num_tweets != prev_num_tweets:
        num_users = prev_num_users
	num_tweets = prev_num_tweets
        (users,num_users) = get_valid_users(input_file_name, tweets, min_freq_user, min_freq_content)
        (tweets,num_tweets) = get_valid_tweets(input_file_name,users, min_freq_content, min_freq_user)
       
    print num_users
    print num_tweets

    input_file = open(input_file_name, 'r')
    train_file = open(train_file_name, 'w')
    test_file = open(test_file_name, 'w')
    tweet_train = {}
    n = 0
    user_train = {}
    test_data_tmp = {}

    for content in tweets:
        tweet_train[content] = 0
    
    #Getting train tweets
    for line in input_file:
        line = line.rstrip()
	vec = line.rsplit(',')
        user = vec[0]
	content = vec[1]

	if content in tweets and user in users and tweets[content] >= min_freq_content and users[user] >= min_freq_user:
	    if tweet_train[content] < int(ceil(train_rate * tweets[content])):
	        train_file.write(user+","+content+"\n")
		tweet_train[content] = tweet_train[content] + 1
		
		if user in user_train:
		    user_train[user] = user_train[user] + 1
		else:
		    user_train[user] = 1
		    
	    else:
	        test_data_tmp[user+","+content] = 1
	
    #This part guarantees that there is training data for every user in the test file
    #As a consequence, some tweets in the training file may not be in test
    for d in test_data_tmp:
	vec = d.rsplit(',')
        user = vec[0]
	content = vec[1]
        
	if user in user_train and user_train[user] >= min_freq_user:
	    test_file.write(user+","+content+"\n")
    
    train_file.close()
    test_file.close()
    input_file.close()


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg
	    
def main(argv=None):
    if argv is None:
        argv = sys.argv

    try:
        try:
            opts, input_file_name = getopt.getopt(argv[1:], "t:e:r:c:u:h", ["train-file=","test-file=","train-rate=","min-freq-content=","min-freq-user=","help"])
        except getopt.error, msg:
            raise Usage(msg)
 
        train_file_name = "train.csv"
	test_file_name = "test.csv"
	train_rate = 0.5
	min_freq_content = 5
	min_freq_user = 5

        if len(input_file_name) < 1:
	    print "python generate_data.py [-t <train file>] [-e <test file>] [-r <train rate>] [-c <min freq content>] [-u <min freq user>] [input file]"
	    sys.exit()

        for opt,arg in opts:
	    if opt in ('-t', '--train-file'):
                train_file_name = arg
	    
            if opt in ('-e', '--test-file'):
	        test_file_name = arg
        
	    if opt in ('-r', '--train-rate'):
	        train_rate = float(arg)
	
	    if opt in ('-c', '--min-freq-content'):
	        min_freq_content = int(arg)
	    
	    if opt in ('-c', '--min-freq-user'):
	        min_freq_user = int(arg)
	    
	    if opt in ('-h', '--help'):
	        print "python generate_data.py [-t <train file>] [-e <test file>] [-r <train rate>] [-c <min freq content>] [-u <min freq user>] [input file]"
	        sys.exit()

	print "python generate_data.py [-t %s] [-e %s] [-r %lf] [-c %d] [-u %d] [%s]" % (train_file_name,test_file_name,train_rate,min_freq_content,min_freq_user,input_file_name)

        generate_data(input_file_name[0], train_file_name, test_file_name, train_rate, min_freq_content, min_freq_user)

    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

if __name__ == "__main__":
    sys.exit(main())
