def load_comparison():
	fileloc='/Users/austinc/Desktop/senate.csv'
	with open(fileloc,'r') as cfile:
		reader=csv.reader(cfile)
		data=[row for row in reader]
	data=[row for row in data[1:] if int(row[2])>=1989 and int(row[2])<=2011]
	return data

# useful rows:
# 0: congress
# 2: year
# 3: vote number
# 6: oldvote
# 30: bill type
# 31: bill number
# 32: full bill type/number
# 33: question
# 34: amendment
# 35: result
# 36: url
# 37: title

# show a code and associated fields
def show_code(code,data):
	temp=[vote for vote in data if int(vote[6])==code]
	for vote in temp:
		print vote[0]+','+vote[1]+','+vote[3]+','+str(vote[6])+'|||'+str(vote[7])+'|||'+vote[2]+'|||'+vote[3]+'|||'+vote[32]+'|||'+vote[33]+'>>>'+vote[34]+'<<<'+vote[37]
		print

def code_votes_senate(data,test=0):
	for row in data:
		question=strip(row[33])
		bill_title=strip(row[36])
		votetype=strip(row[30]).lower()
		amendment=strip(row[34])
		code=classify_question(question,bill_title,votetype,amendment,test=test)
		row[7]=code
	return data

def show_discrep(code,data):
	print 'Total of oldcode: ',len([row for row in data if str(row[6])==str(code)])
	print 'Newcode not assigned: ',len([row for row in data if str(row[6])==str(code) and str(row[7])!=str(code)])
	print 'Newcode assigned erroneously: ',len([row for row in data if str(row[6])!=str(code) and str(row[7])==str(code)])
	print
	print "NOT ASSIGNED:"
	for vote in [row for row in data if str(row[6])==str(code) and str(row[7])!=str(code)]:
		print str(vote[6])+'|||'+str(vote[7])+'|||'+vote[2]+'|||'+vote[3]+'|||'+vote[32]+'|||'+vote[33]+'|||'+vote[36]
	print
	print "ASSIGNED IN ERROR"
	for vote in [row for row in data if str(row[6])!=str(code) and str(row[7])==str(code)]:
		print str(vote[6])+'|||'+str(vote[7])+'|||'+vote[2]+'|||'+vote[3]+'|||'+vote[32]+'|||'+vote[33]+'|||'+vote[36]


def discrep_table(data):
	temp=list(set([int(row[7]) for row in data]))
	temp2=list(set([int(row[6]) for row in data]))
	temp=list(set(temp+temp2))
	temp.sort()
	print 'NEW VOTES'
	print ' ',
	for code in temp:
		print code,
	print
	for code in temp:
		print code,
		for code2 in temp:
			print len([row for row in data if int(row[6])==code2 and int(row[7])==code]),
		print


