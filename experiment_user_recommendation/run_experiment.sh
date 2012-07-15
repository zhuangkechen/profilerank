#!/bin/bash

databases_dir='../../data/'
databases=("brasileirao") 
train_rate=0.5
min_freq_content=("2")
min_freq_user=("5")
num_iterations_profilerank=10
damping_factor=0.85
cold_start_methods=("common-content_none" "adamic-adar_none" "common-content_triangles" "common-content_squares" "adamic-adar_triangles" "adamic-adar_squares" "common-content_none_ordered" "adamic-adar_none_ordered" "common-content_triangles_ordered" "common-content_squares_ordered" "adamic-adar_triangles_ordered" "adamic-adar_squares_ordered")

d=0

python run.py [-n <num iterations profilerank>] [-d <damping factor profilerank>] [-o <output prefix>] [-f <dist function>] [<content file>]

for database in ${databases[@]}
do
	echo "database: $database"
	
	echo "Generating data"
	python generate_data.py -c train-$database.csv -n test-$database.csv -t ${min_freq_content[$d]} -u ${min_freq_user[$d]} $databases_dir$database\_tweets.csv $databases_dir$database\_network.csv
	
	echo "Running methods"
	python run.py -n $num_iterations_profilerank -d $damping_factor -o $database train-$database.csv
	
	echo "Evaluating profilerank"
	python evaluate.py -o $database-profilerank $database\_profilerank.csv test-$database.csv

	for method in ${cold_start_methods[@]}
	do
		echo "Evaluating $method"
		python evaluate.py -o $database-$method $database\_$method\_cold_start.csv test-$database.csv
	done
        
	d=$(($d+1))
done

