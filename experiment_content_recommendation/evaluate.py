import sys
import commands
import operator
import getopt
import math

def read_test_data(test_file_name):
    """
        Gets test data for evaluation
    """
    test_file = open(test_file_name, 'r')
    test_data = {}
    
    for line in test_file:
        line = line.rstrip()
        test_data[line] = 1

    test_file.close()

    return test_data

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
	content = vec[1]

	users[user] = 1

    test_file.close()

    return users
    
def read_predictions(input_file_name):
    """
        Gets the predictions for USER in the input file
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

def read_predictions_user(input_file_name,USER):
    """
        Gets the predictions for USER in the input file
    """
    input_file = open(input_file_name, 'r')
    predictions = {}
    
    for line in input_file:
        line = line.rstrip()
        vec = line.rsplit(',')

	user = vec[0]
	content = vec[1]
	score = vec[2]
        
	if user == USER:
	    predictions[content] = float(score)

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
    test_data = read_test_data(test_file_name)
    num_users = len(users)
    num_tweets = len(tweets)
    num_test_tweets_with_repetitions = len(test_data)

    total_positive = num_test_tweets_with_repetitions
    total_negative = num_users * num_tweets - num_test_tweets_with_repetitions

    predictions = read_predictions(input_file_name)

    sorted_predictions = sorted(predictions.iteritems(), key=operator.itemgetter(1), reverse=True)
    
    num_false_positives = 0
    num_true_positives = 0
    
    start = False
                
    output_file.write("0.0	0.0\n")

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

	    if prediction in test_data:
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

def recall_at(input_file_name,test_file_name,output_prefix):
    """
        Computes the recall @ 5, 10, 15, and 20
    """
    output_file_name = output_prefix+"_recall_at.dat"
    output_file = open(output_file_name,'w')
    values = [5, 10, 15, 20]
    recalls = [0, 0, 0, 0]
    num_users = [0, 0, 0, 0]

    users = get_users(test_file_name)
    tweets = read_tweets(test_file_name)

    for user in users:
       predictions = read_predictions_user(input_file_name,user)
       tweets_user = read_tweets_user(test_file_name,user)

       sorted_predictions = sorted(predictions.iteritems(), key=operator.itemgetter(1), reverse=True)

       for p in range(0,len(values)):
	   recall = 0
	   num_users[p] = num_users[p] + 1

	   for i in range(0,values[p]):
	      if sorted_predictions[i][0] in tweets_user:
                  recall = recall + 1

	   recall = float(recall) / len(tweets_user)
	   recalls[p] = float(recalls[p]) + recall

    for p in range(0,len(values)):
        recalls[p] = float(recalls[p]) / num_users[p]
        output_file.write(str(values[p])+"	"+str(recalls[p])+"	"+str(num_users[p])+"\n")
    
    output_file.close()

def precision_at(input_file_name,test_file_name,output_prefix):
    """
        Computes the precision @ 5, 10, 15, and 20
    """
    output_file_name = output_prefix+"_precision_at.dat"
    output_file = open(output_file_name,'w')
    values = [5, 10, 15, 20]
    precisions = [0, 0, 0, 0]
    num_users = [0, 0, 0, 0]

    users = get_users(test_file_name)
    tweets = read_tweets(test_file_name)

    for user in users:
       predictions = read_predictions_user(input_file_name,user)
       tweets_user = read_tweets_user(test_file_name,user)

       sorted_predictions = sorted(predictions.iteritems(), key=operator.itemgetter(1), reverse=True)

       for p in range(0,len(values)):
	    precision = 0
	    num_users[p] = num_users[p] + 1

	    for i in range(0,values[p]):
	       if sorted_predictions[i][0] in tweets_user:
                   precision = precision + 1

	    precision = float(precision) / values[p]
	    precisions[p] = float(precisions[p]) + precision

    for p in range(0,len(values)):
        precisions[p] = float(precisions[p]) / num_users[p]
        output_file.write(str(values[p])+"	"+str(precisions[p])+"\n")
    
    output_file.close()

def precision_recall(input_file_name,test_file_name,output_prefix):
    """
        Computes the precision-recall curve
    """
    output_file_name = output_prefix+"_precision_recall.dat"
    output_file = open(output_file_name,'w')
    
    test_data = read_test_data(test_file_name)
    num_test_tweets_with_repetitions = len(test_data)
    users = get_users(test_file_name)
    tweets = read_tweets(test_file_name)
    
    predictions = read_predictions(input_file_name)
    sorted_predictions = sorted(predictions.iteritems(), key=operator.itemgetter(1), reverse=True)

    total_precision = 0
    total_recall = num_test_tweets_with_repetitions
    num_matches = 0
    start = False
    break_even_precision = 1.0
    break_even_recall = 0.0
    precisions = []
    recalls = []

    for p in range(0,len(sorted_predictions)):
	prediction = sorted_predictions[p][0]
	score = sorted_predictions[p][1]

        vec = prediction.rsplit(',')

	user = vec[0]
	content = vec[1]
	
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

	    if prediction in test_data:
	        num_matches = num_matches + 1

    precision = float(num_matches) / total_precision
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
    
    test_data = read_test_data(test_file_name)
    num_test_tweets_with_repetitions = len(test_data)
    users = get_users(test_file_name)
    tweets = read_tweets(test_file_name)
    num_users = len(users)
    num_tweets = len(tweets)
    
    predictions = read_predictions(input_file_name)
    sorted_predictions = sorted(predictions.iteritems(), key=operator.itemgetter(1), reverse=True)

    total_recall = num_test_tweets_with_repetitions
    total_fallout = (num_users * num_tweets) - num_test_tweets_with_repetitions
    num_matches = 0
    num_errors = 0
    start = False
    
    for p in range(0,len(sorted_predictions)):
	prediction = sorted_predictions[p][0]
	score = sorted_predictions[p][1]

        vec = prediction.rsplit(',')

	user = vec[0]
	content = vec[1]
	
	if user in users and content in tweets:
	    if start and prev_score != score:
		recall = float(num_matches) / total_recall
		fallout = float(num_errors) / total_fallout
		
		if fallout > 0:
		    recall_fallout = float(recall) / fallout
                
		    output_file.write(str(prev_score)+"	"+str(recall_fallout)+"	"+str(recall)+"	"+str(fallout)+"\n")
	    
	    prev_score = score
	    start = True

	    if prediction in test_data:
	        num_matches = num_matches + 1
	    else:
	        num_errors = num_errors + 1
    
    recall = float(num_matches) / total_recall
    fallout = float(num_errors) / total_fallout
    recall_fallout = float(recall) / fallout
		
    output_file.write(str(prev_score)+"	"+str(recall_fallout)+"	"+str(recall)+"	"+str(fallout)+"\n")
	    
    output_file.close()

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg
	    
def main(argv=None):
    if argv is None:
        argv = sys.argv

    try:
        try:
            opts, args = getopt.getopt(argv[1:], "o:h", ["output=","help"])
        except getopt.error, msg:
            raise Usage(msg)
        
        if len(args) < 2:
	    print "python evaluate.py [-o <output prefix>] [<input file>] [<test file>]"
	    sys.exit()
	
	input_file_name = args[0]
	test_file_name = args[1]
	output_prefix = ""

        for opt,arg in opts:
	    if opt in ('-h', '--help'):
	        print "python evaluate.py [-o <output prefix>] [<input file>] [<test file>]"
	        sys.exit()
	    
	    if opt in ('-o', '--output'):
	        output_prefix = arg

	print "python evaluate.py [-o %s] [%s] [%s]" % (output_prefix,input_file_name,test_file_name)

	ROC(input_file_name, test_file_name, output_prefix)
	precision_at(input_file_name, test_file_name, output_prefix)
	recall_at(input_file_name, test_file_name, output_prefix)
	precision_recall(input_file_name, test_file_name, output_prefix)
        recall_fallout(input_file_name,test_file_name,output_prefix)

    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

if __name__ == "__main__":
    sys.exit(main())
