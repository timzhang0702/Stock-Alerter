import nltk
import streamlit as st
import pandas as pd
import re
import smtplib
import requests
import tweepy
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import datetime, timedelta
import cufflinks as cf
import yfinance as yf
from htbuilder import HtmlElement, div, hr, a, p, styles
from htbuilder.units import percent, px
import SessionState
import yahoo_fin.stock_info as si
import requests_html

TWITTER_CONSUMER_KEY = 'BvbkjWzqKUKiUJuqpuf5DhZn5'
TWITTER_CONSUMER_SECRET = 'N2RVYi0LReDZA2tBPykVDUKBF0CuTuKHx9qtQorYL9TNV6nqq9'
TWITTER_ACCESS_TOKEN = '1171104317199310849-6BwEquJ2x9AAVUdW00rySWEiuRhZxU'
TWITTER_ACCESS_TOKEN_SECRET = 'BSuiCfdBRaxYQWtuK7mY44opMSOjpYvoy4FktLpRHp6sm'

BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAAMLqOgEAAAAAjkUEWfK%2F6m%2FLz9qwJb5%2Bu%2FsAq04%3DUuy0eAovNSACTyX8eg5yzSfu8g1uw9UHUDu5aWY2tVzDEkaIvS'
auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

periodDict = {
    "1 Month": 30,
    "3 Months": 90,
    "6 Months": 120,
    "1 Year": 365,
}
intervalDict = {
    "1 Month": "1d",
    "3 Months": "1d",
    "6 Months": "1d",
    "1 Year": "1wk",
}


def link(link, text, **style):
    return a(_href=link, _target="_blank", style=styles(**style))(text)


def layout(*args):
    style = """
    <style>
      #MainMenu {visibility: hidden;}
      footer {visibility: hidden;}
    </style>
    """

    style_div = styles(
        left=0,
        bottom=0,
        margin=px(0, 0, 0, 0),
        width=percent(100),
        color="black",
        text_align="center",
        height="auto",
        opacity=1
    )

    style_hr = styles(
        margin=px(3, 3, 10, 3),
        border_style="inset",
        border_width=px(3)
    )

    body = p()
    foot = div(
        style=style_div
    )(
        hr(
            style=style_hr
        ),
        body
    )

    st.markdown(style, unsafe_allow_html=True)

    for arg in args:
        if isinstance(arg, str):
            body(arg)

        elif isinstance(arg, HtmlElement):
            body(arg)

    st.markdown(str(foot), unsafe_allow_html=True)


def footer():
    myargs = [
        "Copyright © 2021 ",
        link("mailto:timzhang0702@gmail.com", "Tim Zhang"),
    ]
    layout(*myargs)


