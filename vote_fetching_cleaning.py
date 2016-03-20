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

server_file_location='/home/austinc/public_html/rohde_rollcalls/votes.csv'
southern_states=['AL','AR','FL','GA','KY','LA','MS','NC','OK','SC','TN','TX','VA']

def geturl(url):
	try:
		return urllib2.urlopen(url).read()
	except:
		time.sleep(20)
		print 'connection problem'
		geturl(url)


def scrape_votes(existing_file):
	"""The work horse function - looks for new votes and codes them. Takes a csv file of votes
	that have already been coded so it doesn't duplicate work."""

	with open(existing_file,'rU') as csvfile:
		reader=csv.reader(csvfile)
		data=[row for row in reader]

	csvfile=open(existing_file,'a')
	writer=csv.writer(csvfile)

	compare_votes=[[int(row[2]),int(row[3])]for row in data[1:]]
	new_votes=[]

	# Iterate through years from 1989 to present (Thomas only has votes >1989)
	current_year=datetime.date.today().year
	for year in range(1989,current_year+1,1):
		print year
		url='http://clerk.house.gov/evs/%s/index.asp' % (year)
		
		try:
			vote=urllib2.urlopen(url).read()
		except:
			pass

		# Assemble list of all pages containing votes for this congress
		votepage_finder=re.compile('<A HREF="(.*?)">Roll Calls .*? Thru .*?</A><BR>')
		pages=votepage_finder.findall(vote)
		vote_pages=[]
		for vote_page in pages:
			vote_pages.append(vote_page)

		# Iterate through pages and collect all votes
		# compare against existing file to see if the vote is already in the database
		for page in vote_pages:
			print page
			url='http://clerk.house.gov/evs/%s/%s' % (year,page)
			votepage=urllib2.urlopen(url).read()
			vote_finder=re.compile('<TR><TD><A HREF="http://clerk.house.gov/cgi-bin/vote.asp\?year=.*?&rollnumber=.*?">(.*?)</A></TD>')
			fullvote_finder=re.compile('<TR><TD><A HREF="http://clerk.house.gov/cgi-bin/vote.asp\?year=.*?&rollnumber=.*?">(.*?)</A></TD>\r\n<TD><FONT FACE="Arial" SIZE="-1">.*?</FONT></TD>\r\n<TD><FONT FACE="Arial" SIZE="-1">\r\n<A HREF="(.*?)">.*?</A>\r\n</FONT></TD>\r\n<TD><FONT FACE="Arial" SIZE="-1">.*?</FONT></TD>\r\n<TD ALIGN="CENTER"><FONT FACE="Arial" SIZE="-1">.*?</FONT></TD>\r\n<TD><FONT FACE="Arial" SIZE="-1">.*?</FONT></TD></TR>')
			# 0 is roll call number, 1 is thomas page for the bill, might not be a link
			votes=vote_finder.findall(votepage)
			fullvotes=fullvote_finder.findall(votepage)

			# new 
			# <TR><TD><A HREF="http://clerk.house.gov/cgi-bin/vote.asp\?year=.*?&rollnumber=.*?">(.*?)</A></TD>\r\n<TD><FONT FACE="Arial" SIZE="-1">.*?</FONT></TD>\r\n<TD><FONT FACE="Arial" SIZE="-1">\r\n<A HREF="(.*?)">.*?</A>\r\n</FONT></TD>\r\n<TD><FONT FACE="Arial" SIZE="-1">.*?</FONT></TD>\r\n<TD ALIGN="CENTER"><FONT FACE="Arial" SIZE="-1">.*?</FONT></TD>\r\n<TD><FONT FACE="Arial" SIZE="-1">.*?</FONT></TD></TR>
			# http://thomas.loc.gov/cgi-bin/bdquery/z?d107:h.res.00428:
			# http://thomas.loc.gov/cgi-bin/bdquery/z?d107:HE00428:@@@X

			for vote in votes:
				if [year,int(vote)] not in compare_votes:
					print vote
					vote_s="%03d" % (int(vote))
					url='http://clerk.house.gov/evs/%s/roll%s.xml' % (year,vote_s)
					rollcall=geturl(url)

					# Go to all actions page for the legislation, find the action that includes the roll call, save the full text into question2
					question2=''
					amendment2=''
					amendment3=''
					amendment=''
					for fullvote in fullvotes:
						if int(vote)==int(fullvote[0]):
							bill_details=geturl(fullvote[1])
							bill_title_finder=re.compile('<b>Latest Title:</b>(.*?)\n')
							all_action_finder=re.compile('<a href="(.*?)">All Congressional Actions\n</a>')
							all_action_amendment_finder=re.compile('<a href="(.*?)">All Congressional Actions with Amendments</a>')
							action_page=all_action_finder.findall(bill_details)
							amend_page=all_action_amendment_finder.findall(bill_details)

							try:
								bill_title=bill_title_finder.findall(bill_details)[0]
							except:
								bill_title=''

							if len(amend_page)>0:
								page=amend_page[0]
							else:
								page=action_page[0]

							try:
								action_url='http://thomas.loc.gov'+page
								actions=geturl(action_url)
								action_finder=re.compile('<strong>.*?</strong><dd>(.*?)(?:\n<dt>|\n</dl>)',re.DOTALL)
								amendment_finder=re.compile('<a href="/cgi-bin/bdquery/(.*?)">')
								# '<dt><strong>.*?</strong><dd>(.*?<a href=".*?">.*?</a>'
								all_actions=action_finder.findall(actions)
								for action in all_actions:
									if url in action:
										question2=action
										if len(amendment_finder.findall(question2))>0:
											amendment_url='http://thomas.loc.gov/cgi-bin/bdquery/%s' % (amendment_finder.findall(question2)[0])
											amendment_page=geturl(amendment_url)
											purpose_finder=re.compile('<p>AMENDMENT PURPOSE:<br />(.*?)\n')
											amdesc_finder=re.compile('<p>AMENDMENT DESCRIPTION:<br />(.*?)\n')
											try:
												amendment2=purpose_finder.findall(amendment_page)[0]
											except:
												amendment2=''
											try:
												amendment3=amdesc_finder.findall(amendment_page)[0]
											except:
												amendment3=''
							except:
								pass

					# define various regular expressions
					congress_finder=re.compile('<congress>(.*?)</congress>')
					session_finder=re.compile('<session>(.)..</session>')
					vote_totals=re.compile('<total-stub>Totals</total-stub>\r\n<yea-total>(.*?)</yea-total>\r\n<nay-total>(.*?)</nay-total>')
					rep_totals=re.compile('<party>Republican</party>\r\n<yea-total>(.*?)</yea-total>\r\n<nay-total>(.*?)</nay-total>')
					dem_totals=re.compile('<party>Democratic</party>\r\n<yea-total>(.*?)</yea-total>\r\n<nay-total>(.*?)</nay-total>')
					leg_finder=re.compile('<legislator .*?party="(.*?)" state="(.*?)" role="legislator">.*?</legislator><vote>(.*?)</vote>')
					legis_num_finder=re.compile('<legis-num>(.*?)</legis-num>')
					question_finder=re.compile('<vote-question>(.*?)</vote-question>')
					amend_author=re.compile('<amendment-author>(.*?)</amendment-author>')
					vote_desc=re.compile('<vote-desc>(.*?)</vote-desc>')

					congress=congress_finder.findall(rollcall)[0]
					session=session_finder.findall(rollcall)[0]
					try:
						totalvotes=int(vote_totals.findall(rollcall)[0][0])+int(vote_totals.findall(rollcall)[0][1])
						ayes=int(vote_totals.findall(rollcall)[0][0])
						nays=int(vote_totals.findall(rollcall)[0][1])
						dayes=int(dem_totals.findall(rollcall)[0][0])
						dnays=int(dem_totals.findall(rollcall)[0][1])
						rayes=int(rep_totals.findall(rollcall)[0][0])
						rnays=int(rep_totals.findall(rollcall)[0][1])
					except:
						pass
					legislators=leg_finder.findall(rollcall)
					try:
						legislation=legis_num_finder.findall(rollcall)[0]
					except:
						legislation='Speaker'
					amendment=amend_author.findall(rollcall)
					votetype=vote_desc.findall(rollcall)
					question=question_finder.findall(rollcall)[0]
					# question=q_finder.findall(vote)[0]
					question=question.lower()
					question=question.replace('the','')
					question=question.replace(',','')
					question=question.replace('.','')
					question=question.replace('  ',' ')
					question=question.strip()

					legislation=legislation.upper()
					legislation=legislation.replace(' ','')
					legislation=legislation.replace('.','')
					billtype=re.compile('([A-Z]{1,6})')
					billnumb=re.compile('([0-9]{1,6})')
					try:
						bill_type=billtype.findall(legislation)[0]
					except:
						bill_type=''
					try:
						bill_numb=billnumb.findall(legislation)[0]
					except:
						bill_numb=''
					try:
						amendment=amendment[0]
					except:
						amendment=''
					try:
						votetype=votetype[0]
					except:
						votetype=''
					# try:
					# 	question=question[0]
					# except:
					# 	question=''

					if question=='ELECTION OF SPEAKER':
						cand_finder=re.compile('<totals-by-candidate><candidate>(.*?)</candidate><candidate-total>(.*?)</candidate-total></totals-by-candidate>')
						candidates=cand_finder.findall(rollcall)
						candidate1=candidates[0][0]
						candidate2=candidates[0][1]
						ayes=candidates[0][1]
						nays=candidates[1][1]
						dayes=0
						dnays=0
						rayes=0
						rnays=0

						totalvotes=0
						for cand in candidates:
							totalvotes=totalvotes+int(cand[1])

					# tally up north/south dems, north/south repubs
					ndayes=0
					ndnays=0
					sdayes=0
					sdnays=0
					nrayes=0
					nrnays=0
					srayes=0
					srnays=0
					# legs are [party,state,vote]
					for leg in legislators:
						if leg[0]=='D':
							if leg[1] not in southern_states:
								if leg[2]=='Yea':
									ndayes=ndayes+1
								if leg[2]=='Nay' or leg[2]=='No':
									ndnays=ndnays+1
							if leg[1] in southern_states:
								if leg[2]=='Yea':
									sdayes=sdayes+1
								if leg[2]=='Nay' or leg[2]=='No':
									sdnays=sdnays+1

						if leg[0]=='R':
							if leg[1] not in southern_states:
								if leg[2]=='Yea':
									nrayes=nrayes+1
								if leg[2]=='Nay' or leg[2]=='No':
									nrnays=nrnays+1
							if leg[1] in southern_states:
								if leg[2]=='Yea':
									srayes=srayes+1
								if leg[2]=='Nay' or leg[2]=='No':
									srnays=srnays+1


					unity=0
					try:
						if ((dayes/(dayes+dnays))>.5 and (rnays/(rayes+rnays))>.5) or ((dnays/(dayes+dnays))>.5 and (rayes/(rayes+rnays))>.5):
							unity=1
					except:
						pass

					unanimous=0
					try:
						if (ayes/(ayes+nays))>.9 or (nays/(ayes+nays))>.9:
							unanimous=1
					except:
						pass

					coalition=0
					try:
						if ((ndayes/(ndayes+ndnays))>.5 and (rnays/(rayes+rnays))>.5 and (sdnays/(sdayes+sdnays))>.5) or ((ndnays/(ndayes+ndnays))>.5 and (rayes/(rayes+rnays))>.5 and (sdayes/(sdayes+sdnays))>.5):
							coalition=1
					except:
						pass

					ndr=0
					try:
						if ((ndayes/(ndayes+ndnays))>.5 and (rnays/(rayes+rnays))>.5) or ((ndnays/(ndayes+ndnays))>.5 and (rayes/(rayes+rnays))>.5):
							ndr=1
					except:
						pass

					try:
						votecode=classify_question(question,question2,bill_title,amendment,votetype,bill_type,amendment2,amendment3)

						row=[congress,session,year,vote,'','',votecode,'','','',
							totalvotes,ayes,nays,dayes,dnays,rayes,rnays,ndayes,ndnays,sdayes,sdnays,nrayes,
							nrnays,srayes,srnays,unity,coalition,unanimous,ndr,bill_type,bill_numb,
							question,amendment,votetype,url,question2,bill_title,amendment2,amendment3]	
						code_votes([row])
						print url
						print row
						writer.writerow(row)

					except:
						print 'Bad vote: '+ str(congress) + ' ' + str(session) + ' ' + str(year) + ' ' + str(vote)


