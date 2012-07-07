import sys
import operator
from scipy.sparse import coo_matrix, SparseEfficiencyWarning
from numpy import array
import getopt
import math
import warnings
import commands

warnings.simplefilter('ignore',SparseEfficiencyWarning)

def print_matrix(matrix):
    """
	Prints a matrix.
    """
    for i in range(0,len(matrix)):
        for j in range(0,len(matrix[i])):
            sys.stdout.write(str(matrix[i][j])+ " ")
	print 

def power_method(M1,M2,num_iterations,damping_factor,num_columns,user=""):
    """
    Implements the power method for a pair of matrices. 
    The linear system to be solved is:
    S = damping_factor*M1*M2 + (1-damping_factor)*U
    where U is a uniform vector
    """
    row = []
    column = []
    data = []

    #In case there is not an input user, C is initialized as a uniform vector.
    if user == "":
        for i in range(0,num_columns):
            row.append(0)
	    column.append(i)
            data.append(float(1)/num_columns)
    #Otherwise, only the position of C corresponding to the user is initialized as 1.
    else:
        for i in range(0,num_columns):
            row.append(0)
	    column.append(i)
	    
	    if user == i:
	        data.append(float(1))
	    else:
	        data.append(0)

    #Generating C matrix using coo_matrix from scipy
    C = coo_matrix((data,(row,column)), shape=(1,num_columns))
    U = C

    for i in range(num_iterations):
	T = C * M1
	S = T * M2
        
	S = damping_factor * S + (1.0-damping_factor) * U

#	e = sqeuclidean(S.getrow(0).todense(),C.getrow(0).todense())
	
	C = S

    return S.getrow(0).toarray()

def fast_read_data(input_file_name,function):
    """
    Reads input data. 
    Format:  
        <user,content>
        <user,content>
	...

    Lines must be sorted according to the order in which the content appears.
    Returns two dictionaries containing user and content ids and two matrices (CU and UC).
    CU is a content-user matrix. It connects content to its information sources (users).
    UC is a user-content matrix. It connects sources/users to the content they propagate.
    """
    tmp_dir_name = "profilerank_tmp_dir"
    tmp_file_name = "profilerank.tmp"
    commands.getoutput("mkdir "+tmp_dir_name)
    commands.getoutput("sort -st, -k2,2 -T "+tmp_dir_name+" "+input_file_name+" > "+tmp_file_name)
    commands.getoutput("rm -r "+tmp_dir_name)

    input_file = open(tmp_file_name, 'r')
    users = {}
    contents = {}
    user_id = 0
    content_id = -1
    sum_user = {}
    sum_content = {}

    user_content = []
    content_user = []
    non_dangling_users = {}

    last_content = ""
    n = 0
    
    for line in input_file:
        n = n + 1
	if n % 10000 == 0:
	    print "== %d lines read ==" % n
        line = line.rstrip()
	vec = line.rsplit(',')
        user = vec[0]
	content = vec[1]

	if user not in users:
	    users[user] = user_id
	    user = user_id
	    user_id = user_id + 1
        else:
	    user = users[user]
	
	if user not in sum_user:
	    sum_user[user] = 0
	
	if content != last_content:
	    content_id = content_id + 1
	    contents[content] = content_id
	    content_user.append([content_id,user,1])
	    sum_content[content_id] = 1
	else:
	    non_dangling_users[user] = 1
	
	user_content.append([user,content_id,1])
	sum_user[user] = sum_user[user] + 1
	last_content = content

    input_file.close()
    #commands.getoutput("rm "+tmp_file_name)

    content_id = content_id + 1

    #Both UC and CU are normalized.
    for user in sum_user:
        content_user.append([content_id,user,float(1)/user_id])
        
	#dangling users/sources are connected connected to a default content in the UC matrix.
        if user not in non_dangling_users:
	    user_content.append([user,content_id,1])
	    sum_user[user] = sum_user[user] + 1

    for i in range(0,len(user_content)):
        user_content[i][2] =  float(user_content[i][2]) / (sum_user[user_content[i][0]])

#    for content in sum_content:
#	sum_value = 0.0
           
#	for j in range(0,len(content_user)):
#	    if content == content_user[j][0]:
#	        sum_value = sum_value + content_user[j][2]

