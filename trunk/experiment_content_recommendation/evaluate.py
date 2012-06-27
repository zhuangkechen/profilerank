import sys
import operator
import getopt
import math
import commands

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

def get_users(test_file_name):
    """
        Gets users from the input file
    """
    test_file = open(test_file_name, 'r')
    users = {}
    
    for line in test_file:
        line = line.rstrip()
        vec = line.rsplit(',')

	user = vec[0]

	users[user] = 1

    test_file.close()

    return users
    
def read_predictions(input_file_name):
    """
        Gets the predictions in the input file
    """
    input_file = open(input_file_name, 'r')
    predictions = {}
    
    for line in input_file:
        line = line.rstrip()
        vec = line.rsplit(',')

	user = vec[0]
	content = vec[1]
	score = vec[2]
        
	predictions[user+","+content] = float(score)

    input_file.close()

    return predictions

def read_top_predictions_users(input_file_name, num):
    """
        Gets the predictions in the input file, the input file is assumed to be sorted
	w.r.t. score
    """
    input_file = open(input_file_name, 'r')
    predictions = {}
    
    for line in input_file:
        line = line.rstrip()
        vec = line.rsplit(',')

	user = vec[0]
	content = vec[1]
	score = vec[2]
        
	if user in predictions:
            #Max number of tuples for a user is num
	    if len(predictions[user]) < num:
	        predictions[user][content] = float(score)
	else:
	    predictions[user] = {}
	    predictions[user][content] = float(score)

    input_file.close()

    return predictions

def read_predictions_users(input_file_name):
    """
        Gets the predictions in the input file
    """
    input_file = open(input_file_name, 'r')
    predictions = {}
    
    for line in input_file:
        line = line.rstrip()
        vec = line.rsplit(',')

	user = vec[0]
	content = vec[1]
	score = vec[2]
        
	if user in predictions:
	    predictions[user][content] = float(score)
	else:
	    predictions[user] = {}
	    predictions[user][content] = float(score)

    input_file.close()

    return predictions


def area(roc_curve_file_name):
    """
        Computes the area under the a ROC curve from the file
    """
    area = 0.0
    input_file = open(roc_curve_file_name, 'r')
    line = input_file.readline()
    line = line.rstrip()
    vec = line.rsplit()
    x_0 = float(vec[0])
    y_0 = float(vec[1])
 
    for line in input_file:
        line = line.rstrip()
        vec = line.rsplit()
        x_1 = float(vec[0])
        y_1 = float(vec[1])

        area = area + float((x_1-x_0)*(y_1+y_0))/2
 
        x_0 = x_1
        y_0 = y_1
 
    input_file.close()
 
    return area

def ROC(input_file_name, test_file_name, output_prefix):
    """
        Generates a ROC curve based on predictions (input_file_name) and test data
    """
    output_file_name = output_prefix+"_ROC.dat"
    output_file = open(output_file_name,'w')
    tweets = read_tweets(test_file_name)
    users = get_users(test_file_name)
    (test_data,num_test_tweets_with_repetitions) = read_tweets_users(test_file_name)
    num_users = len(users)
    num_tweets = len(tweets)

    total_positive = num_test_tweets_with_repetitions
    total_negative = num_users * num_tweets - num_test_tweets_with_repetitions

    predictions = read_predictions(input_file_name)

    sorted_predictions = sorted(predictions.iteritems(), key=operator.itemgetter(1), reverse=True)
    
    num_false_positives = 0
    num_true_positives = 0
    
    start = False
                
    output_file.write("0.0	0.0\n")
    prev_score = 0
    score = 0

    for p in range(0,len(sorted_predictions)):
	prediction = sorted_predictions[p][0]
	score = sorted_predictions[p][1]

        vec = prediction.rsplit(',')

	user = vec[0]
	content = vec[1]
	
	if user in users and content in tweets:
	    if start and prev_score != score:
	        tpr = float(num_true_positives) / total_positive
	        fpr = float(num_false_positives) / total_negative
            
                output_file.write(str(fpr)+"	"+str(tpr)+"\n")
	
	    prev_score = score
	    start = True

	    if user in test_data and content in test_data[user]:
	        num_true_positives = num_true_positives + 1
	    else:
	        num_false_positives = num_false_positives + 1

    
    tpr = float(num_true_positives) / total_positive
    fpr = float(num_false_positives) / total_negative
    output_file.write(str(fpr)+"	"+str(tpr)+"\n")

    output_file.write("1	1\n")
    output_file.close()

    #Computing AUC
    AUC = area(output_file_name)
    print "AUC = %lf" % AUC

