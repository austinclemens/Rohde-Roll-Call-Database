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
import xml.etree.ElementTree as ET

server_file_location=os.path.dirname(os.path.realpath(__file__))+'/house_votes.csv'
server_file_location_senate=os.path.dirname(os.path.realpath(__file__))+'/senate_votes.csv'

# server_file_location='/Users/austinc/Desktop/votes.csv'
# print os.path.dirname(os.path.realpath(__file__))
# print server_file_location
southern_states=['AL','AR','FL','GA','KY','LA','MS','NC','OK','SC','TN','TX','VA']
request_headers = {"Accept-Language": "en-US,en;q=0.5","User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Referer": "http://pipcvotes.cacexplore.org","Connection": "keep-alive" }
monthdict=['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']

def geturl(url):
	# print url
	request = urllib2.Request(url, headers=request_headers)
	return urllib2.urlopen(request).read()

def fix_dayes(doc,doc2):
	with open(doc,'rU') as csvfile:
		reader=csv.reader(csvfile)
		data=[row for row in reader]

	for row in data[1:]:
		url=row[34]
		print url
		if url!='':
			rollcall=geturl(url)
			dem_totals=re.compile('<party>Democratic</party>\r\n<yea-total>(.*?)</yea-total>\r\n<nay-total>(.*?)</nay-total>')
			try:
				dayes=int(dem_totals.findall(rollcall)[0][0])
				row[13]=dayes
			except:
				pass

	with open(doc2,'w') as csvfile:
		writer=csv.writer(csvfile)
		for row in data:
			writer.writerow(row)

# useful: https://stackoverflow.com/questions/2941681/how-to-make-int-parse-blank-strings
def mk_int(s):
	if s is not None:
		s=s.strip()
		return int(s) if s else 0
	else:
		return 0