@st.cache(suppress_st_warning=True)
def chart(range, tickerSymbol):
    
    tickerDf = si.get_data(tickerSymbol, start_date=datetime.now() - timedelta(days=periodDict[range]),
                              end_date=datetime.now(), interval=intervalDict[range])

    r = requests.get(
        f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={tickerSymbol}&apikey=Y4NCX1DFBJCN4I82')
    data = r.json()

    try:
        string_name = data['Name']
    except:
        string_name = tickerSymbol
    try:
        string_summary = data['Description']
    except:
        string_summary = "Currently Unavailable"

    qf = cf.QuantFig(tickerDf, name='Price', title='Stock Chart', margin=dict(l=0,r=40,b=0,t=0))
    qf.add_sma(10, width=2, color='green', name='SMA')
    qf.add_bollinger_bands(periods=20, boll_std=2, colors=['magenta', 'magenta'], fill=True, name='BBands')
    qf.add_volume(title='Volume', up_color='grey', down_color='lightsteelblue', margin=dict(l=0,r=40,b=0,t=0))
    qf.add_rsi(periods=14, color='midnightblue', name='RSI', showbands=False, margin=dict(l=0,r=40,b=0,t=0))
    qf.add_macd(legendgroup=True, name='MACD', colors=['red', 'black'], margin=dict(l=0,r=40,b=0,t=0))
    layout = dict(
        xaxis=dict(rangeslider=dict(visible=False), categoryorder="category ascending", type="category", visible=False))
    config = {'displaylogo': False,
              "modeBarButtonsToRemove": ['pan2d', 'zoom2d', 'select2d', 'lasso2d', 'toggleSpikelines', 'autoScale2d']}
    fig = qf.iplot(asFigure=True, layout=layout)
    fig.update_layout(height=1200, title_text=string_name, title_x=0.5, showlegend=True,
                      legend=dict(orientation="h", yanchor="top", y=1.02, xanchor="center", x=0.5),margin=dict(l=0,r=40,b=20,t=100))
    return string_name, string_summary, fig, config


def increased_volume():
    st.markdown("<h1 style='text-align: center; color: black;'>Increased Volume</h1>", unsafe_allow_html=True)
    st.markdown(
        """
        ---
        Looking at volume over time can help get a sense of the strength or conviction behind advances and declines in specific stocks.
        An sharp increase in volume can indicate new interest in a stock and can signal an uptrend. 
        By understanding this, stocks with a sharp increase in volume that have not seen an as dramastic increase in price can present profitable trading opportunities.
        ### Stock Selection Criteria:
        - Current volume is greater than 2-times the 90-day average
        - Current price has increased less than 15% from the 90-day average price
        - Current volume is greater than 1 million
        """
    )
    st.write('---')


def uptrend_pullback():
    st.markdown("<h1 style='text-align: center; color: black;'>Uptrend Pullback</h1>", unsafe_allow_html=True)
    st.markdown(
        """
        ---
        In the long run, the stock market is in an uptrend. 
        However, in the short run, panic-selling and profit-taking causes stock prices to fall below it's intrinsic value. 
        By using the RSI indicator, a stock can be analyzed to be oversold or overbought. 
        This can help scan for profitable trading opportunities by recognizing that stock prices usually rebound. 
        ### Stock Selection Criteria:
        - Current RSI is less than 30 
        - Current price is great than the 200-day moving average
        - Current volume is greater than 500,000
        """
    )
    st.write('---')


def bbs():
    st.markdown("<h1 style='text-align: center; color: black;'>Bollinger Bands Squeeze</h1>", unsafe_allow_html=True)
    st.markdown(
        """
        ---
        The Bollinger Band Squeeze occurs when volatility falls to low levels and the Bollinger Bands narrow. 
        According to John Bollinger, developer of Bollinger Bands, periods of low volatility are often followed by periods of high volatility. 
        Therefore, a volatility contraction or narrowing of the bands can foreshadow a significant advance or decline.
        Usually, an uptrend is signaled once a stock's price breaks above the upper band.
        ### Stock Selection Criteria:
        - Low volatility during the last 5 days 
        - Current price is great than the upper bollinger band
        - Current volume is greater than 1 million
        """
    )
    st.write('---')


def search():
    st.markdown("<h1 style='text-align: center; color: black;'>Search</h1>", unsafe_allow_html=True)
    st.write('---')


def table(Symbol, Open, High, Low, Close, Volume, pctchange):
    st.markdown("<h2 style='text-align: center; color: black;'><b>Overview</b></h2>", unsafe_allow_html=True)
    st.write("---")

    fig = go.Figure(
        data=go.Table(columnorder=[1, 2, 3, 4, 5, 6, 7], columnwidth=[50, 50, 50, 50, 50, 50, 50],
                      header=dict(values=['Ticker', 'Open', 'High', 'Low', 'Close', 'Volume', 'Price Change'],
                                  fill_color='#FD8E72', align='left'),
                      cells=dict(values=[Symbol[1:], Open, High, Low, Close, Volume, pctchange],
                                 fill_color='#E5ECF6', align='left')))
    fig.update_layout(height=(len(Open)) * 21 , margin=dict(l=1, r=1, b=0, t=0))
    st.write(fig)
    st.write("---")

@st.cache()
def twitter(stock):
    endpoint = 'https://api.twitter.com/2/tweets/search/recent'
    headers = {'authorization': f'Bearer {BEARER_TOKEN}'}
    params = {
        'query': f'({stock}) (lang:en)',
        'max_results': '10',
        'tweet.fields': 'created_at,lang'
    }
    dtformat = '%Y-%m-%dT%H:%M:%SZ'  # the date format string required by twitter

    # we use this function to subtract 60 mins from our datetime string
    def time_travel(now, mins):
        now = datetime.strptime(now, dtformat)
        back_in_time = now - timedelta(minutes=mins)
        return back_in_time.strftime(dtformat)

    def get_data(tweet):
        data = {
            'id': tweet['id'],
            'created_at': tweet['created_at'][:10],
            'text': tweet['text']
        }
        return data

    now = datetime.now() - timedelta(minutes=1)  # get the current datetime, this is our starting point
    last_week = now - timedelta(days=5)  # datetime one week ago = the finish line
    now = now.strftime(dtformat)  # convert now datetime to format for API
    df = pd.DataFrame()  # initialize dataframe to store tweets
    while True:
        if datetime.strptime(now, dtformat) < last_week:
            # if we have reached 7 days ago, break the loop
            break
        pre60 = time_travel(now, 1440)  # get 60 minutes before 'now'
        # assign from and to datetime parameters for the API
        params['start_time'] = pre60
        params['end_time'] = now
        response = requests.get(endpoint,
                                params=params,
                                headers=headers)  # send the request
        now = pre60  # move the window 60 minutes earlier
        # iteratively append our tweet data to our dataframe
        print(response.json())
        for tweet in response.json()['data']:
            row = get_data(tweet)  # we defined this function earlier
            df = df.append(row, ignore_index=True)
    nltk.download('vader_lexicon')
    vader = SentimentIntensityAnalyzer()
    scores = df['text'].apply(vader.polarity_scores).tolist()
    # Convert the 'scores' list of dicts into a DataFrame
    scores_df = pd.DataFrame(scores)
    scores_df['pos'] = 100 * scores_df['pos']
    scores_df['neg'] = 100 * scores_df['neg']
    # Join the DataFrames of the news and the list of dicts
    scores_df = scores_df.rename(columns={'pos': 'Positive Sentiment', 'neg': 'Negative Sentiment'})
    df = df.join(scores_df[['Positive Sentiment', 'Negative Sentiment']])
    # Convert the date column from string to datetime
    df['created_at'] = pd.to_datetime(df['created_at']).dt.date
    plt.rcParams['figure.figsize'] = [10, 6]
    # Group by date and ticker columns from scored_news and calculate the mean
    mean_scores = df.groupby('created_at').mean()
    # Unstack the column ticker
    # mean_scores = mean_scores.unstack()
    return mean_scores


def ta(stock):
    layout = dict(
        xaxis=dict(rangeslider=dict(visible=False), categoryorder="category ascending", type="category",
                   visible=True))
    config = {'displaylogo': False,
              "modeBarButtonsToRemove": ['pan2d', 'zoom2d', 'select2d', 'lasso2d', 'toggleSpikelines',
                                         'autoScale2d']}
    fig = twitter(stock.split('.')[0]).iplot(kind="bar", barmode="stack", asFigure=True, opacity=1.0,
                                             colors=['limegreen', 'orangered'])
    fig.update_layout(height=500, title_text=string_name, title_x=0.5, showlegend=True,
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5))

    return fig, config


