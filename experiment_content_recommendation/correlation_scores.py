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

def get_correlation(output_prefix,scores_one_file_name,scores_two_file_name,test_file_name):
    """
        Computes correlations between scores
    """
    output_file_right_name = output_prefix+"_correlation_right.dat"
    output_file_right = open(output_file_right_name,'w')
    
    output_file_wrong_name = output_prefix+"_correlation_wrong.dat"
    output_file_wrong = open(output_file_wrong_name,'w')

    test_data = read_test_data(test_file_name)
    predictions_one = read_predictions(scores_one_file_name)
    predictions_two = read_predictions(scores_two_file_name)

    for prediction in predictions_one:
        if prediction in predictions_two:
	    if prediction in test_data:
	        output_file_right.write(str(predictions_one[prediction])+"	"+str(predictions_two[prediction])+"\n")
	    else:
	        output_file_wrong.write(str(predictions_one[prediction])+"	"+str(predictions_two[prediction])+"\n")
	       
    output_file_right.close()
    output_file_wrong.close()

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
        
        if len(args) < 3:
	    print "python correlation_scores.py [-o <output prefix>] [<scores I>] [<scores II>] [test file]"
	    sys.exit()
	
	scores_one_file_name = args[0]
	scores_two_file_name = args[1]
	test_file_name = args[2]
	output_prefix = ""

        for opt,arg in opts:
	    if opt in ('-h', '--help'):
	        print "python run.py [-o <output prefix>] [<scores I>] [<scores II>] [test file]"
	        sys.exit()
	    
	    if opt in ('-o', '--output'):
	        output_prefix = arg
	    
	print "python run.py [-o %s] [%s] [%s] [%s]" % (output_prefix,scores_one_file_name,scores_two_file_name,test_file_name)

        get_correlation(output_prefix,scores_one_file_name,scores_two_file_name,test_file_name)
         
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

if __name__ == "__main__":
    sys.exit(main())