def scrape_votes_senate(existing_file_senate):
	"""Same as scrape_votes but for Senate. Take existing file, add all new votes, run new votes
	through classifier."""
	with open(existing_file_senate,'rU') as csvfile:
		reader=csv.reader(csvfile)
		data=[row for row in reader]

	csvfile=open(existing_file_senate,'a')
	writer=csv.writer(csvfile)

	compare_votes=[[mk_int(row[2]),mk_int(row[3])]for row in data[1:]]
	new_votes=[]

	# Iterate through years from 1989 to present (Thomas only has votes >1989)
	current_year=datetime.date.today().year
	for year in range(1989,current_year+1,1):
		print year
		# convert year to congress/session
		congress=math.floor((year-1787)/2)
		session=(year-1)%2+1
		url='http://www.senate.gov/legislative/LIS/roll_call_lists/vote_menu_'+str(int(congress))+'_'+str(int(session))+'.htm'
		
		try:
			votepage=geturl(url)
		except:
			pass

		# get all votes for the year
		# compare against existing file to see if the vote is already in the database
		# vote_finder gets all vote numbers for the year
		vote_finder=re.compile('href="/legislative/LIS/roll_call_lists/roll_call_vote_cfm\.cfm\?congress='+str(int(congress))+'&session='+str(int(session))+'&vote=(.*?)">')
		# fullvote_finder pulls the data in each row - date/tally/result/question/issue
		fullvote_finder=re.compile('<td valign="top" class="contenttext">(.*?)</td>',re.DOTALL)

		votes=vote_finder.findall(votepage)
		fullvotes=fullvote_finder.findall(votepage)
		# the question field - a short description of the vote
		votedescs=fullvotes[2::5]
		# links to the bill at issue on congress.gov
		billpages=fullvotes[3::5]
		# date of vote
		dates=fullvotes[4::5]
		# result
		results=fullvotes[1::5]

		for i,vote in enumerate(votes):
			# print i,year,int(vote)
			vote_s="%05d" % (int(vote))
			if [int(year),int(vote)] not in compare_votes:
				amendment_to_amendment=''
				amendment_to_amendment_to_amendment=''
				print vote
				vote_s="%05d" % (int(vote))
				url='http://www.senate.gov/legislative/LIS/roll_call_lists/roll_call_vote_cfm.cfm?congress='+str(int(congress))+'&session='+str(int(session))+'&vote='+vote_s
				urlxml='https://www.senate.gov/legislative/LIS/roll_call_votes/vote'+str(int(congress))+str(int(session))+'/vote_'+str(int(congress))+'_'+str(int(session))+'_'+vote_s+'.xml'
				# rollcall holds the senate rollcall vote page. ex: http://www.senate.gov/legislative/LIS/roll_call_lists/roll_call_vote_cfm.cfm?congress=114&session=2&vote=00155
				rollcall=geturl(url)
				rollcall_xml=geturl(urlxml)
				root=ET.fromstring(rollcall_xml)
				votedesc=votedescs[i]
				billpage=billpages[i]
				newdate=dates[i].replace('&nbsp;',' ')
				month=monthdict.index(newdate[0:3].lower())+1
				day=newdate[4:6]
				result=results[i]
				print billpage

				if 'n/a' in billpage or 'Treaty' in billpage or 'PN' in billpage:
					question2=''
					amendment2=''
					amendment3=''
					amendment=''

					if('Treaty') in billpage:
						bill_finder=re.compile('>([A-Za-z\.\s]+)([0-9\-\(\)A-Z]+)<')
						bill_url_finder=re.compile('<a href="(.*?)">.*?</a>')
						proper_url_finder=re.compile('<meta name="canonical" content="(.*?)">')
						billdetails=bill_finder.findall(billpage)[0]
						billurl=bill_url_finder.findall(billpage)[0]
						try:
							bill_details=geturl(billurl)
							billurl=proper_url_finder.findall(bill_details)[0]	
						except:
							billurl=''
						bill_title=''

					if('n/a') in billpage:
						billdetails='na'
						billurl=''
						bill_title=''

					if 'PN' in billpage:
						bill_finder=re.compile('>([A-Za-z\.\s]+)([0-9\-]+)<')
						bill_url_finder=re.compile('<a href="(.*?)">.*?</a>')
						proper_url_finder=re.compile('<meta name="canonical" content="(.*?)">')
						billdetails=bill_finder.findall(billpage)[0]
						billurl=bill_url_finder.findall(billpage)[0]
						try:
							bill_details=geturl(billurl)
							billurl=proper_url_finder.findall(bill_details)[0]
						except:
							billurl=''
						bill_title=''			

				if billpage!='n/a' and 'Treaty' not in billpage and 'PN' not in billpage:

					bill_finder=re.compile('>([A-Za-z\.\s]+)([0-9]+)<')
					bill_url_finder=re.compile('<a href="(.*?)">.*?</a>')

					billdetails=bill_finder.findall(billpage)[0]
					billurl=bill_url_finder.findall(billpage)[0]

					# get data from the bill page
					# Go to all actions page for the legislation, find the action that includes the roll call, save the full text into question2
					question2=''
					amendment2=''
					amendment3=''
					amendment=''

					bill_details=geturl(billurl)
					proper_url_finder=re.compile('<meta name="canonical" content="(.*?)">')
					billurl=proper_url_finder.findall(bill_details)[0]
					bill_title_details=geturl(billurl+'/titles')
					action_url=geturl(billurl+'/all-actions')
					bill_title_finder=re.compile("<h4>Official Title as Introduced:</h4>\r\n(.*?)<p>(.*?)<br /></p>")

					try:
						bill_title=bill_title_finder.findall(bill_title_details)[0][1].replace('\n','').replace('\r','')
					except:
						bill_title=''

				# get data from the rollcall page
				vote_totals=re.compile('<td width="50%" class="contenttext">(?:YEAs|Guilty)</td><td width="25%" class="contenttext" align="right">(.*?)</td>\n    </tr>\n    <tr>\n        <td></td><td width="50%" class="contenttext">(?:NAYs|Not Guilty)</td><td width="25%" class="contenttext" align="right">(.*?)</td>')
				leg_block_finder=re.compile('Alphabetical by Senator Name(.*?)By Vote Position', re.DOTALL)
				leg_finder=re.compile('>(.*?) \(([A-Z])-([A-Z]{2})\), <b>(Yea|Nay|Not Voting)</b>')
				amdt_finder=re.compile('<TD valign="top" class="contenttext"><B>Amendment Number: </B></TD><TD valign="top" colspan="3" class="contenttext">(.*?)</TD>', re.DOTALL)

				leg_block=root.find('members')
				legislators=[]
				for member in leg_block:
					legislators.append([member.find('last_name').text,member.find('party').text,member.find('state').text,member.find('vote_cast').text])

				amendment=root.find('amendment').find('amendment_purpose').text
				try:
					amendment_to_amendment=root.find('amendment').find('amendment_to_amendment_number').text
				except:
					pass
				try:
					amendment_to_amendment_to_amendment=root.find('amendment').find('amendment_to_amendment_to_amendment_number').text
				except:
					pass

				dayes=0
				dnays=0
				rayes=0
				rnays=0

				for leg in legislators:
					if leg[1]=='D' and leg[3]=='Yea':
						dayes=dayes+1
					if leg[1]=='D' and leg[3]=='Nay':
						dnays=dnays+1
					if leg[1]=='R' and leg[3]=='Yea':
						rayes=rayes+1
					if leg[1]=='R' and leg[3]=='Nay':
						rnays=rnays+1

				ayes=mk_int(root.find('count').find('yeas').text)
				nays=mk_int(root.find('count').find('nays').text)
				totalvotes=ayes+nays+mk_int(root.find('count').find('present').text)
				
				bill_type=billdetails[0].replace('.','').replace(' ','')
				bill_numb=billdetails[1]

				# amendment=amend_author.findall(rollcall)
				# There's really no point popuating votetype on the Senate side - it's just the 2nd sentence of question
				votetype=''
				question=votedesc
				# question=q_finder.findall(vote)[0]
				question=question.lower()
				question=question.replace('the','')
				question=question.replace(',','')
				question=question.replace('.','')
				question=question.replace('  ',' ')
				question=question.strip()

				# tally up north/south dems, north/south repubs
				ndayes=0
				ndnays=0
				sdayes=0
				sdnays=0
				nrayes=0
				nrnays=0
				srayes=0
				srnays=0
				# legs are [name,party,state,vote]
				for leg in legislators:
					if leg[1]=='D':
						if leg[2] not in southern_states:
							if leg[3]=='Yea':
								ndayes=ndayes+1
							if leg[3]=='Nay' or leg[3]=='No':
								ndnays=ndnays+1
						if leg[2] in southern_states:
							if leg[3]=='Yea':
								sdayes=sdayes+1
							if leg[3]=='Nay' or leg[3]=='No':
								sdnays=sdnays+1

					if leg[1]=='R':
						if leg[2] not in southern_states:
							if leg[3]=='Yea':
								nrayes=nrayes+1
							if leg[3]=='Nay' or leg[3]=='No':
								nrnays=nrnays+1
						if leg[2] in southern_states:
							if leg[3]=='Yea':
								srayes=srayes+1
							if leg[3]=='Nay' or leg[3]=='No':
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

				# try:
				votecode=classify_question_senate(question,bill_title,votetype,amendment,amendment_to_amendment,amendment_to_amendment_to_amendment)
				bill2watch=''
				billnum2=bill_type+' '+bill_numb
				votedate=str(int(month))+'/'+str(int(day))+'/'+str(int(year))

				question=question.decode('ascii','ignore')
				amendment=''.join([i if ord(i) < 128 else ' ' for i in amendment])
				row=[int(congress),session,year,vote,'','',votecode,'','',
					totalvotes,ayes,nays,dayes,dnays,rayes,rnays,ndayes,ndnays,sdayes,sdnays,nrayes,
					nrnays,srayes,srnays,unity,coalition,unanimous,ndr,bill2watch,bill_type,bill_numb,
					billnum2,question,amendment,amendment_to_amendment,amendment_to_amendment_to_amendment,result,url,bill_title,votedate,month,day]	
				# code_votes_senate([row])
				print url
				print row
				writer.writerow(row)

				del amendment,vote,totalvotes,ayes,nays,dayes,dnays,rayes,rnays,ndayes,ndnays,sdayes,sdnays,nrayes,nrnays,srayes,srnays,unity,coalition,unanimous,ndr,bill2watch,bill_type,bill_numb,billnum2,question,result,url,bill_title,votedate,month,day

				# except:
					# print 'Bad vote: '+ str(congress) + ' ' + str(session) + ' ' + str(year) + ' ' + str(vote)
			# else:
			# 	amendment_to_amendment=''
			# 	amendment_to_amendment_to_amendment=''
			# 	# try:
			# 	oldrow=[row for row in data[1:] if int(row[0])==int(congress) and int(row[1])==int(session) and int(row[3])==int(vote_s)][0]
			# 	urlxml='https://www.senate.gov/legislative/LIS/roll_call_votes/vote'+str(int(congress))+str(int(session))+'/vote_'+str(int(congress))+'_'+str(int(session))+'_'+vote_s+'.xml'
			# 	rollcall_xml=geturl(urlxml)
			# 	root=ET.fromstring(rollcall_xml)
			# 	# except:
			# 	# 	pass

			# 	try:
			# 		amendment_to_amendment=root.find('amendment').find('amendment_to_amendment_number').text
			# 	except:
			# 		pass
			# 	try:
			# 		amendment_to_amendment_to_amendment=root.find('amendment').find('amendment_to_amendment_to_amendment_number').text
			# 	except:
			# 		pass

			# 	oldrow[34]=amendment_to_amendment
			# 	oldrow[35]=amendment_to_amendment_to_amendment

			# 	writer.writerow(oldrow)


