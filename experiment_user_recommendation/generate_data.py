import sys
from math import ceil
import getopt
import random

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
       
        if user not in users:
            users[user] = 1
	else:
            users[user] = users[user] + 1

    input_file.close()
    
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

    input_file.close()
    
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

    input_file.close()
    
    num = 0

    for content in tweets:
        if tweets[content] < min_freq_content:
	    tweets[content] = 0
	else:
	    num = num + 1

    return tweets, num
    
def random_users(users, num_users, min_freq_user):
    """
        Selects num_users users at random
    """
    selected = {}
    n = 0
    user_list = []

    for user in users:
        if users[user] >= min_freq_user:
            user_list.append(user)

    while n < num_users and n < len(user_list):
        i = int(ceil(random.uniform(0,len(user_list)-1)))
	if user_list[i] not in selected:
	    selected[user_list[i]] = True
	    n = n + 1

	    if n % 10 == 0:
	        print "%d vertices selected" % (n)
    
    return selected

def generate_data(input_content_file_name, input_network_file_name, content_file_name, network_file_name, min_freq_content, min_freq_user):
    """
        Generates input data for the user recommendation experiment
    """
    (users,prev_num_users) = get_valid_users_init(input_content_file_name, min_freq_user)
    (tweets,prev_num_tweets) = get_valid_tweets(input_content_file_name,users,min_freq_content,min_freq_user)

    num_tweets = 0
    num_users = 0

    #Users and tweets are removed till min_freq_content and min_freq_user hold
    while num_users != prev_num_users or num_tweets != prev_num_tweets:
        prev_num_users = num_users
	prev_num_tweets = num_tweets
        (users,num_users) = get_valid_users(input_content_file_name, tweets, min_freq_user, min_freq_content)
        (tweets,num_tweets) = get_valid_tweets(input_content_file_name,users, min_freq_content, min_freq_user)
       
        #print num_users
        #print num_tweets
	#print

    input_content_file = open(input_content_file_name, 'r')
    content_file = open(content_file_name, 'w')
    
    #Generating content file
    for line in input_content_file:
        line = line.rstrip()
	vec = line.rsplit(',')
        user = vec[0]
	content = vec[1]

	if content in tweets and user in users and tweets[content] >= min_freq_content and users[user] >= min_freq_user:
	    content_file.write(user+","+content+"\n")

    content_file.close()

    input_content_file.close()
    input_network_file = open(input_network_file_name, 'r')
    network_file = open(network_file_name, 'w')
    
    #Generating network data, only the followees of selected users are included
    for line in input_network_file:
        line = line.rstrip()
	vec = line.rsplit(',')

	if vec[0] in users and users[vec[0]] >= min_freq_user and vec[1] in users and users[vec[1]] >= min_freq_user:
            network_file.write(vec[0]+","+vec[1]+"\n")
    
    network_file.close()
    input_network_file.close()


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg
	    
def main(argv=None):
    if argv is None:
        argv = sys.argv

    try:
        try:
            opts, input_file_name = getopt.getopt(argv[1:], "c:n:t:u:hs", ["content-file=","network-file=","min-freq-content=","min-freq-user=","help","silent"])
        except getopt.error, msg:
            raise Usage(msg)
 
        content_file_name = "content.csv"
	network_file_name = "network.csv"
	min_freq_content = 10
	min_freq_user = 10
	silent = False

        if len(input_file_name) < 2:
	    print "python generate_data.py [-c <content file>] [-n <network file>] [-t <min freq content>] [-u <min freq user>] [input content file] [input network file]"
	    sys.exit()

        for opt,arg in opts:
	    if opt in ('-c', '--content-file'):
                content_file_name = arg
	    
            if opt in ('-n', '--network-file'):
	        network_file_name = arg
        
	    if opt in ('-t', '--min-freq-content'):
	        min_freq_content = int(arg)
	    
	    if opt in ('-u', '--min-freq-user'):
	        min_freq_user = int(arg)
	    
	    if opt in ('-s', '--silent'):
	        silent = True
	    
	    if opt in ('-h', '--help'):
	        print "python generate_data.py [-c <content file>] [-n <network file>] [-t <min freq content>] [-u <min freq user>] [input content file] [input network file]"
	        sys.exit()

        if silent is False:
	    print "python generate_data.py [-c %s] [-n %s] [-t %d] [-u %d] [%s] [%s]" % (content_file_name, network_file_name, min_freq_content, min_freq_user, input_file_name[0], input_file_name[1])

        generate_data(input_file_name[0], input_file_name[1], content_file_name, network_file_name, min_freq_content, min_freq_user)

    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

if __name__ == "__main__":
    sys.exit(main())
