from flask import Flask, request, redirect, url_for
from flask import render_template
import requests
import re

app = Flask(__name__)


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
