from flask import Flask, request, redirect, url_for
from flask import render_template
import requests
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Base, LinkList
from sqlalchemy.orm import scoped_session

app = Flask(__name__)

engine = create_engine('sqlite:///linklist.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = scoped_session(DBSession)


@app.route('/linklist')
def showLinks():

   links = session.query(LinkList).all()

   testLink = LinkList(inputUrl="www.test.at", links="ein Link")
   testLink2 = LinkList(inputUrl="www.nocheinlink.at", links="du doof Link")
   session.add(testLink)
   session.add(testLink2)
   session.commit()

   return render_template("linklist.html", links=links)

# def newLink():
#    if request.method == 'POST':
#        newLink = LinkList(inputUrl = request.form['inputUrl'], links = request.form['links'])
#        session.add(newLink)
#        session.commit()
#        return redirect(url_for('showLinks'))




@app.route('/', methods=["GET", "POST"])
def getLinks():
    if request.method == "POST":
        inputUrl = request.form['inputUrl']

        siteRequest = requests.get(inputUrl)
        linkList = re.findall(r'<a[^>]* href="([^"]*)"', str(siteRequest.content))
        internalLinks = []
        externalLinks = linkList.copy()

        for link in linkList:
            if link.startswith(siteRequest.url) or link.startswith('#'):
                newLink = link.split(siteRequest.url)
                internalLinks.append('/' + newLink[-1])
                externalLinks.remove(link)


        internalLinks.sort()
        externalLinks.sort()

        return render_template("results.html", inputUrl=inputUrl, intern=internalLinks, extern=externalLinks)

    else:
        return render_template("results.html")


if __name__ == '__main__':
    app.run()
