# Tweet Archival
Using this application you can search and view latest 30 tweets for any term and have the application store tweets for the previously searched term each hour automatically. You can then view the collection of tweets that came in  for your favourite topics while you were away!

[![Run on Google Cloud](https://storage.googleapis.com/cloudrun/button.svg)](https://console.cloud.google.com/cloudshell/editor?shellonly=true&cloudshell_image=gcr.io/cloudrun/button&cloudshell_git_repo=https://github.com/vaibssingh/cloud-tweet-archival-system.git)

### Tech Stack
This application has been developed with Python3 as backend, Flask as the frontend and Firestore for data storage.
It also uses 'tweepy' module for getting tweets using Twitter api. You can read about tweepy and how to set it up for your application [here](https://tweepy.readthedocs.io/en/latest/)

The app is deployed on Google App Engine and uses it's cron service for fetching the tweets each hour. More about Google App Engine [here](https://cloud.google.com/appengine/docs/)

Flask renders data using templates via ``render_template()`` which are in the /template folder.

### Structure
Once the user queries for any term, they are directed to the /results page where the latest 30 results are displayed. On the backend, all the results are stored in an array and saved to db with the corresponding search term as the document name. If the document for the search term already exists, then the array is appended to the existing document. If there is no such document i.e. if the term has been searched for the first time, then a new document with the same name as the searched term is created and the results are added to the document, along with a timestamp. 

Also on the same page, other terms that the user's have searched for is also displayed at the bottom. This is done by querying the db and simply getting the existing documents in collection and passing them on as template to flask.

The last part is the cron job which is configured in cron.yaml file. It runs every hour and stores latest 30 tweets for each term that has been searched previously.

### Todo's and future plans

 - Add error handling for the whole program at appropriate places
 - Fix the error where cron job crashes if there are no stored results for a document.
