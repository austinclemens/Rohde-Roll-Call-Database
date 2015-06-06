from __future__ import division
import urllib2
import string
import time
import re
import datetime
import math
import numpy as np
import pandas as pd
import time
import csv

def output_training_votes(file_path='/Users/austinc/Desktop/votes.csv',target_file='/Users/austinc/Desktop/type_examples.csv'):
	"""Takes the Rohde dataset, gets the two most recent examples of each type of vote in the dataset,
	outputs them to a file so they can be checked against Thomas."""
	# execfile('/Users/austinc/Desktop/Current Work/Rohde_Vote_Coding/Rohde-Roll-Call-Database/vote_fetching_cleaning.py')

	data=pd.read_csv(file_path)
	vote_codes=list(set(data['vote']))

	# For each vote code, output 2 of: [vote,cong,session,year,billtype1,billnum1,date]
	output=[]
	output.append(['vote code','congress','session','year','bill type','bill number','date'])

	for vote in vote_codes:
		temp_data=data[data['vote']==vote]
		temp_data=temp_data[['vote','cong','session','year','billtype1','billnum1','date']]

		try:
			output.append(list(temp_data.iloc[-2]))
		except:
			pass

		try:
			output.append(list(temp_data.iloc[-2]))
		except:
			pass

	with open(target_file,'wb') as f:
		writer=csv.writer(f)
		writer.writerows(output)
