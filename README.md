pychorusai
==========

simple python wrapper for pulling data from the chorus.ai API. Intended for bulk downloads by date. Returns raw json from API.

Supports these objects:
+ Engagements
+ Emails
+ Playlists
+ Users
+ Scorecards
+ External Moments

Does not support:
+ modifying, deleting, or adding records
+ pulling individual records
+ filtering on records by anything except min/max date

usage:
```python
from pychorusai import chorusai

c = chorusai(token = 'abc123')

# Get all users
c.getUsers()

# Iterate through pages of Playlists
for page in c.getPlaylists():
	print(page)
	
# Iterate through pages of Engagements (including trackers) after a specific date
for page in c.getEngagements(min_date = '2022-03-25T00:00:00.000Z', with_trackers = True):
	print(page)
	
```