#        for j in range(0,len(content_user)):
#	    if content == content_user[j][0]:
#	        content_user[j][2] = float(content_user[j][2]) / (sum_value)
    
    content_id = content_id + 1

#    print "user_content:"
#    for i in range(0,len(user_content)):
#        print user_content[i]

#    print "content_user:"
#    for i in range(0,len(content_user)):
#        print content_user[i]

    row = []
    column = []
    data = []

    for i in range(0,len(user_content)):
        row.append(user_content[i][0])
        column.append(user_content[i][1])
        data.append(user_content[i][2])

    user_content = []

    #Generating UC matrix using coo_matrix from scipy
    UC = coo_matrix((data,(row,column)), shape=(user_id,content_id))
    
    row = []
    column = []
    data = []

    for i in range(0,len(content_user)):
        row.append(content_user[i][0])
        column.append(content_user[i][1])
        data.append(content_user[i][2])

    content_user = []

    #Generating CU matrix using coo_matrix from scipy
    CU = coo_matrix((data,(row,column)), shape=(content_id,user_id))

    return users,contents,UC,CU


def read_data(input_file_name,function):
    """
    Reads input data. 
    Format:  
        <user,content>
        <user,content>
	...

    Lines must be sorted according to the order in which the content appears.
    Returns two dictionaries containing user and content ids and two matrices (CU and UC).
    CU is a content-user matrix. It connects content to its information sources (users).
    UC is a user-content matrix. It connects sources/users to the content they propagate.
    """
    input_file = open(input_file_name, 'r')
    contents = {}
    users = {}
    user_id = 0
    content_id = 0
    sum_user = {}
    sum_content = {}

    user_content = []
    content_user = []
    non_dangling_users = {}
    
    for line in input_file:
        line = line.rstrip()
	vec = line.rsplit(',')
        user = vec[0]
	content = vec[1]

	if user not in users:
	    users[user] = user_id
	    user = user_id
	    user_id = user_id + 1
        else:
	    user = users[user]
	
	if user not in sum_user:
	    sum_user[user] = 0
	
	if function == "single":
	    if content not in contents:
	        contents[content] = content_id
	        content_user.append([content_id,user,1])
	        sum_content[content_id] = 1
	        content_id = content_id + 1
	    else:
	        non_dangling_users[user] = 1
	
#	elif function == "uniform":
#	    if content not in contents:
#	        contents[content] = content_id
#	        sum_content[content_id] = 0
#	        content_id = content_id + 1
#	    else:
#	        non_dangling_users[user] = 1
	        
#            content_user.append([contents[content],user,1])
#	    sum_content[contents[content]] = sum_content[contents[content]] + 1

#	elif function == "linear":
#	    if content not in contents:
#	        contents[content] = content_id
#	        sum_content[content_id] = 0
#	        content_id = content_id + 1
#	    else:
#	        non_dangling_users[user] = 1

#	    value = float(1) / (sum_content[contents[content]]+1)
#	    content_user.append([contents[content],user,value])
#	    sum_content[contents[content]] = sum_content[contents[content]] + 1

#	elif function == "exponential":
#	    if content not in contents:
#	        contents[content] = content_id
#	        sum_content[content_id] = 0
#	        content_id = content_id + 1
#	    else:
#	        non_dangling_users[user] = 1
            
#	    value = float(1) / math.exp(sum_content[contents[content]])
#	    content_user.append([contents[content],user,value])
#	    sum_content[contents[content]] = sum_content[contents[content]] + 1
	
#	elif function == "logarithm":
#	    if content not in contents:
#	        contents[content] = content_id
#	        sum_content[content_id] = 0
#	        content_id = content_id + 1
#	    else:
#	        non_dangling_users[user] = 1
            