# http://drumcoder.co.uk/blog/2012/jul/13/removing-non-ascii-chars-string-python/
def rna(s): 
	return "".join(i for i in s if ord(i)<128)


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
			vote=geturl(url)
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
			votepage=geturl(url)
			vote_finder=re.compile('<TR><TD><A HREF="http://clerk.house.gov/cgi-bin/vote.asp\?year=.*?&rollnumber=.*?">(.*?)</A></TD>')
			
			# this fullvotes string changed around 4/15/2016. The old one is preserved below.
			# fullvote_finder=re.compile('<TR><TD><A HREF="http://clerk.house.gov/cgi-bin/vote.asp\?year=.*?&rollnumber=.*?">(.*?)</A></TD>\r\n<TD><FONT FACE="Arial" SIZE="-1">.*?</FONT></TD>\r\n<TD><FONT FACE="Arial" SIZE="-1">\r\n<A HREF="(.*?)">.*?</A>\r\n</FONT></TD>\r\n<TD><FONT FACE="Arial" SIZE="-1">.*?</FONT></TD>\r\n<TD ALIGN="CENTER"><FONT FACE="Arial" SIZE="-1">.*?</FONT></TD>\r\n<TD><FONT FACE="Arial" SIZE="-1">.*?</FONT></TD></TR>')
			# fullvote_finder=re.compile('<TR><TD><A HREF="http://clerk.house.gov/cgi-bin/vote.asp\?year=.*?&rollnumber=.*?">(.*?)</A></TD>\r\n<TD><FONT FACE="Arial" SIZE="-1">.*?</FONT></TD>\r\n<TD><FONT FACE="Arial" SIZE="-1">\r\n<A HREF="(.*?)">.*?</A>\r\n</FONT></TD>\r\n<TD><FONT FACE="Arial" SIZE="-1">.*?</FONT></TD>\r\n<TD ALIGN="CENTER"><FONT FACE="Arial" SIZE="-1">.*?</FONT></TD>\r\n<TD><FONT FACE="Arial" SIZE="-1">.*?</FONT></TD></TR>')
			fullvote_finder=re.compile('<TR><TD><A HREF="http://clerk.house.gov/cgi-bin/vote.asp\?year=.*?&rollnumber=.*?">(.*?)</A></TD>\r\n<TD><FONT FACE="Arial" SIZE="-1">.*?</FONT></TD>\r\n<TD><FONT FACE="Arial" SIZE="-1"><A HREF="(.*?)">')
			# 0 is roll call number, 1 is thomas page for the bill, might not be a link
			votes=vote_finder.findall(votepage)
			fullvotes=fullvote_finder.findall(votepage)

			# new 
			# <TR><TD><A HREF="http://clerk.house.gov/cgi-bin/vote.asp\?year=.*?&rollnumber=.*?">(.*?)</A></TD>\r\n<TD><FONT FACE="Arial" SIZE="-1">.*?</FONT></TD>\r\n<TD><FONT FACE="Arial" SIZE="-1">\r\n<A HREF="(.*?)">.*?</A>\r\n</FONT></TD>\r\n<TD><FONT FACE="Arial" SIZE="-1">.*?</FONT></TD>\r\n<TD ALIGN="CENTER"><FONT FACE="Arial" SIZE="-1">.*?</FONT></TD>\r\n<TD><FONT FACE="Arial" SIZE="-1">.*?</FONT></TD></TR>
			# http://thomas.loc.gov/cgi-bin/bdquery/z?d107:h.res.00428:
			# http://thomas.loc.gov/cgi-bin/bdquery/z?d107:HE00428:@@@X

			for vote in votes:
				if [int(year),int(vote)] not in compare_votes:
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
							bill_title_details=geturl(fullvote[1]+'/titles')
							action_url=geturl(fullvote[1]+'/all-actions')
							# bill_title_finder=re.compile('<b>Latest Title:</b>(.*?)\n')
							bill_title_finder=re.compile("<h4>Official Title as Introduced:</h4>\r\n(.*?)<p>(.*?)<br /></p>")
							# all_action_finder=re.compile('<a href="(.*?)">All Congressional Actions\n</a>')
							# all_action_amendment_finder=re.compile('<a href="(.*?)">All Congressional Actions with Amendments</a>')
							# action_page=all_action_finder.findall(bill_details)
							# amend_page=all_action_amendment_finder.findall(bill_details)

							try:
								bill_title=bill_title_finder.findall(bill_title_details)[0][1].replace('\n','').replace('\r','')
							except:
								bill_title=''

							# if len(amend_page)>0:
							# 	page=amend_page[0]
							# else:

							# 	page=action_page[0]

							try:
								# action_url='http://thomas.loc.gov'+page
								actions=action_url
								# action_finder=re.compile('<strong>.*?</strong><dd>(.*?)(?:\n<dt>|\n</dl>)',re.DOTALL)
								action_finder=re.compile('<td class="actions">\n(.*?)\(<a target="_blank" href="'+url)
								# amendment_finder=re.compile('<a href="/cgi-bin/bdquery/(.*?)">')
								amendment_finder=re.compile('<a href="(.*?)">')
								all_actions=action_finder.findall(actions)[0].strip()
								# for action in all_actions:
									# if url in action:
								question2=all_actions.replace('\n','').replace('\r','')
								if 'amendment' in question2:
									amend_url=amendment_finder.findall(question2)[0]
									amendment_page=geturl('https://www.congress.gov'+amend_url)

									amendment2finder=re.compile('<h3>Purpose:</h3>.*?<p>(.*?)</p>')
									amendment3finder=re.compile('<div id="main" class="wrapper_std" role="main"><p>(.*?)</p>')

									try:
										amendment2=amendment2finder.findall(amendment_page)[0].replace('\n','').replace('\r','')
									except:
										amendment2=''
									try:
										amendment3=amendment3finder.findall(amendment_page)[0].replace('\n','').replace('\r','')
									except:
										amendment3=''

							except:
								print "Couldn't find question."
								question2=''
								amendment2=''
								amendment3=''

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

					# handle votes for the speaker - the ayes and nays should be the vote totals for the candidates with the first and second-most votes
					if 'election' in question and 'speaker' in question:
						speaker_vote_finder=re.compile('<totals-by-candidate><candidate>.*?</candidate><candidate-total>(.*?)</candidate-total></totals-by-candidate>')
						ayes=int(speaker_vote_finder.findall(rollcall)[0])
						nays=ayes=int(speaker_vote_finder.findall(rollcall)[1])
						dayes=0
						dnays=0
						rayes=0
						rnays=0
						totalvotes=ayes+nays

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

					# try:
					votecode=classify_question(question,question2,bill_title,amendment,votetype,bill_type,amendment2,amendment3)

					row=[congress,session,year,vote,'','',votecode,'','','',
						totalvotes,ayes,nays,dayes,dnays,rayes,rnays,ndayes,ndnays,sdayes,sdnays,nrayes,
						nrnays,srayes,srnays,unity,coalition,unanimous,ndr,bill_type,bill_numb,
						question,amendment,votetype,url,question2,bill_title,amendment2,amendment3]	
					code_votes([row])
					print url
					print row
					writer.writerow(row)

					# except:
						# print 'Bad vote: '+ str(congress) + ' ' + str(session) + ' ' + str(year) + ' ' + str(vote)


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
		vote=geturl(url)
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
		votenums=[mk_int(row[3]) for row in data if row[2]==year]
		yeardict[year]=max(votenums)

	for row in data[1:]:
		if int(row[2])%2==0:
			try:
				row[4]=str(mk_int(row[3])+int(yeardict[str(int(row[2])-1)]))
			except:
				pass
		else:
			row[4]=row[3]
	return data


