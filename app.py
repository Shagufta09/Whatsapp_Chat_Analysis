from flask import Flask, render_template, request
import re
import nltk
nltk.download('vader_lexicon')
# Add more datasets as needed

import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import os
print(os.getcwd())


app = Flask(__name__, template_folder='/Users/mymac/Documents/WhatsApp_Chat_Sentiment_Analysis/docs')

print(app.jinja_loader.searchpath)
@app.route('/')
def upload_file():
    return render_template('upload.html')

@app.route('/result', methods=['POST', 'GET'])
def result():
    if request.method == 'POST':
        f = request.files['file']
        conversation = f.read().decode("utf-8")

        def date_time(s):
            pattern='^([0-9]{2})\/([0-9]{2})\/([0-9]{2}), ([0-9]{1,2}):([0-9]{2})\s?(am|pm|AM|PM)? -'
            result=re.match(pattern, s)
            if result:
                return True
            return False

        def find_contact(s):
            s=s.split(":")
            if len(s)==2:
                return True
            else:
                return False

        def getMassage(line):
            splitline=line.split(' - ')
            datetime= splitline[0];
            date, time= datetime.split(', ')
            message=" ".join(splitline[1:])

            if find_contact(message):
                splitmessage=message.split(": ")
                author=splitmessage[0]
                message=splitmessage[1]
            else:
                author=None
            return date, time, author, message

        data=[]
        messageBuffer=[]
        date, time, author= None, None, None
        for line in conversation.split('\n'):
            line=line.strip()
            if date_time(line):
                if len(messageBuffer) >0:
                    data.append([date, time, author, ''.join(messageBuffer)])
                messageBuffer.clear()
                date, time, author, message=getMassage(line)
                messageBuffer.append(message)
            else:
                messageBuffer.append(line)

        df=pd.DataFrame(data, columns=["Date", "Time", "contact", "Message"])
        df['Date']=pd.to_datetime(df['Date'])

        data=df.dropna()
        sentiments=SentimentIntensityAnalyzer()
        data["positive"]=[sentiments.polarity_scores(i)["pos"] for i in data["Message"]]
        data["negative"]=[sentiments.polarity_scores(i)["neg"] for i in data["Message"]]
        data["neutral"]=[sentiments.polarity_scores(i)["neu"] for i in data["Message"]]

        x=sum(data['positive'])
        y=sum(data['negative'])
        z=sum(data['neutral'])

        def score(a,b,c):
            if(a>b) and (a>c):
                return "Sentiment: Positive 😄"
            elif (b>a) and (b>c):
                return "Sentiment: Negative 😔"
            else:
                return "Sentiment: Neutral 🙂"

        sentiment = score(x, y, z)
        return render_template("result.html", sentiment=sentiment)

if __name__ == '__main__':
    app.run(debug=True)
