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
# 34: result
# 35: url
# 36: title

# show a code and associated fields
def show_code(code,data):
	temp=[vote for vote in data if int(vote[6])==code]
	for vote in temp:
		print vote[2]+'|||'+vote[3]+'|||'+vote[32]+'|||'+vote[33]+'|||'+vote[36]
		print

def code_votes_senate(data,test=0):
	for row in data:
		question=strip(row[33])
		bill_title=strip(row[36])
		votetype=strip(row[30])
		code=classify_question(question,bill_title,votetype,test=test)
		row[7]=code
	return data

def classify_question(question,bill_title,votetype,test=0):
	"""Takes three strings associated with a vote and classifies the vote. If more than one classification
	is found or not classification is found, will classify the vote as '?'."""
	dict={}
	print bill_title
	print votetype
	if 'table' not in question and 'previous question' not in question and 'substitute' not in question:
		# 1: constitutional amendments
		if '' in question:
			dict['1']=1
		# 11: final passage/adoption of a bill
		if '' in question:
			dict['11']=1
		# 12: Final Passage/Adoption of Conference Report 
		if '' in question:
			dict['12']=1
		# 13: Final Passage/Adoption of Resolution 
		if '' in question:
			dict['13']=1
		# 14: Final Passage/Adoption of Joint Resolution
		if '' in question:
			dict['14']=1
		# 17: Final Passage/Adoption of Concurrent Resolution 
		if '' in question:
			dict['17']=1
		# 21: Straight Amendments (includes en bloc & amendments in the nature of a substitute) 
		if '' in question:
			dict['21']=1
		# 22: Amendments to Amendments 
		if '' in question:
			dict['22']=1
		# 23: Substitute (to an amendment) 
		if '' in question:
			dict['23']=1
		# 24: Motion to Table Amendment 
		if '' in question:
			dict['24']=1
		# 25: Amendment to Amendment to Substitute 
		if '' in question:
			dict['25']=1
		# 26: Perfecting Amendment 
		if '' in question:
			dict['26']=1
		# 27: Amendment to Substitute 
		if '' in question:
			dict['27']=1
		# 30: Passage over Presidential Veto 
		if '' in question:
			dict['30']=1
		# 34: Treaty Ratification 
		if '' in question:
			dict['34']=1
		# 48: 
		if '' in question:
			dict['48']=1
		# 52: Judgment of the Senate 
		if '' in question:
			dict['52']=1
		# 54: Motion to Suspend Senate Rules
		if '' in question:
			dict['54']=1
		# 56: Motion to Discharge 
		if '' in question:
			dict['56']=1
		# 57: Point of Order 
		if '' in question:
			dict['57']=1
		# 58: Motion to Go into Executive Committee 
		if '' in question:
			dict['58']=1
		# 60: Motion to Waive Gramm-Rudman Requirements
		if '' in question:
			dict['60']=1
		# 61: Budget Waivers
		if '' in question:
			dict['61']=1
		# 62: Motion to Invoke Cloture
		if '' in question:
			dict['62']=1
		# 63: Motion to Reconsider 
		if '' in question:
			dict['63']=1
		# 64: Motion to Waive 
		if '' in question:
			dict['64']=1
		# 65: Confirmation 
		if '' in question:
			dict['65']=1
		# 66: Motion to Proceed 
		if '' in question:
			dict['66']=1
		# 67: Appeal of the Chair’s Ruling
		if '' in question:
			dict['67']=1
		# 69: miscellaneous
		if '' in question:
			dict['69']=1
		# 72: Motion to Recommit to Conference 
		if '' in question:
			dict['72']=1
		# 74: Motion to Postpone 
		if '' in question:
			dict['74']=1
		# 79: Motion to Disagree 
		if '' in question:
			dict['79']=1
		# 82: Motion to Recede
		if '' in question:
			dict['82']=1
		# 83: Motion to Commit
		if '' in question:
			dict['83']=1
		# 84: Motion to Consider
		if '' in question:
			dict['84']=1
		# 87: Motion to Refer 
		if '' in question:
			dict['87']=1
		# 90: Motion to Strike
		if '' in question:
			dict['90']=1
		# 92: Motion to Adjourn 
		if '' in question:
			dict['92']=1
		# 93: Motion to Recommit (Note: Recommit to Conference is 72)
		if '' in question:
			dict['93']=1
		# 95: Motion to Instruct Conferees 
		if '' in question:
			dict['95']=1
		# 96: Motion to Table
		if '' in question:
			dict['96']=1
		# 97: Motion to Recede and Concur (also includes motion to concur)
		if '' in question:
			dict['97']=1
		# 111: Adjourn to a day certain
		if '' in question:
			dict['111']=1
		# 112: Recess
		if '' in question:
			dict['112']=1
		# 113: Executive Session
		if '' in question:
			dict['113']=1
		# 124: Compel Attendance by Absentees
		if '' in question:
			dict['124']=1
		# 128: Proceed to Consideration of Conference Report
		if '' in question:
			dict['128']=1
		# 134: Engrossment and Third Reading
		if '' in question:
			dict['134']=1
		# 138: Determine Germaneness
		if '' in question:
			dict['138']=1
		# 191: Rules of Evidence Impeachment
		if '' in question:
			dict['191']=1
		# 192: Rules of Trial Impeachment
		if '' in question:
			dict['192']=1
		# 193: Guilt or Innocence Impeachment
		if '' in question:
			dict['193']=1
	if len(dict.keys())>1:
		final='?'
	if len(dict.keys())==1:
		final=dict.keys()[0]
	if len(dict.keys())==0:
		final='69'
	if test==1:
		print dict
	return final














