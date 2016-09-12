# Rohde-Roll-Call-Database
Automatic creation of the Rohde Roll Call database

This project scrapes congressional vote data and codes votes according to a classification system established by David Rohde. The results can be found here: <a href="http://pipcvotes.cacexplore.org">http://pipcvotes.cacexplore.org</a>

There is not a lot of text available to classify votes so the system is completely rule based. It is possible for researchers without much/any programming knowledge to alter the rules by making changes to the script providing they have some knowledge of what is being scraped, which I will provide here.

**IMPORTANT USAGE NOTE**: NEVER re-classify all votes. The script intentionally ignores older votes because many of these have been re-coded by hand or were classified by older versions of the script that worked for the time the vote was scraped in. Current rules reflect current practices by the House Clerk in 'talking' about votes/bills/etc.