def taWrite():
    st.write("---")
    st.markdown("<h2 style='text-align: center; color: black;'><b>Twitter Sentiment Analysis</b></h2 >",
                unsafe_allow_html=True)
    st.write("---")
    st.info(
        "Below shows the sentiment analysis for tweets relating to the selected stock in recent days. Scores are classified from 0-100, with 100 being the highest degree of positivity/negativity.")


def sendmail(mes):
    sender_email = "timzhangx01@gmail.com"
    rec_email = "timzhang0702@gmail.com"
    password = "wagp54cb"

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, password)
    server.sendmail(sender_email, rec_email, mes)


def sheets(url):

    html = requests.get(url).content
    df_list = pd.read_html(html)
    dfc = df_list[-3]

    Symbol = dfc['Symbol'].tolist()
    Symbol.insert(0, 'Summary of Stocks')
    Open = dfc['Open'].tolist()
    High = dfc['High'].tolist()
    Low = dfc['Low'].tolist()
    Close = dfc['Close'].tolist()
    Volume = dfc['Volume'].tolist()
    pctchange = dfc['% Change'].tolist()

    return Symbol, Open, High, Low, Close, Volume, pctchange


def email():
    with st.form(key='my_form'):
        st.header("Want to be notified of new features?")
        col1, col2 = st.beta_columns([5, 1])
        regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'

        with col1:
            text_input = st.text_input('Subscribe today to get the latest news and updates.', 'Email Address')
        with col2:
            st.header('')
            submit_button = st.form_submit_button(label="Subscribe")
        if submit_button and re.search(regex, text_input):
            st.info("You've been subscribed successfully!")
            st.balloons()
            sendmail(text_input)

        elif submit_button:
            st.error("Invalid Email")