def output_training_votes(file_path='/Users/austinc/Desktop/votes.csv',target_file='/Users/austinc/Desktop/type_examples.csv'):
	"""Takes the Rohde dataset, finds the Thomas URL for each vote, checks the 'question' field, returns all possible texts
	for each vote code. Returns a dictionary. Run the find_conflicts function on the dictionary to find instances where a
	string from Thomas is used for more than one code.

	Don't use this."""

	with open(file_path,'rU') as csvfile:
		reader=csv.reader(csvfile)
		data=[row for row in reader]

	vote_codes=set([row[6] for row in data[1:]])
	vote_dict={}
	count=0
	for code in vote_codes:
		vote_dict[code]={}

	# Construct URL
	not_av=re.compile('(Roll call vote not available)')
	for row in data[1:]:
		print round((count/len(data[1:]))*100,1)
		count=count+1
		url='http://clerk.house.gov/cgi-bin/vote.asp?year=%s&rollnumber=%s' % (row[2],row[3])
		vote=download(url)

		# Thomas does not have roll calls prior to 1989.
		if len(not_av.findall(vote))!=1:
			q_finder=re.compile('<vote-question>(.*?)</vote-question>')
			question=q_finder.findall(vote)[0]
			question=question.lower()
			question=question.replace('the','')
			question=question.replace(',','')
			question=question.replace('.','')
			question=question.replace('  ',' ')
			question=question.strip()

			if question not in vote_dict[row[6]]:
				vote_dict[row[6]][question]=[url]
			if question in vote_dict[row[6]]:
				vote_dict[row[6]][question].append(url)

	return vote_dict