def precision_recall_at(input_file_name,test_file_name,output_prefix):
    """
        Computes the precision and recall @ 5, 10, 15, and 20, the input file is assumed
	to be sorted w.r.t. score
    """
    precision_file_name = output_prefix+"_precision_at.dat"
    recall_file_name = output_prefix+"_recall_at.dat"
    precision_file = open(precision_file_name,'w')
    recall_file = open(recall_file_name,'w')
    values = [5, 10, 15, 20]
    precisions = [0, 0, 0, 0]
    recalls = [0, 0, 0, 0]
    num_users = [0, 0, 0, 0]

    users = get_users(test_file_name)
    predictions = read_top_predictions_users(input_file_name, 20)
    (test_data,num_test_tweets_with_repetitions) = read_tweets_users(test_file_name)

    for user in users:
       if user in predictions:
           sorted_predictions = sorted(predictions[user].iteritems(), key=operator.itemgetter(1), reverse=True)
       else:
           sorted_predictions = []

       for p in range(0,len(values)):
	    precision = 0
	    recall = 0
	    
	    num_users[p] = num_users[p] + 1

	    for i in range(0,values[p]):
	        if i < len(sorted_predictions) and sorted_predictions[i][0] in test_data[user]:
                    precision = precision + 1
		    recall = recall + 1

	        precision = float(precision) / values[p]
	        precisions[p] = float(precisions[p]) + precision
	        recall = float(recall) / len(test_data[user])
	        recalls[p] = float(recalls[p]) + recall

    for p in range(0,len(values)):
        precisions[p] = float(precisions[p]) / num_users[p]
        precision_file.write(str(values[p])+"	"+str(precisions[p])+"	"+str(num_users[p])+"\n")
        recalls[p] = float(recalls[p]) / num_users[p]
        recall_file.write(str(values[p])+"	"+str(recalls[p])+"	"+str(num_users[p])+"\n")
    
    precision_file.close()
    recall_file.close()

def precision_recall(input_file_name,test_file_name,output_prefix):
    """
        Computes the precision-recall curve
    """
    output_file_name = output_prefix+"_precision_recall.dat"
    output_file = open(output_file_name,'w')
    
    (test_data,num_test_tweets_with_repetitions) = read_tweets_users(test_file_name)
    users = get_users(test_file_name)
    tweets = read_tweets(test_file_name)
    
    total_precision = 0
    total_recall = num_test_tweets_with_repetitions
    num_matches = 0
    start = False
    break_even_precision = 1.0
    break_even_recall = 0.0
    precisions = []
    recalls = []
    prev_score = 0
    score = 0

    input_file = open(input_file_name, 'r')

    for line in input_file:
        line = line.rstrip()
	vec = line.rsplit(',')

	user = vec[0]
	content = vec[1]
	score = vec[1]
	
	if user in users and content in tweets:
	    if start and prev_score != score:
	        precision = float(num_matches) / total_precision
		recall = float(num_matches) / total_recall

		if num_matches > 0 and math.fabs(precision - recall) < math.fabs(break_even_precision - break_even_recall):
		    break_even_precision = precision
		    break_even_recall = recall
	            
		    precisions.append(precision)
		    recalls.append(recall)
                
	    total_precision = total_precision + 1

	    prev_score = score
	    start = True

	    if user in test_data and content in test_data[user]:
	        num_matches = num_matches + 1

    if total_precision > 0:
        precision = float(num_matches) / total_precision
    else:
       precision = 0
    
    recall = float(num_matches) / total_recall
    
    precisions.append(precision)
    recalls.append(recall)
    
    for i in range(0,len(recalls)):
        precision = 0

	for j in range(i,len(precisions)):
	    if precision < precisions[j]:
	        precision = precisions[j]
    
        output_file.write(str(precision)+"	"+str(recalls[i])+"\n")
    
    #Adjusting the Breakeven point
    if break_even_precision < break_even_recall:
        BEP = break_even_precision
    else:
        BEP = break_even_recall
    
    print "BEP = %lf" % (BEP)
    output_file.close()