#	    value = float(1) / math.log(sum_content[contents[content]]+2)
#	    content_user.append([contents[content],user,value])
#	    sum_content[contents[content]] = sum_content[contents[content]] + 1
	    
	content = contents[content]
	user_content.append([user,content,1])
	sum_user[user] = sum_user[user] + 1

    input_file.close()

    #Both UC and CU are normalized.
    for user in sum_user:
        content_user.append([content_id,user,float(1)/user_id])
        
	#dangling users/sources are connected connected to a default content in the UC matrix.
        if user not in non_dangling_users:
	    user_content.append([user,content_id,1])
	    sum_user[user] = sum_user[user] + 1

    for i in range(0,len(user_content)):
        user_content[i][2] =  float(user_content[i][2]) / (sum_user[user_content[i][0]])

    for content in sum_content:
	sum_value = 0.0
           
	for j in range(0,len(content_user)):
	    if content == content_user[j][0]:
	        sum_value = sum_value + content_user[j][2]

        for j in range(0,len(content_user)):
	    if content == content_user[j][0]:
	        content_user[j][2] = float(content_user[j][2]) / (sum_value)
    
    content_id = content_id + 1

#    print "user_content:"
#    for i in range(0,len(user_content)):
#        print user_content[i]

#    print "content_user:"
#    for i in range(0,len(content_user)):
#        print content_user[i]

    row = []
    column = []
    data = []

    for i in range(0,len(user_content)):
        row.append(user_content[i][0])
        column.append(user_content[i][1])
        data.append(user_content[i][2])

    user_content = []

    #Generating UC matrix using coo_matrix from scipy
    UC = coo_matrix((data,(row,column)), shape=(user_id,content_id))
    
    row = []
    column = []
    data = []

    for i in range(0,len(content_user)):
        row.append(content_user[i][0])
        column.append(content_user[i][1])
        data.append(content_user[i][2])

    content_user = []

    #Generating CU matrix using coo_matrix from scipy
    CU = coo_matrix((data,(row,column)), shape=(content_id,user_id))

    return users,contents,UC,CU

def compute_relevance(users,contents,UC,CU,num_iterations,damping_factor,user,function):
    """
	Computes relevance and influence based on UC and CU
    """
    #In case there is an input user, the influence is relative to such user
    if user != "" and user in users:
        relevance_vector = power_method(UC,CU,num_iterations,damping_factor,len(users),users[user])
    #Otherwise, the an overall relevance is computed
    else:
        relevance_vector = power_method(UC,CU,num_iterations,damping_factor,len(users))
    
    relevance = {}

    for user in users:
        relevance[user] = relevance_vector[0][users[user]]

    user_relevance = sorted(relevance.iteritems(), key=operator.itemgetter(1), reverse=True)

    #In case there is not an input user, computes the overall relevance
    if user == "" or user not in users:
        relevance_vector = power_method(CU,UC,num_iterations,damping_factor,len(contents)+1)
    #Otherwise, computes the relevance relative to a given user
    else:
        relevance_vector = relevance_vector * UC

    relevance = {}

    #Removing the effect of the dangling content in the relevance scores.
    for content in contents:
        relevance[content] = relevance_vector[0][contents[content]] + (float(relevance_vector[0][len(relevance_vector[0])-1]) / len(contents))

    content_relevance = sorted(relevance.iteritems(), key=operator.itemgetter(1), reverse=True)

    return user_relevance,content_relevance

def compute_user_relevance(users,contents,UC,CU,num_iterations,damping_factor,user,function):
    """
	Computes relevance and influence based on UC and CU
    """
    #In case there is an input user, the influence is relative to such user
    if user != "" and user in users:
        relevance_vector = power_method(UC,CU,num_iterations,damping_factor,len(users),users[user])
    #Otherwise, the an overall relevance is computed
    else:
        relevance_vector = power_method(UC,CU,num_iterations,damping_factor,len(users))
    
    relevance = {}

    for user in users:
        relevance[user] = relevance_vector[0][users[user]]

    user_relevance = sorted(relevance.iteritems(), key=operator.itemgetter(1), reverse=True)

    return user_relevance

def compute_content_relevance(users,contents,UC,CU,num_iterations,damping_factor,user,function):
    """
	Computes relevance and influence based on UC and CU
    """
    #In case there is not an input user, computes the overall relevance
    if user == "" or user not in users:
        relevance_vector = power_method(CU,UC,num_iterations,damping_factor,len(contents)+1)
    #Otherwise, computes the relevance relative to a given user
    else:
        relevance_vector = power_method(UC,CU,num_iterations,damping_factor,len(users))
        relevance_vector = relevance_vector * UC

    relevance = {}

    #Removing the effect of the dangling content in the relevance scores.
    for content in contents:
        relevance[content] = relevance_vector[0][contents[content]] + (float(relevance_vector[0][len(relevance_vector[0])-1]) / len(contents))
    
    content_relevance = sorted(relevance.iteritems(), key=operator.itemgetter(1), reverse=True)

    return content_relevance


