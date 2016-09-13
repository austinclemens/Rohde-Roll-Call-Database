# Rohde-Roll-Call-Database
Automatic creation of the Rohde Roll Call database

This project scrapes congressional vote data and codes votes according to a classification system established by David Rohde. The results can be found here: <a href="http://pipcvotes.cacexplore.org">http://pipcvotes.cacexplore.org</a>

There is not a lot of text available to classify votes so the system is completely rule based. It is possible for researchers without much/any programming knowledge to alter the rules by making changes to the script providing they have some knowledge of what is being scraped, which I will provide here.

**IMPORTANT USAGE NOTE**: NEVER re-classify all votes. The script intentionally ignores older votes because many of these have been re-coded by hand or were classified by older versions of the script that worked for the time the vote was scraped in. Current rules reflect current practices by the House Clerk in 'talking' about votes/bills/etc.

## Explanation of scraped text

The following fields that were not present in the original Rohde dataset have been added:

1. url: This is the URL to the rollcall vote record at the House Clerk's site. This is an XML file that provides many of the other fields listed below.
1. billtype1: billtype1 is the first part of the underlying bill's designation e.g. HR, HRES, etc. It is found in the rollcall XML in legis-num field. ~~~~ <legis-num>H R 3408</legis-num> ~~~~ 
2. billnum1
3. question
4. amendment
5. Title_Desription
6. url
7. question2
8. bill_title
9. amendment2
10. amendment3
