import sys
import commands
import getopt

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
        
	if user in users:
	    users[user] = users[user] + 1
	else:
	    users[user] = 1

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
	     
def run_profile_rank(content_file_name,num_iterations,damping_factor,output_prefix,function):
    """
        Runs user recommendation using profilerank
    """
    tmp_file_name = output_prefix+"_profilerank.tmp"
    output_file = open(tmp_file_name,'w')
    
    #Read train users
    users = read_users(content_file_name)
	
    #The model file stores the ouput from profilerank (1 user per file)
    model_file_name = "models_profilerank/"+output_prefix

    #Generates user list for profilerank
    user_list_file_name = output_prefix+"_user_list"
    user_list = open(user_list_file_name, 'w')
    
    for user in users:
        user_list.write(user+"\n")

    user_list.close()

    print "python ../profilerank.py -n %d -d %lf -o %s -a user -l %s -f %s %s" % (num_iterations,damping_factor,model_file_name,user_list_file_name,function,content_file_name)
    
    #Running profilerank
    c = commands.getoutput("python ../profilerank.py -n "+str(num_iterations)+" -d "+str(damping_factor)+" -o "+model_file_name+" -a user -l "+user_list_file_name+" -f "+function+" "+content_file_name)
    print c
	
    for user in users:
        model_file_name = "models_profilerank/"+output_prefix+"_"+str(user)
	
	#Read proximities
        proximities = read_proximities(model_file_name)

        for rec_user in users:
	    if rec_user != user:
	        if rec_user in proximities:
	            score = proximities[rec_user]
	        else:
		    score = 0
	        
		score = score * users[user]
		if score > 0:
		    output_file.write(user+","+rec_user+","+str(score)+"\n")

    output_file.close()
    c = commands.getoutput("rm "+str(user_list_file_name))
    output_file_name = output_prefix+"_profilerank.csv"
    tmp_dir_name = output_prefix+"_profilerank_tmp_dir"
    commands.getoutput("mkdir "+tmp_dir_name)
    commands.getoutput("sort -t, -k3,3gr -T "+tmp_dir_name+" "+tmp_file_name+" > "+output_file_name)
    commands.getoutput("rm "+tmp_file_name)
    commands.getoutput("rm -r "+tmp_dir_name)

def run_cold_start(content_file_name,bootstrap_method,transitivity_method,output_prefix,in_order):
    """
        Runs user recommendation using profilerank
    """
    if in_order is True:
        prefix = str(output_prefix)+"_"+str(bootstrap_method)+"_"+str(transitivity_method)+"_ordered"
        commands.getoutput("python cold_start.py -b "+str(bootstrap_method)+" -t "+str(transitivity_method)+" -o "+str(prefix)+" -r true "+str(content_file_name))
    else:
        prefix = str(output_prefix)+"_"+str(bootstrap_method)+"_"+str(transitivity_method)
        commands.getoutput("python cold_start.py -b "+str(bootstrap_method)+" -t "+str(transitivity_method)+" -o "+str(prefix)+" "+str(content_file_name))

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg
	    
def main(argv=None):
    if argv is None:
        argv = sys.argv

    try:
        try:
            opts, args = getopt.getopt(argv[1:], "n:d:o:f:h", ["num-iterations=","damping-factor=","dist-function=","output=","help"])
        except getopt.error, msg:
            raise Usage(msg)
        
        if len(args) < 1:
	    print "python run.py [-n <num iterations profilerank>] [-d <damping factor profilerank>] [-o <output prefix>] [-f <dist function>] [<content file>]"
	    sys.exit()
	
	content_file_name = args[0]
	num_iterations = 10
	damping_factor = 0.85
	output_prefix = ""
	function = "single"
	cold_start_bootstrap_methods = ["common-content", "adamic-adar"]
	cold_start_transitivity_methods = ["none", "triangles", "squares"]

        for opt,arg in opts:
	    if opt in ('-h', '--help'):
	        print "python run.py [-n <num iterations profilerank>] [-d <damping factor profilerank>] [-o <output prefix>] [<content file>]"
	        sys.exit()
	    
	    if opt in ('-n', '--num-iterations'):
	        num_iterations = int(arg)
	
	    if opt in ('-d', '--damping-factor'):
	        damping_factor = float(arg)
	    
	    if opt in ('-o', '--output'):
	        output_prefix = arg
	    
	    if opt in ('-f', '--dist-function'):
	        function = arg

	print "python run.py [-n %d] [-d %lf] [-o %s] [-f %s] [%s]" % (num_iterations,damping_factor,output_prefix,function,content_file_name)

        #Creating dirs for models
        commands.getoutput("mkdir models_profilerank")

        for b in cold_start_bootstrap_methods:
	    for t in cold_start_transitivity_methods:
	        run_cold_start(content_file_name,b,t,output_prefix, True)
	        run_cold_start(content_file_name,b,t,output_prefix, False)
	
	run_profile_rank(content_file_name,num_iterations,damping_factor,output_prefix,function)
         
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

if __name__ == "__main__":
    sys.exit(main())
