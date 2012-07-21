import sys
import commands
import getopt
import math

def read_users(input_file_name):
    """
        Gets set of users and their tweets from the input file
    """
    input_file = open(input_file_name, 'r')
    users = {}
    i = 0
    for line in input_file:
        line = line.rstrip()
        vec = line.rsplit(',')
        user = vec[0]
	content = vec[1]
        
	if user in users:
	    users[user][content] = i
	else:
	    users[user] = {}
	    users[user][content] = i

	i = i + 1

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
        tweet = vec[1]

	if tweet not in tweets:
            tweets[tweet] = 1
	else:
            tweets[tweet] = tweets[tweet] + 1

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
    i = 0

    for line in input_file:
        line = line.rstrip()
        vec = line.rsplit(',')
        user = vec[0]
	content = vec[1]
        
	if user == USER:
	    tweets[content] = i
	
	i = i + 1

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
	user = vec[1]
	proximity = vec[2]
	     
	proximities[user] = float(proximity)
	     
    input_file.close()
    
    return proximities

def compute_common_content(USER, users, in_order):
    """
        Computes the proximity between USER and the remaining users as the number of common content
    """
    proximities = {}
    
    for user in users:
        common_content = 0
        
	if user != USER:
	    for tweet in users[USER]:
	        if in_order:
	            if tweet in users[user] and users[user][tweet] > users[USER][tweet]:
		        common_content = common_content + 1
		else:
	            if tweet in users[user]:
		        common_content = common_content + 1
	    proximities[user] = common_content

    return proximities
    
def compute_adamic_adar(USER, users, tweets, in_order):
    """
        Computes the proximity between USER and the remaining users as the adamic/adar score
    """
    proximities = {}
    
    for user in users:
        score = 0
        if user != USER:
	    for tweet in users[USER]:
		if in_order:
	            if tweet in users[user] and users[user][tweet] > users[USER][tweet]:
		        score = score + float(1)/math.log(tweets[tweet])
		else:
	            if tweet in users[user]:
		        score = score + float(1)/math.log(tweets[tweet])
		    
	    proximities[user] = score
        
    return proximities
	
def save_proximities(model_file_name, proximities, USER):
    """
        Saves the proximities in model_file_name
    """
    model_file = open(model_file_name, 'w')

    for user in proximities:
        score = proximities[user]
        if score > 0:
	    model_file.write(USER+","+user+","+str(score)+"\n")

    model_file.close()

def scores_to_probabilities(bootstrap_proximities, max_score):
    """
         Scores are turned into probabilities
    """
    for u in bootstrap_proximities:
        for z in bootstrap_proximities[u]:
             score = bootstrap_proximities[u][z]

	     prob = float(math.log(score+1)) / (math.log(max_score+1))

             bootstrap_proximities[u][z] = prob

def compute_proximities_squares(output_prefix, bootstrap_proximities):
    """
        Computes proximities using the squares method
    """
    for u in bootstrap_proximities:
        model_file_name = "models_cold_start/"+output_prefix+"_"+str(u)
        probabilities = {}
        
	for v in bootstrap_proximities:
	    if u != v:
	        for z in bootstrap_proximities[u]:
	            u_z = bootstrap_proximities[u][z]
	    
		    if z in bootstrap_proximities[v]:
		        v_z = bootstrap_proximities[v][z]
		    else:
		        v_z = 0
		    
		    if v_z > 0:
		        for y in bootstrap_proximities[v]:
		            v_y = bootstrap_proximities[v][y]

                            u_y = u_z * v_z * v_y
			    
#			    print "u_y = %lf * %lf * %lf" % (u_z, v_z, v_y)
                         
		            if y in probabilities:
		                probabilities[y] = probabilities[y] + u_y
		            else:
		                probabilities[y] = u_y

	save_proximities(model_file_name, probabilities, u)

def compute_proximities_triangles(output_prefix, bootstrap_proximities):
    """
        Computes proximities using the triangles (or common neighbors) method
    """
    for u in bootstrap_proximities:
        model_file_name = "models_cold_start/"+output_prefix+"_"+str(u)
        probabilities = {}
	
	for y in bootstrap_proximities[u]:
	    u_y = bootstrap_proximities[u][y]

            for v in bootstrap_proximities[y]:
	        y_v = bootstrap_proximities[y][v]

	    u_v = u_y * y_v

	    if v in probabilities:
	        probabilities[v] = probabilities[v] + u_v
	    else:
                probabilities[v] = u_v
	
	save_proximities(model_file_name, probabilities, u)