def recall_fallout(input_file_name,test_file_name,output_prefix):
    """
        Computes the recall-fallout curve
    """
    output_file_name = output_prefix+"_recall_fallout.dat"
    output_file = open(output_file_name,'w')
    
    (test_data,num_test_tweets_with_repetitions) = read_tweets_users(test_file_name)
    users = get_users(test_file_name)
    tweets = read_tweets(test_file_name)
    num_users = len(users)
    num_tweets = len(tweets)
    
    total_recall = num_test_tweets_with_repetitions
    total_fallout = (num_users * num_tweets) - num_test_tweets_with_repetitions
    num_matches = 0
    num_errors = 0
    start = False
    prev_score = 0
    score = 0
    
    #Re-ordering the scores
    commands.getoutput("sort -t, -k3,3g "+input_file_name+" > recall_fallout.tmp")
    input_file = open("recall_fallout.tmp", 'r')

    for line in input_file:
        line = line.rstrip()
	vec = line.rsplit(',')

	user = vec[0]
	content = vec[1]
	score = vec[1]
	
	if user in users and content in tweets:
	    if start and prev_score != score:
		recall = float(num_matches) / total_recall
		fallout = float(num_errors) / total_fallout
		
		if fallout > 0:
		    recall_fallout = float(recall) / fallout
                
		    output_file.write(str(prev_score)+"	"+str(recall_fallout)+"	"+str(recall)+"	"+str(fallout)+"\n")
	    
	    prev_score = score
	    start = True

	    if user in test_data and content in test_data[user]:
	        num_matches = num_matches + 1
	    else:
	        num_errors = num_errors + 1
    
    recall = float(num_matches) / total_recall
    fallout = float(num_errors) / total_fallout
    
    if fallout > 0:
        recall_fallout = float(recall) / fallout
    else:
        recall_fallout = 0
		
    output_file.write(str(prev_score)+"	"+str(recall_fallout)+"	"+str(recall)+"	"+str(fallout)+"\n")
	    
    output_file.close()
    
    commands.getoutput("rm recall_fallout.tmp")

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg
	    
def main(argv=None):
    if argv is None:
        argv = sys.argv

    try:
        try:
            opts, args = getopt.getopt(argv[1:], "o:hs", ["output=","help","silent"])
        except getopt.error, msg:
            raise Usage(msg)
        
        if len(args) < 2:
	    print "python evaluate.py [-o <output prefix>] [<input file>] [<test file>]"
	    sys.exit()
	
	input_file_name = args[0]
	test_file_name = args[1]
	output_prefix = ""
	silent = False

        for opt,arg in opts:
	    if opt in ('-h', '--help'):
	        print "python evaluate.py [-o <output prefix>] [<input file>] [<test file>]"
	        sys.exit()
	    
	    if opt in ('-o', '--output'):
	        output_prefix = arg
	    
	    if opt in ('-s', '--silent'):
	        silent = True

        if silent is False:
	    print "python evaluate.py [-o %s] [%s] [%s]" % (output_prefix,input_file_name,test_file_name)

	ROC(input_file_name, test_file_name, output_prefix)
	precision_recall_at(input_file_name, test_file_name, output_prefix)
	precision_recall(input_file_name, test_file_name, output_prefix)
        recall_fallout(input_file_name,test_file_name,output_prefix)

    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

if __name__ == "__main__":
    sys.exit(main())
