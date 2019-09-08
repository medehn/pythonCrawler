from flask import Flask, request, abort
from flask import render_template
import requests
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Base, BaseUrl, RelatedLinks
from sqlalchemy.orm import scoped_session
from sqlalchemy.sql.expression import exists

app = Flask(__name__)

engine = create_engine('sqlite:///linklist.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = scoped_session(DBSession)


# @app.route('/linklist')
# def showLinks():
#     links = session.query(BaseUrl).all()
#     related_links = session.query(RelatedLinks).all()
#
#     return render_template("linklist.html", links=links, relatedLinks=related_links)


@app.route('/', methods=["GET", "POST"])
def getLinks():
    if request.method == "POST":

        checkAndAddToDB()

        # get list of links
        input_url = request.form['inputUrl']
        site_request = requests.get(input_url)
        link_list = re.findall(r'<a[^>]* href="([^"]*)"', str(site_request.content))
        internal_links = []
        external_links = link_list.copy()

        urlInDb = session.query(exists().where(BaseUrl.baseUrl == input_url)).scalar()

        if not urlInDb:
            for link in link_list:
                if link.startswith(site_request.url) or link.startswith('#'):
                    new_link = link.split(site_request.url)
                    internal_links.append(new_link[-1])
                    if link in external_links:
                        external_links.remove(link)

        else:
            baseUrlObject = session.query(BaseUrl).filter_by(baseUrl=input_url).one()
            linkList = baseUrlObject.links

            for link in linkList:
                link = link.linkUrl
                if link.startswith(site_request.url)or link.startswith('#')or link.startswith('/'):
                    newLink = link.split(site_request.url)
                    internal_links.append(newLink[-1])
                    if link in external_links:
                        external_links.remove(link)

        internal_links.sort()
        external_links.sort()

        return render_template("results.html", inputUrl=input_url, intern=internal_links, extern=external_links)

    else:
        return render_template("results.html")


def checkAndAddToDB():
    # database communication
    try:
        input_url = request.form['inputUrl']

    # get list of links
        site_request = requests.get(input_url)
        link_list = re.findall(r'<a[^>]* href="([^"]*)"', str(site_request.content))

    except:
        abort(500, "Please provide an URL with  http://... or https://.")

    urlInDb = session.query(exists().where(BaseUrl.baseUrl == input_url)).scalar()
    if not urlInDb:
        new_base_url = BaseUrl(baseUrl=input_url)
        session.add(new_base_url)
        session.flush()

        for link in link_list:
            newRelatedLink = RelatedLinks(linkUrl=link, linklist_id=new_base_url.id)

            session.add(newRelatedLink)

        session.commit()

    else:
        print("nur bei alten links!")


if __name__ == '__main__':
    app.run()
