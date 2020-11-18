# Listjj


Django app made for heroku. It is very generic, multi-purpose app which allows to create own lists of items with some categories, dates and values, with api access.


![Screenshot](screenshot.png?raw=true "Screenshot")

User can:

- register, create more users
- create/edit/delete own categories
- add/edit/delete notes with categories (current date, value, description)
- filter by category, date
- recent filter is saved to cookies and kept 1 day
- filter current page by content dynamically
- set default category (to add note quickly)
- use api to read/write (need to create token for auth)
- export/import to csv

