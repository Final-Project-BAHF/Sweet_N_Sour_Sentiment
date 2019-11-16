from flask import Flask, jsonify, render_template
import requests
#from sweet_n_sour.modules import scrape
from modules import scrape

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """Homepage for Fiscal-Heartbreak Viz project"""
    return render_template("index.html")

@app.route("/api")
def api_list():
    """List all available api routes."""
    return render_template("api.html")

@app.route("/api/get-scripts/<arg_ticker>/<arg_num_scripts>")
def GetScriptsAPI(arg_ticker='GE',arg_num_scripts=1):
    """Return a json with the specified number of transcripts for the requested company.
        Argument: arg_ticker - the stock ticker symbol for the desired company. Defaults to 'GE' if no ticker specified.
        Argument: arg_num_scripts - the number of most recent Earnings Call Transcripts to retrieve. Defaults to 1.
       """

    # initialize an http session to be used for scraping
    http_session = requests.session()

    # get list of Earnings Calls for requested company
    articles = scrape.get_article_list(http_session, arg_ticker)

    ### DEBUG
    print(f'Calls Found: {articles}')
    ###

    # check that requested num articles does not exceed list length
    num_articles = int(arg_num_scripts)
    if (num_articles > len(articles)):
        num_articles = len(articles)

    # initialize list to be returned
    transcript_list = []

    # iterate through requested number of transcripts and get content
    for article in articles[0:num_articles]:
        transcript_list.append(scrape.get_call_content(http_session, article['url'], article['ticker']))

    # close http session
    http_session.close()

    return jsonify(transcript_list)

### Main ###
if __name__ == '__main__':
    app.run(debug=True)
############