def run_cold_start_link_prediction(content_file_name,output_prefix,bootstrap_strategy,transitivity_strategy,in_order):
    """
        Runs user recommendation using cold start link prediction
    """
    tmp_file_name = output_prefix+"_cold_start.tmp"
    output_file = open(tmp_file_name,'w')
    
    users = read_users(content_file_name)
    tweets = read_tweets(content_file_name)

    bootstrap_proximities = {}
    max_score = 0

    for user in users:
        if bootstrap_strategy == "common-content":
	    bootstrap_proximities_user = compute_common_content(user, users, in_order)
	elif bootstrap_strategy == "adamic-adar":
	    bootstrap_proximities_user = compute_adamic_adar(user, users, tweets, in_order)

	if transitivity_strategy == "none":
	    #The model file stores the proximities (1 user per file)
            model_file_name = "models_cold_start/"+output_prefix+"_"+str(user)
	    save_proximities(model_file_name, bootstrap_proximities_user, user)
	else:
	    bootstrap_proximities[user] = {}

            #All bootstrap proximities are added to a single structure
	    for other_user in bootstrap_proximities_user:
	        if bootstrap_proximities_user[other_user] > 0:
		    bootstrap_proximities[user][other_user] = bootstrap_proximities_user[other_user]

		    if bootstrap_proximities_user[other_user] > max_score:
		        max_score = bootstrap_proximities_user[other_user]
	
    #Apply the squares method
    if transitivity_strategy == "squares":
         scores_to_probabilities(bootstrap_proximities, max_score)
         compute_proximities_squares(output_prefix, bootstrap_proximities)
	
    #Apply the triangles method
    if transitivity_strategy == "triangles":
        scores_to_probabilities(bootstrap_proximities, max_score)
        compute_proximities_triangles(output_prefix, bootstrap_proximities)
	
    for user in users:
        model_file_name = "models_cold_start/"+output_prefix+"_"+str(user)
	#Read proximities
        proximities = read_proximities(model_file_name)

        for rec_user in users:
	    if rec_user != user:
	        if rec_user in proximities:
	            score = proximities[rec_user]
	        else:
		    score = 0
	        
		score = score * len(users[user])

		if score > 0:
		    output_file.write(user+","+rec_user+","+str(score)+"\n")

    output_file.close()
   
    tmp_dir_name = output_prefix+"_cold_start_tmp_dir"
    commands.getoutput("mkdir "+tmp_dir_name)
    output_file_name = output_prefix+"_cold_start.csv"
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
            opts, args = getopt.getopt(argv[1:], "b:t:r:o:h", ["bootstrap-strategy=","transitivity-strategy=","in-order=","output=","help"])
        except getopt.error, msg:
            raise Usage(msg)
        
        if len(args) < 1:
	    print "python cold_start.py [-b <bootstrap strategy>] [-t <transitivity strategy>] [-r <in order>] [-o <output prefix>] [<content file>]"
	    sys.exit()
	
	content_file_name = args[0]
	output_prefix = ""
	bootstrap_strategy = "common-content"
	transitivity_strategy = "none"
	in_order = False
	in_order_arg = "false"

        for opt,arg in opts:
	    if opt in ('-h', '--help'):
	        print "python cold_start.py [-b <bootstrap strategy>] [-t <transitivity strategy>] [-r <in order>] [-o <output prefix>] [<content file>]"
	        sys.exit()
	    
	    if opt in ('-b', '--bootstrap-strategy'):
	        bootstrap_strategy = arg
	
	    if opt in ('-t', '--transitivity-strategy'):
	        transitivity_strategy = arg
	    
	    if opt in ('-r', '--in-order'):
	        in_order_arg = arg
		
		if in_order_arg == "true":
		    in_order = True
	    
	    if opt in ('-o', '--output'):
	        output_prefix = arg
	    
	print "python cold_start.py [-b %s] [-t %s] [-r %s] [-o %s] [%s]" % (bootstrap_strategy, transitivity_strategy, in_order_arg, output_prefix, content_file_name)
        
	#Creating dirs for models
        commands.getoutput("mkdir models_cold_start")

        run_cold_start_link_prediction(content_file_name,output_prefix,bootstrap_strategy,transitivity_strategy,in_order)
         
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

if __name__ == "__main__":
    sys.exit(main())
