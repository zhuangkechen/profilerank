import sys
import commands
import getopt

def read_tweets_users(test_file_name):
    """
        Gets test data for evaluation
    """
    test_file = open(test_file_name, 'r')
    test_data = {}
    num = 0
    
    for line in test_file:
        line = line.rstrip()
        vec = line.rsplit(',')
	user = vec[0]
	content = vec[1]

	if user in test_data:
	    test_data[user][content] = True
	else:
	    test_data[user] = {}
	    test_data[user][content] = True

	num = num + 1

    test_file.close()

    return test_data, num

def read_users(input_file_name):
    """
        Gets set of users from the input file
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

    return users

def read_tweets(input_file_name):
    """
        Gets set of tweets from the input file
    """
    input_file = open(input_file_name, 'r')
    tweets = {}
    
    for line in input_file:
        line = line.rstrip()
        vec = line.rsplit(',')
	user = vec[0]
        tweet = vec[1]

	if tweet not in tweets:
            tweets[tweet] = user

    input_file.close()

    return tweets

def read_retweets_user(input_file_name,USER):
    """
        Gets set of retweets from a user
    """
    input_file = open(input_file_name, 'r')
    retweets = {}
    tweets = {}

    for line in input_file:
        line = line.rstrip()
        vec = line.rsplit(',')
        user = vec[0]
	content = vec[1]
        
	if content not in tweets:
	    tweets[content] = 1
	else:
	    if user == USER:
	        retweets[content] = user

    input_file.close()

    return retweets

def read_tweets_user(input_file_name,USER):
    """
        Gets set of tweets (and retweets) from a user
    """
    input_file = open(input_file_name, 'r')
    tweets = {}

    for line in input_file:
        line = line.rstrip()
        vec = line.rsplit(',')
        user = vec[0]
	content = vec[1]
        
	if user == USER:
	    tweets[content] = user

    input_file.close()

    return tweets

def read_proximities(input_file_name):
    """
        Read proximities given by profilerank
    """
    input_file = open(input_file_name, 'r')
    proximities = {}
    
    for line in input_file:
        line = line.rstrip()
        vec = line.rsplit(',')
        user = vec[0]
	proximity = vec[1]

        proximities[user] = float(proximity)

    input_file.close()

    return proximities
	     
def read_proximities_my_media_lite(line):
    """
        Read proximities based on recommendations from my media lite
    """
    proximities = {}
    
    vec_user = line.rsplit()
    proximity_values = vec_user[1]
    
    if proximity_values != "[]":
        proximity_values = proximity_values.replace('[','')
        proximities_values = proximity_values.replace(']','')
        proximities_vec = proximities_values.split(',')

        for i in range(0, len(proximities_vec)):
	    pair = proximities_vec[i].split(':')
	    content = pair[0]
	    value = pair[1]
	    proximities[content] = float(value)

    return proximities
    
def create_user_file_name(train_users_file_name,train_file_name):
    """
        Creates a file with the list of users from train_file_name
    """
    train_users_file = open(train_users_file_name, 'w')
    train_file = open(train_file_name, 'r')
    users = {}

    for line in train_file:
        line = line.rstrip()
        vec = line.rsplit(',')
        user = vec[0]
        
	users[user] = 1

    for user in users:
        train_users_file.write(user+"\n")

    train_users_file.close()
    train_file.close()
    
def create_train_file_mml(train_file_mml_name,train_file_name):
    """
        Creates train file for my_media_lite. The original author is not included in the
	training file because it does not make sense for collaborative filtering. Otherwise,
	it would recommend content from the retweeter to the source of a given tweet.
    """
    input_file = open(train_file_name, 'r')
    train_file_mml = open(train_file_mml_name, 'w')

    tweets = {}

    for line in input_file:
        line = line.rstrip()
        vec = line.rsplit(',')
        tweet = vec[1]

	if tweet not in tweets:
            tweets[tweet] = 1
	else:
	    train_file_mml.write(line+"\n")

    input_file.close()
    train_file_mml.close()

def generate_my_media_lite_input_files(train_file_name,test_file_name,output_prefix):
    """
        Generates the input files required by my_media_lite
    """
    #Create file with training users
    train_users_file_name = output_prefix+"_users_mml.txt"
    create_user_file_name(train_users_file_name,test_file_name)
    
    #Create file with training data
    train_file_mml_name = output_prefix+"_train_mml.csv"
    create_train_file_mml(train_file_mml_name,train_file_name)
   
def remove_my_media_lite_files(output_prefix):
    """
        Removes the input files required by my_media_lite
    """
    #removing temporary files
    train_users_file_name = output_prefix+"_users_mml.txt"
    train_file_mml_name = output_prefix+"_train_mml.csv"
    commands.getoutput("rm "+train_users_file_name+" "+train_file_mml_name)

def run_my_media_lite(method,train_file_name,output_prefix):
    """
        Runs tweet recommendation using 'method' from the my_media_lite library
    """
    #Create file with training users
    train_users_file_name = output_prefix+"_users_mml.txt"
    
    #Create file with training data
    train_file_mml_name = output_prefix+"_train_mml.csv"
   
    #The model file stores the ouput from my media lite
    model_file_name = "models_mml/"+output_prefix+"_"+method
   
#    print "item_recommendation --training-file=%s --test-users=%s --recommender=%s --prediction-file=%s" % (train_file_mml_name,train_users_file_name,method,model_file_name)
#    print "mono-2.10 ../../MyMediaLite-3.0/bin/item_recommendation --training-file=%s --test-users=%s --recommender=%s --prediction-file=%s" % (train_file_mml_name,train_users_file_name,method,model_file_name)
        
    #Running my media lite
#    commands.getoutput("mono-2.10 ../../MyMediaLite-3.0/bin/item_recommendation --training-file="+train_file_mml_name+" --test-users="+train_users_file_name+" --recommender="+method+" --prediction-file="+model_file_name)
    commands.getoutput("item_recommendation --training-file="+train_file_mml_name+" --test-users="+train_users_file_name+" --recommender="+method+" --prediction-file="+model_file_name)
    
    input_file = open(model_file_name, 'r')
	
    #Read tweets from user in the train file
    (train_tweets_users,num) = read_tweets_users(train_file_name) 
    
    tmp_file_name = output_prefix+"_"+method+".tmp"
    output_file = open(tmp_file_name,'w')

    train_tweets = read_tweets(train_file_name)
    
    #Processing output from my media lite
    for line in input_file:
        line = line.rstrip()
        
	vec_user = line.rsplit()
	user = vec_user[0]
   
	#Read proximities
	proximities = read_proximities_my_media_lite(line)

	for tweet in train_tweets:
	    if tweet not in train_tweets_users[user]:
	        if tweet in proximities:
	            score = proximities[tweet]
	        else:
		    score = 0

	        if score > 0:
		    output_file.write(user+","+tweet+","+str(score)+"\n")

    output_file.close()


    #Sorting the output file
    output_file_name = output_prefix+"_"+ method + ".csv"
    tmp_dir_name = output_prefix+"_tmp_dir"
    commands.getoutput("mkdir "+tmp_dir_name)
    commands.getoutput("sort -t, -k3,3gr -T "+tmp_dir_name+" "+tmp_file_name+" > "+output_file_name)
    commands.getoutput("rm "+tmp_file_name)
    commands.getoutput("rm -r "+tmp_dir_name)

def run_profile_rank(train_file_name,test_file_name,num_iterations,damping_factor,output_prefix,function):
    """
        Runs tweet recommendation using profilerank
    """
    user_list_file_name = output_prefix+"_user_list.tmp"
    user_list = open(user_list_file_name, 'w')
    
    #Read train users
    test_users = read_users(test_file_name)
    train_users = read_users(train_file_name)
        
    #The model file stores the ouput from profilerank (1 user per file)
    model_file_name = "models_profilerank/"+output_prefix

    #Read train tweets
    train_tweets = read_tweets(train_file_name)
	
    (train_tweets_users,num) = read_tweets_users(train_file_name)

    for user in test_users:
        user_list.write(user+"\n")

    user_list.close()

#    print "python ../profilerank.py -n %d -d %lf -o %s -a content -l %s -f %s %s" % (num_iterations,damping_factor,model_file_name,user_list_file_name,function,train_file_name)
    commands.getoutput("python ../profilerank.py -n "+str(num_iterations)+" -d "+str(damping_factor)+" -o "+model_file_name+" -a content -l "+user_list_file_name+" -f "+function+" "+train_file_name)
    
    tmp_file_name = output_prefix+"_profilerank.tmp"
    output_file = open(tmp_file_name,'w')
	
    for user in test_users:
	#Read tweets from user in the train file
        model_file_name = "models_profilerank/"+output_prefix+"_"+str(user)

	#Read proximities
        proximities = read_proximities(model_file_name)

        for tweet in train_tweets:
	    if tweet not in train_tweets_users[user]:
	        if tweet in proximities:
	            score = proximities[tweet]
	        else:
		    score = 0
		
		score = score * float(train_users[user])

		if score > 0:
		    output_file.write(user+","+tweet+","+str(score)+"\n")

    output_file.close()
    commands.getoutput("rm "+str(user_list_file_name))
    
    #Sorting the output file
    output_file_name = output_prefix+"_profilerank.csv"
    tmp_dir_name = output_prefix+"_tmp_dir"
    commands.getoutput("mkdir "+tmp_dir_name)
    commands.getoutput("sort -t, -k3,3gr -T "+tmp_dir_name+" "+tmp_file_name+" > "+output_file_name)
    commands.getoutput("rm "+tmp_file_name)
    commands.getoutput("rm -r "+tmp_dir_name)

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg
	    
def main(argv=None):
    if argv is None:
        argv = sys.argv

    try:
        try:
            opts, args = getopt.getopt(argv[1:], "n:d:o:f:hs", ["num-iterations=","damping-factor=","dist-function=","output=","help","silent"])
        except getopt.error, msg:
            raise Usage(msg)
        
	my_media_lite_methods = ["BPRMF", "Random", "UserKNN", "WRMF", "MostPopular", "WeightedItemKNN", "WeightedUserKNN", "SoftMarginRankingMF", "WeightedBPRMF"]

        if len(args) < 2:
	    print "python run.py [-n <num iterations profilerank>] [-d <damping factor profilerank>] [-o <output prefix>] [-f <dist function>] [<train file>] [<test file>]"
	    sys.exit()
	
	train_file_name = args[0]
	test_file_name = args[1]
	num_iterations = 10
	damping_factor = 0.85
	output_prefix = ""
	function = "single"
	silent = False

        for opt,arg in opts:
	    if opt in ('-h', '--help'):
	        print "python run.py [-n <num iterations profilerank>] [-d <damping factor profilerank>] [-o <output prefix>] [<train file>] [<test file>]"
	        sys.exit()
	    
	    if opt in ('-n', '--num-iterations'):
	        num_iterations = int(arg)
	
	    if opt in ('-d', '--damping-factor'):
	        damping_factor = float(arg)
	    
	    if opt in ('-o', '--output'):
	        output_prefix = arg
	    
	    if opt in ('-f', '--dist-function'):
	        function = arg
	    
	    if opt in ('-s', '--silent'):
	        silent = True
        
	if silent is False:
	    print "python run.py [-n %d] [-d %lf] [-o %s] [-f %s] [%s] [%s]" % (num_iterations,damping_factor,output_prefix,function,train_file_name,test_file_name)

        #Creating dirs for models
        commands.getoutput("mkdir models_mml models_profilerank")

        #Creating input files for my_media_lite methods
	generate_my_media_lite_input_files(train_file_name,test_file_name,output_prefix)
	
	for m in my_media_lite_methods:
	    run_my_media_lite(m, train_file_name,output_prefix)
        
	#Removing input files for my_media_lite methods
        remove_my_media_lite_files(output_prefix)

        run_profile_rank(train_file_name,test_file_name,num_iterations,damping_factor,output_prefix,function)
         
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

if __name__ == "__main__":
    sys.exit(main())