def download(url):
	try:
		vote=urllib2.urlopen(url).read()
		return vote
	except:
		time.sleep(20)
		print 'delay'
		download(url)


def strip(text):
	text=text.lower()
	text=text.replace('the','')
	text=text.replace(',','')
	text=text.replace('.','')
	text=text.replace('  ',' ')
	text=text.strip()
	return text


def find_conflicts(rows):
	"""Returns a dict that is useful for examining how questions and codes are related"""
	conflict_dict={}
	for row in rows:
		question=row[31]
		if question not in conflict_dict.keys():
			conflict_dict[question]={}
			conflict_dict[question][row[6]]=1
		if question in conflict_dict.keys():
			if row[6] not in conflict_dict[question].keys():
				conflict_dict[question][row[6]]=0
			if row[6] in conflict_dict[question].keys():
				conflict_dict[question][row[6]]=conflict_dict[question][row[6]]+1

	return conflict_dict


def fix_contvotes(data):
	"""Correctly determines the contvote number for a series of votes with non-cont numbers"""
	years=list(set([row[2] for row in data[1:]]))
	yeardict={}
	for year in years:
		votenums=[int(row[3]) for row in data if row[2]==year]
		yeardict[year]=max(votenums)

	for row in data[1:]:
		if int(row[2])%2==0:
			try:
				row[4]=str(int(row[3])+int(yeardict[str(int(row[2])-1)]))
			except:
				pass
		else:
			row[4]=row[3]

	return data