st.sidebar.write('#')
st.sidebar.header('Filters')
st.sidebar.write('####')
option = st.sidebar.selectbox('Dashboard',
                              ('Home', 'Search', 'Increased Volume', 'Uptrend Pullback', 'Bollinger Bands Squeeze'),
                              0)

if option == 'Home':
    try:
        st.markdown("<h1 style='text-align: center; color: black; font-weight:100;'><b>Home</b></h1 >",
                    unsafe_allow_html=True)
        st.markdown(
            """
            ---
            This program provides a set of powerful tools & analytics to help with your stock research.
            If you have a suggestion for improvement or feedback, please contact [Tim Zhang](mailto:timzhang0702@gmail.com)
            ### What's Provided?
            - Interactive stock charts
            - Popular indicators (Bollinger Bands, RSI, SMA)
            - Twitter sentiment for individual stocks
            - Select the Search dashboard from the filters to learn more! 
            ### Coming Soon...
            - Stock screener lists (Increased Volume, Uptrend Pullback, Bollinger Bands Squeeze) 
            ---
            """
        )

        email()

        footer()
    except:
        st.info('Page In Development')

if option == 'Increased Volume':
    try:
        increased_volume()
        Symbol, Open, High, Low, Close, Volume, pctchange = sheets(url = 'https://stock-screener.org/unusual-volume-stocks.aspx')

        tickerSymbol = st.sidebar.selectbox('Stock Ticker', Symbol)  # Select ticker symbol
        if tickerSymbol == 'Summary of Stocks':
            table(Symbol, Open, High, Low, Close, Volume, pctchange)
        else:
            range = st.sidebar.selectbox("Date Range", (
                '1 Month', '3 Months', '6 Months', '1 Year'), 1)
            try:
                string_name, string_summary, fig, config = chart(range, tickerSymbol)
                st.markdown(
                    "<h2 style='text-align: center; color: black; font-weight:100;'><b>Business Summary</b></h2 >",
                    unsafe_allow_html=True)
                st.write("---")
                st.info(string_summary)
                st.write("---")
                st.markdown("<h2 style='text-align: center; color: black;'><b>Interactive Stock Chart</b></h2 >",
                            unsafe_allow_html=True)
                st.write("---")
                st.plotly_chart(fig, config=config)

                agree = st.sidebar.checkbox("Show Twitter Sentiment Analysis")

                if agree:
                    taWrite()
                    fig, config = ta(tickerSymbol)
                    st.plotly_chart(fig, config=config)

            except:
                st.info('Ticker Symbol Not Found')
        email()
        footer()
    except:
        st.info('Page In Development')