def compute_user_statistics(input_file_name):
    """
    Computes user statistics:
        - number of retweets
	- average number of retweets/tweet
	- number of retweeters
	- sum number of retweets retweeter
    TODO: Change names to a more general form
    """
    user_num_retweets = {}
    user_average_num_retweets = {}
    user_num_retweeters = {}
    user_sum_num_retweets_retweeter = {}

    content_user = {}
    num_tweets = {}
    user_retweeter = {}
    
    input_file = open(input_file_name, 'r')
    
    for line in input_file:
        line = line.rstrip()
	vec = line.rsplit(',')
        user = vec[0]
	content = vec[1]

	if user not in num_tweets:
	    user_num_retweets[user] = 0
	    user_average_num_retweets[user] = 0
	    num_tweets[user] = 0

	if content not in content_user:
	    content_user[content] = user
	    num_tweets[user] = num_tweets[user] + 1
	else:
	    user_num_retweets[content_user[content]] = user_num_retweets[content_user[content]] + 1
	    user_retweeter[content_user[content]+"+"+user] = 1
    
    input_file.close()

    for pair in user_retweeter:
        vec = pair.rsplit('+')
	user = vec[0]
	retweeter = vec[1]

	if user in user_num_retweeters:
	    user_num_retweeters[user] = user_num_retweeters[user] + 1
	else:
	    user_num_retweeters[user] = 1

	if user in user_sum_num_retweets_retweeter:
	    user_sum_num_retweets_retweeter[user] = user_sum_num_retweets_retweeter[user] + user_num_retweets[retweeter]
	else:
	    user_sum_num_retweets_retweeter[user] = user_num_retweets[retweeter]
	    
    for user in user_num_retweets:
        if num_tweets[user] > 0:
            user_average_num_retweets[user] = float(user_num_retweets[user]) / num_tweets[user]
	if user not in user_num_retweeters:
	    user_num_retweeters[user] = 0
	if user not in user_sum_num_retweets_retweeter:
	    user_sum_num_retweets_retweeter[user] = 0

    return (user_num_retweets,user_average_num_retweets,user_num_retweeters,user_sum_num_retweets_retweeter) 

def compute_content_statistics(input_file_name):
    """
    Computes content statistics:
        - number of retweets
	- sum number of retweets retweeter
    TODO: Change names to a more general form
    """
    content_num_retweets = {}
    content_sum_num_retweets_retweeter = {}
    user_num_retweets = {}
    
    content_user = {}
    
    input_file = open(input_file_name, 'r')
    
    for line in input_file:
        line = line.rstrip()
	vec = line.rsplit(',')
        user = vec[0]
	content = vec[1]

	if user not in user_num_retweets:
	    user_num_retweets[user] = 0
	
	if content not in content_num_retweets:
	    content_num_retweets[content] = 0
	    content_user[content] = user
	else:
	    content_num_retweets[content] = content_num_retweets[content] + 1
	    user_num_retweets[content_user[content]] = user_num_retweets[content_user[content]] + 1

    input_file.close()
    
    input_file = open(input_file_name, 'r')
    
    for line in input_file:
        line = line.rstrip()
	vec = line.rsplit(',')
        user = vec[0]
	content = vec[1]
	
	if content not in content_sum_num_retweets_retweeter:
	    content_sum_num_retweets_retweeter[content] = 0

	if user != content_user[content]:
	    content_sum_num_retweets_retweeter[content] = content_sum_num_retweets_retweeter[content] + user_num_retweets[user]

    input_file.close()

    return (content_num_retweets,content_sum_num_retweets_retweeter,content_user)

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg
	    
def main(argv=None):
    if argv is None:
        argv = sys.argv

