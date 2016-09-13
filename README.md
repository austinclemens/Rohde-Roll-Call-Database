# Rohde-Roll-Call-Database
Automatic creation of the Rohde Roll Call database

This project scrapes congressional vote data and codes votes according to a classification system established by David Rohde. The results can be found here: <a href="http://pipcvotes.cacexplore.org">http://pipcvotes.cacexplore.org</a>

There is not a lot of text available to classify votes so the system is completely rule based. It is possible for researchers without much/any programming knowledge to alter the rules by making changes to the script providing they have some knowledge of what is being scraped, which I will provide here.

**IMPORTANT USAGE NOTE**: NEVER re-classify all votes. The script intentionally ignores older votes because many of these have been re-coded by hand or were classified by older versions of the script that worked for the time the vote was scraped in. Current rules reflect current practices by the House Clerk in 'talking' about votes/bills/etc.

## Explanation of scraped text

The following fields that were not present in the original Rohde dataset have been added:

1. **url**: This is the URL to the rollcall vote record at the House Clerk's site. This is an XML file that provides many of the other fields listed below.
2. **billtype1**: billtype1 is the first part of the underlying bill's designation e.g. HR, HRES, etc. It is found in the rollcall XML in legis-num field. In the example `<legis-num>H R 3408</legis-num>`, the billtype1 is HR
3. **billnum1**: billnum1 is the numerical part of the underlying bill's designation. In the example `<legis-num>H R 3408</legis-num>`, the billnum1 is 3408.
4. **question**: Question is a textual description of the rollcall in question. Each rollcall page contains this text after the QUESTION heading at the top of the page. In the XML it is the vote-question field. In the example `<vote-question>On Agreeing to the Amendment</vote-question>`, the question is 'on agreeing to the amendment.'
5. **amendment**: amendment is recorded only for amendments and is given by the amendment-author field in the XML. In the HTML version of the rollcall it appears as the AUTHOR(S) field. In the example `<amendment-author>Scott of Virginia Part B Amendment No. 44</amendment-author>`, amendment is 'Scott of Virginia Part B Amendment No. 44.'
6. **Title_Description**: Title_Description is a short title for the legislation, marked in the XML by the vote-desc flag. Amendments do not have a vote-desc.

The remaining fields come not from the rollcall URL but instead from the Library of Congress page describing the vote. To find this page, look at one of the House Clerk's rollcall session summary pages like this one: http://clerk.house.gov/evs/2015/ROLL_000.asp. Links in the 'issue' column go to the Library of Congress page for the underlying bill. The remaining fields are drawn from these pages (for bills themselves) or from the associated amendment page (for amendments - these can be found by clicking the 'Actions' tab and finding the appropriate amendment. 

7. **question2**: In the 'Actions' tab of the amendment or bill, question2 is the full description given of the rollcall vote. It is often similar to the description given to the vote by the Office of the Clerk (question). These two images show the question2 for an amendment and a bill: 

![alt text](http://www.austinclemens.com/rohde_rollcalls/assets/question2_1.png "Bill question2") 

![alt text](http://www.austinclemens.com/rohde_rollcalls/assets/question2_2.png "Amendment question2")

8. **bill_title**: bill_title is the formal short title of the underlying bill. It comes from the 'Titles' tab. In the image shown here, the bill_title is 'Student Success Act': 

![alt text](http://www.austinclemens.com/rohde_rollcalls/assets/titles2.png "Bill title")

9. **amendment2**: amendment2 is from the 'Purpose' field of the amendment's 'Description' tab, as shown in this screenshot: 

![alt text](http://www.austinclemens.com/rohde_rollcalls/assets/purpose.png "Amendment2 field")

10. **amendment3**: amendment3 was useful for a previous version of the Library of Congress site (Thomas) but does not presently have a purpose and is not used to code votes.