if option == 'Uptrend Pullback':
    try:
        uptrend_pullback()
        Symbol, Open, High, Low, Close, Volume, pctchange = sheets(
            url='https://stock-screener.org/pullback-stock-screener.aspx')

        tickerSymbol = st.sidebar.selectbox('Stock Ticker', Symbol)  # Select ticker symbol
        if tickerSymbol == 'Summary of Stocks':
            table(Symbol, Open, High, Low, Close, Volume, pctchange)
        else:
            range = st.sidebar.selectbox("Date Range", (
                '1 Month', '3 Months', '6 Months', '1 Year'), 1)
            try:
                string_name, string_summary, fig, config = chart(range, tickerSymbol)
                st.markdown(
                    "<h2 style='text-align: center; color: black; font-weight:100;'><b>Business Summary</b></h2 >",
                    unsafe_allow_html=True)
                st.write("---")
                st.info(string_summary)
                st.write("---")
                st.markdown("<h2 style='text-align: center; color: black;'><b>Interactive Stock Chart</b></h2 >",
                            unsafe_allow_html=True)
                st.write("---")
                st.plotly_chart(fig, config=config)

                agree = st.sidebar.checkbox("Show Twitter Sentiment Analysis")

                if agree:
                    taWrite()
                    fig, config = ta(tickerSymbol)
                    st.plotly_chart(fig, config=config)

            except:
                st.info('Ticker Symbol Not Found')
        email()
        footer()

    except:
        st.info('Page In Development')

if option == 'Bollinger Bands Squeeze':
    try:
        bbs()
        Symbol, Open, High, Low, Close, Volume, pctchange = sheets(
            url='https://stock-screener.org/pullback-stock-screener.aspx')

        tickerSymbol = st.sidebar.selectbox('Stock Ticker', Symbol)  # Select ticker symbol
        if tickerSymbol == 'Summary of Stocks':
            table(Symbol, Open, High, Low, Close, Volume, pctchange)
        else:
            range = st.sidebar.selectbox("Date Range", (
                '1 Month', '3 Months', '6 Months', '1 Year'), 1)
            try:
                string_name, string_summary, fig, config = chart(range, tickerSymbol)
                st.markdown(
                    "<h2 style='text-align: center; color: black; font-weight:100;'><b>Business Summary</b></h2 >",
                    unsafe_allow_html=True)
                st.write("---")
                st.info(string_summary)
                st.write("---")
                st.markdown("<h2 style='text-align: center; color: black;'><b>Interactive Stock Chart</b></h2 >",
                            unsafe_allow_html=True)
                st.write("---")
                st.plotly_chart(fig, config=config)

                agree = st.sidebar.checkbox("Show Twitter Sentiment Analysis")

                if agree:
                    taWrite()
                    fig, config = ta(tickerSymbol)
                    st.plotly_chart(fig, config=config)

            except:
                st.info('Ticker Symbol Not Found')
        email()
        footer()
    except:
        st.info('Page In Development')

if option == 'Search':
    try:
        search()
        session_state = SessionState.get(checkboxed=False)
        with st.form(key='my_form1'):
            col1, col2 = st.beta_columns([6.3, 1])
            with col1:
                tickerSymbol = st.text_input('Enter A Stock Ticker', 'AAPL')
            with col2:
                st.header('')
                submit_button = st.form_submit_button(label="Search")

        if submit_button or session_state.checkboxed:
            session_state.checkboxed = True

            range = st.sidebar.selectbox("Date Range", (
                '1 Month', '3 Months', '6 Months', '1 Year'), 1)
            
            try:
                string_name, string_summary, fig, config = chart(range, tickerSymbol)
                st.markdown(
                    "<h2 style='text-align: center; color: black; font-weight:100;'><b>Business Summary</b></h2 >",
                    unsafe_allow_html=True)
                st.write("---")
                st.info(string_summary)
                st.write("---")
                st.markdown("<h2 style='text-align: center; color: black;'><b>Interactive Stock Chart</b></h2 >",
                            unsafe_allow_html=True)
                st.write("---")
                st.plotly_chart(fig, config=config)

                agree = st.sidebar.checkbox("Show Twitter Sentiment Analysis")

                if agree:
                    taWrite()
                    fig, config = ta(tickerSymbol)
                    st.plotly_chart(fig, config=config)
                email()

            except:
                st.info('Ticker Symbol Not Found')
        
        footer()
    except:
        st.info('Page In Development')










