# execfile('/Users/austinc/Desktop/Current Work/Rohde_Vote_Coding/Rohde-Roll-Call-Database/vote_fetching_cleaning.py')
from __future__ import division
import urllib2
import string
import time
import re
import datetime
import math
import time
import csv
import os
from string import strip
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

house_file_location=os.path.dirname(os.path.realpath(__file__))+'/house_votes.csv'
senate_file_location=os.path.dirname(os.path.realpath(__file__))+'/senate_votes.csv'

def get_diagnostics(vfile,chamber,ranges=[100,300,500,1000]):
	diag=[]
	with open(vfile,'rU') as csvfile:
		reader=csv.reader(csvfile)
		data=[row for row in reader]

	votetypes=list(set([row[6] for row in data[1:]]))
	votetypes.sort()
	header=['range']
	for vt in votetypes:
		header.append(vt)
	ranges_text=[]
	for r in ranges:
		ranges_text.append('last '+str(r))

	# cut data into ranges and tabulate vote types
	for i,r in enumerate(ranges):
		newrow=[]
		newrow.append(ranges_text[i])
		dataslice=data[-r:]
		for vt in votetypes:
			newrow.append(len([row for row in dataslice if row[6]==vt])/r)
		diag.append(newrow)
		print newrow

	newrow=[]
	newrow.append('all')
	dataslice=data
	for vt in votetypes:
		newrow.append(len([row for row in dataslice if row[6]==vt])/len(data))
	diag.append(newrow)
	print newrow

	with open(os.path.dirname(os.path.realpath(__file__))+'/'+chamber+'_diagnostics.csv','w') as cfile:
		writer=csv.writer(cfile)
		writer.writerow(header)
		for row in diag:
			writer.writerow(row)

def draw_graphs(vfile,chamber):
	with open(vfile,'rU') as csvfile:
		reader=csv.reader(csvfile)
		data=[row for row in reader]

	if chamber=="senate":
		minyear=1969

	if chamber=="house":
		minyear=1953

	uniquelist=list(set([row[6] for row in data[1:]]))
	
	# list of years and votetypes
	votes=[[row[2],row[6]] for row in data[1:]]
	years=list(set([row[0] for row in votes]))
	years.sort()

	# for each vote type in uniquelist, get 1-year average and 3-year average for
	# each year
	for vtype in uniquelist:
		a1=[]
		a3=[]
		for year in years:
			# get percent of votes in one year that equal vtype
			vlist1=[row for row in votes if row[0]==year]
			ratio1=len([row for row in vlist1 if row[1]==vtype])/len(vlist1)
			a1.append(ratio1)
			if year>minyear+1:
				vlist3=[row for row in votes if row[0]<=year and row[0]>=int(year)-2]
				ratio3=len([row for row in vlist3 if row[1]==vtype])/len(vlist3)
				a3.append(ratio3)

		plt.plot(years,a1)
		plt.plot(years[2:],a3)
		plt.title(vtype)
		plt.grid(True)
		plt.savefig(os.path.dirname(os.path.realpath(__file__))+'/graphs/'+chamber+str(vtype)+'_graph.png')
		# plt.savefig('/Users/austinc/Desktop/graphs'+'/'+str(vtype)+'_graph.png')
		plt.close()

get_diagnostics(house_file_location,'house')
get_diagnostics(senate_file_location,'senate')

draw_graphs(house_file_location,'house')
draw_graphs(senate_file_location,'senate')