def code_votes(data,test=0):
	"""Take a set of rows and code each vote"""
	for row in data:
		# ['cong', 'session', 'year', 'v1ex', 'vote', 'voteview', 'vote', 'issue', 'pres', 'revote', 'total', 'v2', 'v3', 'v4', 'v5', 'v6', 'v7', 'v8', 'v9', 'v10', 'v11', 'v12', 'v13', 'v14', 'v15', 'v16', 'v17', 'v18', 'v19', 'billtype1', 'billnum1', 'question', 'amendment', 'votetype', 'url', 'question2', 'bill_title', 'amendment2', 'amendment3']
		question=strip(row[31])
		question2=strip(row[35])
		bill_title=strip(row[36])
		amendment=row[32]
		votetype=strip(row[33])
		billtype=row[29]
		amendment2=row[37]
		amendment3=row[38]

		code=classify_question(question,question2,bill_title,amendment,votetype,billtype,amendment2,amendment3,test=test)

		row[6]=code

	return data

def classify_question(question,question2,bill_title,amendment,votetype,billtype,amendment2,amendment3,test=0):
	"""Takes three strings associated with a vote and classifies the vote. If more than one classification
	is found or not classification is found, will classify the vote as '?'."""
	dict={}
	print bill_title
	print votetype

	if 'table' not in question and 'previous question' not in question and 'substitute' not in question:

		# 30: 'on presidential veto' OR 'objections' OR 'objection of president'
		if 'on presidential veto' in question or 'objections' in question or 'objection of president' in question:
			dict['30']=1

		# 56: 'motion to discharge' and NOT 'table'
		if 'motion to discharge' in question:
			dict['56']=1

		# 193: 'article i'
		if 'article i' in question:
			dict['193']=1

		# 63: 'motion to reconsider' and NOT 'table'
		# if 'motion to reconsider' in question or ('sustain' in question and 'chair' in question):
		if 'motion to reconsider' in question:
			dict['63']=1

		# 83: 'commit' AFTER performing a split on space
		if 'commit' in question.split(' '):
			dict['83']=1

		# 82: 'recede' NOT 'recede and concur' 
		if 'recede' in question and 'concur' not in question:
			dict['82']=1

		# 66: 'proceed in order' NOT 'table'
		if 'proceed in order' in question:
			dict['66']=1

		# 67: 'sustain' AND 'chair'
		if 'sustain' in question and 'chair' in question:
			dict['67']=1

		# 89: 'election' AND 'speaker'
		if 'election' in question and 'speaker' in question:
			dict['89']=1

		# 33: 'conference report' AND ('suspend the rules' OR 'suspend rules')
		if 'conference report' in question and ('suspend rules' in question or 'suspend rules' in question):
			dict['33']=1

		# 85: 'ordering a second'
		if 'ordering a second' in question:
			dict['85']=1

		# 87: ('motion to refer' NOT 'table' NOT 'previous question') OR 'refer bill'
		if 'motion to refer' in question or 'refer bill' in question:
			dict['87']=1

		# 84: ('consider' OR 'consideration' after a split on space) AND (NOT 'postpone' or 'postponing')
		if ('consider' in question.split(' ') or 'consideration' in question.split(' ')) and 'postpone' not in question and 'postponing' not in question:
			dict['84']=1

		# 9: 'call of the house'
		if 'call of house' in question:
			dict['9']=1

		# 77: 'rise' NOT ('strike' OR 'stricken' OR 'striking')
		if 'rise' in question and 'strike' not in question and 'stricken' not in question and 'striking' not in question:
			dict['77']=1

		# 90: 'strike' OR 'striking' OR 'stricken'
		if 'strike' in question or 'striking' in question or 'stricken' in question:
			dict['90']=1

		# 91: 'on approving the journal' NOT 'table'
		if 'on approving journal' in question:
			dict['91']=1

		# 92: '' OR 'adjourn' NOT 'table'
		if 'adjourn' in question:
			dict['92']=1

		# 76: 'limit debate' NOT 'table'
		if 'limit debate' in question:
			dict['76']=1

		# 74: 'postpo'
		if 'postpo' in question:
			dict['74']=1

		# 94: 'resolve into committee' OR 'resolving into committee' NOT 'table'
		if 'resolve into committee' in question or 'resolving into committee' in question:
			dict['94']=1

		# 79: 'disagree' NOT 'table' NOT 'recede'
		if ('disagree' in question or 'go to conference' in question) and 'recede' not in question:
			dict['79']=1

		# 72: 'recommit' AND 'conference report' NOT 'table' AND 'conference' in question2
		if ('recommit' in question and 'conference report' in question and 'conference' in question2) or ('recommit' in question and 'conference' in question2):
			dict['72']=1

		# 93: 'recommit' NOT 'conference report' NOT 'table' NOT 'previous question' NOT 'conference' in question2
		if 'recommit' in question and 'conference report' not in question and 'conference' not in question2:
			dict['93']=1

		# 95: 'conferees' NOT 'table' NOT 'previous question' NOT 'substitute' NOT ('authorizing' OR 'authorize')
		if 'conferees' in question and 'authorizing' not in question and 'authorize' not in question:
			dict['95']=1

		# 12: 'agreeing' AND 'conference report' NOT 'table' NOT 'previous question'
		if 'agreeing' in question and 'conference report' in question:
			dict['12']=1

		# 68: 'suspend rules' AND 'senate amendment'
		if 'suspend rules' in question and 'senate amendment' in question:
			dict['68']=1

		# 80: 'agreeing to amendment' AND 'providing for consideration' in bill_title
		if 'agreeing to amendment' in question and 'providing for consideration of bill' in bill_title:
			dict['80']=1

		# 73: 'senate amendment' and 'agree' NOT 'suspend rules' or 'with'
		if 'senate amendment' in question and 'suspend rules' not in question and 'agree' in question and 'with' not in question:
			dict['73']=1

		# 14: 'on passage' or 'agreeing to resolution' AND 'HJRES' in billtype NOT suspend
		if ('on passage' in question or 'agreeing to resolution' in question) and 'suspend' not in question and (billtype=='HJRES' or billtype=='SJRES') and 'constitution' not in bill_title and '30' not in dict.keys() and 'constitution' not in votetype:
			dict['14']=1

		# 16: 'HJRES' or 'SJRES' and 'passage' or 'agreeing' and 'suspend'
		if ('on passage' in question or 'agreeing to resolution' in question or 'and pass' in question) and 'suspend' in question and (billtype=='HJRES' or billtype=='SJRES') and 'constitution' not in bill_title:
			dict['16']=1

		# 11: 'on passage' NOT 'HJRES' in billtype NOT ('constitution' AND 'amendment' in votetype)
		if 'on passage' in question and billtype!='HJRES' and billtype!='SJRES' and 'constitution' not in question2 and '30' not in dict.keys():
			dict['11']=1

		# 97: 'recede and concur' or 'motion to concur' but also like 73 with 'with'
		if '68' not in dict.keys() and 'concurrent' not in question and ('concur' in question or ('senate amendment' in question and 'suspend rules' not in question and 'with' in question) or 'motion to concur' in question or 'concur in the Senate amendment' in question2):
			dict['97']=1

		# 81: 'providing for consideration' or 'providing for further' in votetype, 'agreeing to resolution' in question 
		if 'agreeing to resolution' in question and ('providing for' in votetype or 'waiving' in votetype or 'consideration of' in votetype) and billtype=='HRES':
			dict['81']=1

		# 13: CODE:  13 --- see 81 but in short 'agreeing to the resolution' + NOT already classified as 81, pending resolution of issue sent to mike - also 'adoption' + 'resolution' NOT 'suspend' also billtype is HRES
		if '81' not in dict.keys() and ('agreeing to resolution' in question or ('adoption' in question and 'resolution' in question)) and 'suspend' not in question and billtype=='HRES':
			dict['13']=1

		# 17: 'agreeing' NOT 'suspend' billtype is 'HCONRE' or 'SCONRE' and 'conference report' not in question
		if 'agreeing' in question and 'suspend' not in question and (billtype=='SCONRE' or billtype=='HCONRE') and 'amendment' not in question and 'conference report' not in question:
			dict['17']=1

		# 18: 'suspend' and 'agree' billtype is 'HCONRE' or 'SCONRE'
		if 'suspend' in question and 'agree' in question and (billtype=='SCONRE' or billtype=='HCONRE') and 'constitution' not in bill_title:
			dict['18']=1

		# 15: 'suspend' and 'pass' or 'agree' NOT 'conference report' and billtype is 'HR' or 'S'
		if 'conference report' not in question and 'suspend' in question and ('pass' in question or 'agree' in question) and (billtype=='HR' or billtype=='S') and 'senate amendment' not in question:
			dict['15']=1

		# 1: 'amendment' and 'constitution' in question2 and not 91 for whatever reason
		if ('amendment to constitution' in bill_title or 'constitutional amendment' in bill_title) and len(dict.keys())==0:
			dict['1']=1

		# 19: analog to 13 but with suspension. 'suspend' + 'HRES' + ('agree' or 'pass')
		if 'suspend' in question and billtype=='HRES' and ('agree' in question or 'pass' in question):
			dict['19']=1

		# 31: 
		if 'adopting first article' in question or 'agreeing to sec 1' in question:
			dict['31']=1

		# 32:
		if 'adopting second article' in question or 'adopting third article' in question or 'adopting fourth article' in question or 'adopting fifth article' in question:
			dict['32']=1

		# amendments: these are tricky because they look almost identical to one another and it's also a bit difficult to
		# distinguish them from other votes easily. One possibility is to check for the presence of amendment2/3 ie
		# amendment2!=''. Some other votes that are not amendments occasionally pick up amendment2/3 fields however
		# (update: this is a bug, should be fixed now) so the best thing is probably to see if a vote hasn't been coded
		# yet AND has an amendment2 field.
		if len(dict.keys())==0 and (amendment!=''):

			# 27: 'to' AND 'substitute' in amendment
			if ' to ' in amendment and 'substitute' in amendment:
				dict['27']=1

			# 23: 'substitute' in amendment OR 'substitute' in amendment2 AND 'nature' not in amendment2 AND 'nature' not in amendment
			if 'substitute' in amendment and ' to ' not in amendment:
				dict['23']=1

			# 22: 'amendment to [A-Z].*? ' in amendment - amendment 3 is pretty similar here
			if ' to ' in amendment and 'substitute' not in amendment:
				dict['22']=1

			# 21: all other amendments and NOT 'committees to sit'
			if len(dict.keys())==0 and 'committees to sit' not in question:
				dict['21']=1

	# 99: 'previous question' and 'providing for consideration' in votetype
	if 'previous question' in question and ('providing for' in bill_title or 'waiving' in bill_title):
		dict['99']=1

	# 88: 'previous question'
	if 'previous question' in question and 'providing for' not in bill_title and 'waiving' not in bill_title:
		dict['88']=1
	
	# 96: 'table'
	if 'table' in question:
		dict['96']=1

	if len(dict.keys())>1:
		final='?'

	if len(dict.keys())==1:
		final=dict.keys()[0]

	if len(dict.keys())==0:
		final='69'

	if test==1:
		print dict

	return final



scrape_votes(server_file_location)

with open(server_file_location,'rU') as csvfile:
	reader=csv.reader(csvfile)
	data=[row for row in reader]

data=fix_contvotes(data)
with open(server_file_location,'wb') as csvfile:
	writer=csv.writer(csvfile)
	for row in data:
		writer.writerow(row)