def code_votes(data,test=0,vtype=-1):
	"""Take a set of rows and code each vote. Use 'test=1' if you want to see the classification dictionaries.
	Set 'vtype=x' where vtype"""
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

		if vtype==-1:
			row[6]=code

		if vtype!=-1 and code==vtype:
			row[6]=code

	return data


def code_votes_senate(data,test=0):
	for row in data:
		question=strip(row[32])
		bill_title=strip(row[38])
		votetype=strip(row[29]).lower()
		amendment=strip(row[33])
		amendment_to_amendment_number=row[34]
		amendment_to_amendment_to_amendment_number=row[35]
		code=classify_question_senate(question,bill_title,votetype,amendment,amendment_to_amendment_number,amendment_to_amendment_to_amendment_number,test=test)
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
		# what are these and why are they being coded?
		# if 'article i' in question:
		# 	dict['193']=1

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

		# 9: billtype is quorum
		if 'QUORUM' in billtype and 'states' not in question:
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

			# 22: 'amendment to [A-Z].*? ' in amendment - amendment 3 is pretty similar here. Omit mentions of the senate as 'amendment to senate amendment' is really an amendment to the bill
			if ' to ' in amendment and 'substitute' not in amendment and 'senate' not in amendment:
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

	# sorta klugey but to be safe, override on 9s - some of these seem to pop up as amendments but these have to be quorum calls
	if '9' in dict.keys():
		final='9'

	if test==1:
		print dict

	return final


