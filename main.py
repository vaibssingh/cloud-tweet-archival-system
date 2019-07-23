import datetime
import firebase_admin
import tweepy
from firebase_admin import firestore
from flask import Flask, render_template, request
from google.cloud.firestore_v1 import ArrayUnion

# initialize firestore db
default_app = firebase_admin.initialize_app()
db = firestore.client()

app = Flask(__name__)

# tweepy credentials and setup
# todo: move the keys to another untracked file and fetch from there
consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

# todo: error and exception handling
# render home page
@app.route('/')
def home():
    return render_template('index.html')

# render result page
@app.route('/result', methods=['POST'])
def result():
    if request.method == 'POST':
        # parsing the search term that the user entered
        term = request.form.getlist('searchbox')[0]
        # tweets = tweepy.Cursor(api.search, q=term).items(5)
        # using api.search cause Cursor started causing problems on adding more content to the page -- todo
        tweets = api.search(term, count=30)

        # adding individial tweets to an array before adding to firestore --this could be improved
        array_of_tweets = []
        for tweet in tweets:
            array_of_tweets.append(tweet.text)

        # query firestore for tweet data
        # todo: check firestore docs to see if both the operations can be done in one query
        doc_ref = db.collection(u'tweet_collection').document(term)
        doc = doc_ref.get()

        # query firestore to check for search terms
        search_terms = db.collection(u'tweet_collection').get()

        # adding previous search terms to array so that they can be rendered
        array_of_search_terms = []
        for terms in search_terms:
            array_of_search_terms.append(terms.id)

        if doc.exists:
            # update the tweet array with latest batch of tweets
            doc_ref.update({u'tweets': ArrayUnion(array_of_tweets),
                            u'timestamp': datetime.datetime.now()})
        else:
            # create a new doc and array of tweets
            doc_ref.set({u'tweets': array_of_tweets,
                         u'timestamp': datetime.datetime.now()})

        return render_template("result.html", tweets=tweets, search_terms=array_of_search_terms)


# route for seeing collection of tweets
@app.route('/history', methods=['GET'])
def history():
    if request.method == 'GET':
        # this gets the 'search' term the user clicked on
        result = request.args.get('type')
        # get list of tweets related to that 'term'
        get_tweets = db.collection(u'tweet_collection').document(result)
        list = get_tweets.get()
        data = list.to_dict()
        tweets_array = data['tweets']

    return render_template("history.html", list=tweets_array)


# cron handler todo: graceful error handling
@app.route('/cron', methods=['GET'])
def cron():
    if request.method == 'GET':
        # get the search terms in collection
        searched_terms = db.collection(u'tweet_collection').get()
        for term in searched_terms:
            # after getting the terms, run twitter search for each and add tweets to array
            new_tweets = api.search(term.id, count=30)
            array_of_new_tweets = []
            for results in new_tweets:
                array_of_new_tweets.append(results.text)

            # add new results to db for each term 
            # todo: use bulk update operation
            db.collection(u'tweet_collection').document(term.id).update(
                {u'tweets': ArrayUnion(array_of_new_tweets), u'timestamp': datetime.datetime.now()})
    print('cron job done!!')
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=False)
