def funyuns():
	# Iterate through years from 1989 to present (Thomas only has votes >1989)
	current_year=datetime.date.today().year
	# for year in range(1989,current_year+1,1):
	for year in range(1989,2018,1):
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
			print i,year,int(vote)
			if [year,int(vote)] not in compare_votes:
				print vote
				vote_s="%05d" % (int(vote))
				url='http://www.senate.gov/legislative/LIS/roll_call_lists/roll_call_vote_cfm.cfm?congress='+str(int(congress))+'&session='+str(int(session))+'&vote='+vote_s
				# rollcall holds the senate rollcall vote page. ex: http://www.senate.gov/legislative/LIS/roll_call_lists/roll_call_vote_cfm.cfm?congress=114&session=2&vote=00155
				rollcall=geturl(url)
				votedesc=votedescs[i]
				billpage=billpages[i]
				newdate=dates[i].replace('&nbsp;',' ')
				month=monthdict.index(newdate[0:3].lower())
				day=newdate[4:6]
				result=results[i]
				print billpage