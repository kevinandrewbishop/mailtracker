# mailtracker


The purpose of this project is to automatically read a user's email, extract
text using regular expressions, and store the results in a local file
or database. It was built to help with a budget automation
project, but is intended to work as a general package.  

## Budget Automation Use Case

One of the most frustrating parts of keeping a budget is the need to manually
download a csv of transactions before running it through a python script or
excel worksheet. First, it simply takes time to log in to the financial website.
More importantly, as you periodically download these csvs to keep your budget
up to date, you have to make sure you aren't re-downloading transactions from
the last time you updated your budget. Sometimes this is non-trivial as certain
vendors, like restaurants, often have a lag of multiple days between the date
of the actual transaction vs the date it appears on the website.  

Some applications, like mint, claim to automatically do this, but I have found
they are incompatible with certain credit cards.  

To get around this problem, this package uses the email alert system credit
cards usually provide. Most credit cards offer a way to create automated email
alerts whenever a condition is met (transaction above a certain amount, balance
above a certain amount, etc).   

The overall workflow is as follows:  
1. Set credit card email alerts on all transactions above a nominal amount
(e.g. $5)
2. Create an email filter rule that moves all of these alert messages to a
specific folder (e.g. "Visa")
3. Use this package to download those emails and extract the relevant fields
using regular expressions
4. Store the contents in an application (e.g. flask app with sql database) to
track transactions  

The email checking service should be set to run on an automated loop every
so many minutes.

## Example

```python
import os
#Password should be stored as environment variable rather than plain text
config = {
    'host': 'imap.mail.yahoo.com',
    'port': 993,
    'folder': 'Visa',
    'email': 'my_email@example.com',
    'password': os.environ.get('password')
    }

client = EmailClient(**config)
pattern = r'my regex (pattern)'
#Reads latest message by default
client.read_message(pattern = pattern)
>>> 'result of regex'

#Read a specific message identified by ID
client.read_message(52, pattern = pattern)
```

### Yahoo

This package was built and tested using a yahoo email account. In theory it
should work with all accounts that use imap4.  

#### Unique Email ID
Yahoo appears to identify each email in a folder by the order in which it was
placed in that folder. The first email to arrive in the folder is 1, the second
is 2 and so on up to N, where N is the total number of emails in the folder.  

This is a very unstable way of identifying individual emails. For example:  
* If an email is deleted, any email with a higher ID number gets decremented
by 1
* If an email is moved to another folder, then moved back into the current
folder, that email is now ID number N  

For the initial version, I assume emails enter a folder and never leave. This is
a simplifying assumption that will probably be fixed later. But for the use-case
of scraping automated credit card transaction emails, I think the assumption is
not unrealistic. The user simply needs to make an email filter rule that moves
any emails from institution X to a special folder.

### Gmail

Please note that Gmail by default does not allow users to access
their email in this way. You can change this setting here:  
https://support.google.com/mail/accounts/answer/78754

### Database