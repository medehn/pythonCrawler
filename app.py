from flask import Flask, request, redirect, url_for
from flask import render_template
import requests
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Base, BaseUrl, RelatedLinks
from sqlalchemy.orm import scoped_session
from sqlalchemy.sql.expression import select, exists

app = Flask(__name__)

engine = create_engine('sqlite:///linklist.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = scoped_session(DBSession)


@app.route('/linklist')
def showLinks():
    links = session.query(BaseUrl).all()
    relatedLinks = session.query(RelatedLinks).all()

    return render_template("linklist.html", links=links, relatedLinks=relatedLinks)


@app.route('/', methods=["GET", "POST"])
def getLinks():
    if request.method == "POST":
        inputUrl = request.form['inputUrl']

        # get list of links
        siteRequest = requests.get(inputUrl)
        linkList = re.findall(r'<a[^>]* href="([^"]*)"', str(siteRequest.content))
        internalLinks = []
        externalLinks = linkList.copy()

        # database communication
        urlInDb = session.query(exists().where(BaseUrl.baseUrl == inputUrl)).scalar()
        if not urlInDb:
            newBaseUrl = BaseUrl(baseUrl=inputUrl)
            session.add(newBaseUrl)

            for link in linkList:
                newRelatedLink = RelatedLinks(linkUrl=link)
                session.add(newRelatedLink)

            session.commit()

        # order lists

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