def classify_question_senate(question,bill_title,votetype,amendment,amendment2,amendment3,test=0):
	"""Takes three strings associated with a vote and classifies the vote. If more than one classification
	is found or not classification is found, will classify the vote as '?'."""
	dict={}
	if test==1:
		print question
		print bill_title
		print votetype

	# No Statement of Purpose on File. - sometimes given to bills that aren't amendments
	if 'no statement of purpose' in amendment:
		amendment=''

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
		# 24: Motion to Table Amendment 
		if 'motion to table' in question:
			dict['24']=1
		# 26: Perfecting Amendment 
		elif 'perfecting nature' in question:
			dict['26']=1
		# 22: Amendments to Amendments 
		elif amendment2!='':
			dict['22']=1
		# 21: Straight Amendments (includes en bloc & amendments in the nature of a substitute) 
		if len(dict)==0:
			dict['21']=1
	# 30: Passage over Presidential Veto 
	if 'on overriding veto' in question:
		dict['30']=1
	# 34: Treaty Ratification 
	if 'resolution of ratification' in question:
		dict['34']=1
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
	# 61: Budget Waivers
	if 'motion to table' not in question and 'motion to waive' in question or 'waive cba' in question or 'waive cbr' in question or 'wave cba' in question or ('waive' in question and 'budget' in question) or ('waive' in question and 'internal revenue' in question):
		dict['61']=1
	# 62: Invoke cloture
	if 'cloture motion' in question or question[0:10]=='on cloture':
		dict['62']=1
	# 63: Motion to Reconsider 
	if 'motion to reconsider' in question and ('motion to table' not in question or ('motion to table' in question and question.index('motion to table')>question.index('motion to reconsider'))):
		dict['63']=1
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
	if 'motion to table' in question and amendment=='':
		dict['96']=1
	# 97: Motion to Recede and Concur (also includes motion to concur)
	if 'motion to concur' in question[0:150] and 'motion to waive' not in question or ('motion to concur' in question and 'motion to table' in question and question.find('motion to concur')<question.find('motion to table')):
		dict['97']=1
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