#input_file_name = sys.argv[1] or "USAGE: python pr.py [INPUT] [NUM ITERATIONS] [DAMPING FACTOR] [OUTPUT] [USER|CONTENT]"
    try:
        try:
            opts, input_file_name = getopt.getopt(argv[1:], "n:d:o:a:u:l:f:hs", ["num-iterations=","damping-factor=","output=","analysis=","user=","user-list=","dist-function=","help","silent"])
        except getopt.error, msg:
            raise Usage(msg)
 
        num_iterations = 10
        damping_factor = 0.85
        output_file_name = ""
        analysis = "user"
	user = ""
	function = "single"
	user_list_file_name = "none"
	silent = False

        if len(input_file_name) < 1:
	    print "python profilerank.py [-n <num iterations>] [-d <damping factor>] [-o <output file>] [-a <user|content>] [-u <user>] [-l <user list>] [-f <dist function>] [input file]"
	    sys.exit()

        for opt,arg in opts:
	    if opt in ('-n', '--num-iterations'):
                num_iterations = int(arg)
	    
            if opt in ('-d', '--damping-factor'):
	        damping_factor = float(arg)
        
	    if opt in ('-o', '--output'):
	        output_file_name = arg
	
	    if opt in ('-a', '--analysis'):
	        analysis = arg
	    
	    if opt in ('-u', '--user'):
	        user = arg
	    
	    if opt in ('-f', '--dist-function'):
	        function = arg
	    
	    if opt in ('-l', '--user-list'):
	        user_list_file_name = arg
	    
	    if opt in ('-s', '--silent'):
		silent = True
	
	    if opt in ('-h', '--help'):
	        print "python profilerank.py [-n <num iterations>] [-d <damping factor>] [-o <output file>] [-a <user|content>] [-u <user>] [-l <user list>] [-f <dist function>] [input file]"
	        sys.exit()

	if silent == False:
	    print "python profilerank.py [-n %d] [-d %lf] [-o %s] [-a %s] [-u %s] [-l %s] [-f %s] [%s]" %(num_iterations, damping_factor, output_file_name, analysis, user, user_list_file_name, function, input_file_name[0])
    
        print "reading data"
        #Read the input file
        (users,contents,UC,CU) = fast_read_data(input_file_name[0],function)
	print "reading finished!"

        if user_list_file_name == "none":
	    user_relevance = []
	    content_relevance = []
	    if analysis == "user":
                user_relevance = compute_user_relevance(users,contents,UC,CU,num_iterations,damping_factor,user,function)
            else:
	        content_relevance = compute_content_relevance(users,contents,UC,CU,num_iterations,damping_factor,user,function)
    
            user_relevance_table = {}

            if output_file_name != "":
                output_file = open(output_file_name, 'w')
            else:
                output_file = sys.stdout

            for u in range(0,len(user_relevance)):
                user_relevance_table[user_relevance[u][0]] = user_relevance[u][1]
        
                if analysis == "user":
	            if user != user_relevance[u][0]:
                        output_file.write(str(user_relevance[u][0])+","+ str(user_relevance[u][1])+"\n")
    
            if analysis == "content":
                for c in range(0,len(content_relevance)):
                    output_file.write(str(content_relevance[c][0])+","+ str(content_relevance[c][1])+"\n")
	    
	    if output_file_name != "":
	        output_file.close()
	else:
	    user_list_file = open(user_list_file_name, 'r')

	    for user in user_list_file:
	        user = user.rstrip()
		if output_file_name != "":
                    output_file = open(output_file_name+"_"+str(user), 'w')
                else:
                    output_file = sys.stdout

                (user_relevance,content_relevance) = compute_relevance(users,contents,UC,CU,num_iterations,damping_factor,user,function)
            
	        user_relevance_table = {}

                for u in range(0,len(user_relevance)):
                    user_relevance_table[user_relevance[u][0]] = user_relevance[u][1]
        
                    if analysis == "user":
	                if user != user_relevance[u][0]:
                            output_file.write(str(user_relevance[u][0])+","+ str(user_relevance[u][1])+"\n")
    
                if analysis == "content":
                    for c in range(0,len(content_relevance)):
                        output_file.write(str(content_relevance[c][0])+","+ str(content_relevance[c][1])+"\n")

		if output_file_name != "":
		    output_file.close()
   
            user_list_file.close()
    
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

if __name__ == "__main__":
    sys.exit(main())