def classify_question(question,bill_title,votetype,amendment,amendment_to_amendment_number,amendment_to_amendment_to_amendment_number,test=0):
	"""Takes three strings associated with a vote and classifies the vote. If more than one classification
	is found or not classification is found, will classify the vote as '?'."""
	dict={}
	if test==1:
		print question
		print bill_title
		print votetype
	# if 'table' not in question and 'previous question' not in question and 'substitute' not in question:
	# 1: constitutional amendments
	if 'amendment to constitution' in question or 'amendment to the constitution' in question and 'sense of senate' not in question:
		dict['1']=1
	# 11: final passage/adoption of a bill
	if 'on passage of bill' in question and (votetype=='hr' or votetype=='s') and 'conference report' not in question:
		dict['11']=1
	# 12: Final Passage/Adoption of Conference Report 
	if 'on conference report' in question and 'motion to' not in question:
		dict['12']=1
	# 13: Final Passage/Adoption of Resolution 
	if ('on resolution' in question and votetype=='sres') or (votetype=='sres' and 'on passage of bill' in question):
		dict['13']=1
	# 14: Final Passage/Adoption of Joint Resolution
	if 'on joint resolution' in question and (votetype=='hjres' or votetype=='sjres') and 'amendment to constitution' not in question:
		dict['14']=1
	# 17: Final Passage/Adoption of Concurrent Resolution 
	if ('on concurrent resolution' in question or 'on resolution' in question or 'on passage of bill' in question) and (votetype=='hconres' or votetype=='sconres'):
		dict['17']=1
	if amendment!='' and 'on decision of chair' not in question and 'germane' not in question and 'motion to concur' not in question and 'motion to strike' not in question and 'strike condition' not in question and 'reconsider' not in question and 'suspend rule' not in question and 'suspend paragraph' not in question and 'point of order' not in question and 'motion to waive' not in question:
		dict['21']=1
		# 23: Substitute (to an amendment) 
		if 'substitute' in question:
			dict['23']=1
		# 24: Motion to Table Amendment 
		if 'on motion to table' in question:
			dict['24']=1
		25: Amendment to Amendment to Substitute 
		if '' in question:
			dict['25']=1
		26: Perfecting Amendment 
		if 'perfecting nature' in question:
			dict['26']=1
		if len(dict)==0:
			# 21: Straight Amendments (includes en bloc & amendments in the nature of a substitute) 
			if amendment.count('samdt')==1:
				dict['21']=1
			# 22: Amendments to Amendments 
			if amendment.count('samdt')>1:
				dict['22']=1
			# 27: Amendment to Substitute 
			if '' in question:
				dict['27']=1
	# 30: Passage over Presidential Veto 
	if 'on overriding veto' in question:
		dict['30']=1
	# 34: Treaty Ratification 
	if 'resolution of ratification' in question:
		dict['34']=1
	# 52: Judgment of the Senate 
	# if 'on decision of chair' in question and 'appeal' not in question:
	# 	dict['52']=1
	# 54: Motion to Suspend Senate Rules
	if ('motion to suspend rule' in question or 'motion to waive rule' in question or 'motion to suspend paragraph' in question) and votetype!='na':
		dict['54']=1
	# 56: Motion to Discharge 
	if 'motion to discharge' in question:
		dict['56']=1
	# 57: Point of Order 
	if 'on point of order' in question:
		dict['57']=1
	# 58: Motion to Go into Executive Committee 
	if 'motion to proceed to executive session' in question:
		dict['58']=1
	# # 60: Motion to Waive Gramm-Rudman Requirements
	# if '' in question:
	# 	dict['60']=1
	# 61: Budget Waivers
	if 'motion to table' not in question and 'motion to waive' in question or 'waive cba' in question or 'waive cbr' in question or 'wave cba' in question or ('waive' in question and 'budget' in question) or ('waive' in question and 'internal revenue' in question):
		dict['61']=1
	# 62: Invoke cloture
	if 'cloture motion' in question or question[0:10]=='on cloture':
		dict['62']=1
	# 63: Motion to Reconsider 
	if 'motion to reconsider' in question and ('motion to table' not in question or ('motion to table' in question and question.index('motion to table')>question.index('motion to reconsider'))):
		dict['63']=1
	# # 64: Motion to Waive 
	# if '' in question:
	# 	dict['64']=1
	# 65: Confirmation 
	if question[0:13]=='on nomination':
		dict['65']=1
	# 66: Motion to Proceed 
	if 'motion to proceed' in question[0:30] and 'executive session' not in question and 'conference report' not in question and 'conf rpt' not in question:
		dict['66']=1
	# 67: Appeal of the chair's ruling
	if 'on decision of chair' in question:
		dict['67']=1
	# 72: Motion to Recommit to Conference 
	if 'motion to recommit' in question[0:30] and 'to conference' in question:
		dict['72']=1
	# 74: Motion to Postpone 
	if 'motion to postpone' in question[0:40]:
		dict['74']=1
	# 79: Motion to Disagree 
	if 'motion to disagree' in question[0:40]:
		dict['79']=1
	# 82: Motion to Recede
	if 'motion to recede' in question[0:40]:
		dict['82']=1
	# 83: Motion to Commit
	if 'motion to commit' in question[0:50] and 'motion to table' not in question:
		dict['83']=1
	# 87: Motion to Refer 
	if 'motion to refer' in question[0:40]:
		dict['87']=1
	# 90: Motion to Strike
	if 'motion to strike' in question or 'to strike condition' in question:
		dict['90']=1
	# 92: Motion to Adjourn 
	if 'motion to adjourn' in question[0:30]:
		dict['92']=1
	# 93: Motion to Recommit (Note: Recommit to Conference is 72)
	if 'motion to recommit' in question[0:50] and 'to conference' not in question and 'motion to table' not in question:
		dict['93']=1
	# 95: Motion to Instruct Conferees 
	if 'motion to instruct conferees' in question and 'motion to table' not in question:
		dict['95']=1
	# 96: Motion to Table
	###### ALERT REVISIT #########
	if 'motion to table' in question and amendment=='':
		dict['96']=1
	# 97: Motion to Recede and Concur (also includes motion to concur)
	if 'motion to concur' in question[0:150] and 'motion to waive' not in question or ('motion to concur' in question and 'motion to table' in question and question.find('motion to concur')<question.find('motion to table')):
		dict['97']=1
	# # 111: Adjourn to a day certain
	# if 'motion to adjourn' in question:
	# 	dict['111']=1
	# 112: Recess
	if 'motion to recess' in question[0:40]:
		dict['112']=1
	# 124: Compel Attendance by Absentees
	if 'motion to instruct sgt' in question or 'motion to instruct sergeant' in question or 'motion for attendance' in question:
		dict['124']=1
	# 128: Proceed to Consideration of Conference Report
	if 'motion to proceed' in question and ('conference report' in question or 'conf rpt' in question):
		dict['128']=1
	# 134: Engrossment and Third Reading
	if 'third time?' in question or 'third reading?' in question:
		dict['134']=1
	# 138: Determine Germaneness
	if 'germane' in question or 'germaine' in question:
		dict['138']=1
	# # 191: Rules of Evidence Impeachment
	# if '' in question:
	# 	dict['191']=1
	# # 192: Rules of Trial Impeachment
	# if '' in question:
	# 	dict['192']=1
	# 193: Guilt or Innocence Impeachment
	if 'articles of impeachment' in question or 'resolution impeaching' in question:
		dict['193']=1
	if len(dict.keys())>1:
		final='999'
	if len(dict.keys())==1:
		final=dict.keys()[0]
	if len(dict.keys())==0:
		final='69'
	if 'on cloture motion' in question or 'motion to invoke cloture' in question:
		final='62'
	if test==1:
		print dict
	return final