scrape_votes(server_file_location)
scrape_votes_senate(server_file_location_senate)

with open(server_file_location,'rU') as csvfile:
	reader=csv.reader(csvfile)
	data=[row for row in reader]

data=fix_contvotes(data)

with open(server_file_location,'wb') as csvfile:
	writer=csv.writer(csvfile)
	for row in data:
		writer.writerow(row)

with open(server_file_location_senate,'rU') as csvfile:
	reader=csv.reader(csvfile)
	data=[row for row in reader]

data=fix_contvotes(data)

with open(server_file_location_senate,'wb') as csvfile:
	writer=csv.writer(csvfile)
	for row in data:
		writer.writerow(row)

# remove all newline characters within text fields
with open(server_file_location,'rU') as csvfile:
	reader=csv.reader(csvfile)
	data=[row for row in reader]

for i,row in enumerate(data):
	for j,column in enumerate(row):
		a=column.replace('\n','')
		data[i][j]=a.replace('\r','')

# sort according to congress and then vote number
temp=data[0]
data=data[1:]
data.sort(key=lambda x: int(x[4]))
data.sort(key=lambda x: int(x[2]))
data.insert(0,temp)

with open(server_file_location,'wb') as csvfile:
	writer=csv.writer(csvfile)
	for row in data:
		writer.writerow(row)

# remove all newline characters within text fields
with open(server_file_location_senate,'rU') as csvfile:
	reader=csv.reader(csvfile)
	data=[row for row in reader]

for i,row in enumerate(data):
	for j,column in enumerate(row):
		a=column.replace('\n','')
		data[i][j]=a.replace('\r','')

# sort according to congress and then vote number
temp=data[0]
data=data[1:]
data.sort(key=lambda x: mk_int(x[4]))
data.sort(key=lambda x: int(x[2]))
data.insert(0,temp)

with open(server_file_location_senate,'wb') as csvfile:
	writer=csv.writer(csvfile)
	for row in data:
		writer.writerow(row)






