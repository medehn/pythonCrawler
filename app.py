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

# connection to db
engine = create_engine('sqlite:///linklist.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = scoped_session(DBSession)


@app.route('/', methods=["GET", "POST"])
def get_links():
    if request.method == "POST":
        # error handling to give feedback to user if an invalid URL was passed
        try:
            input_url = request.form['inputUrl']
            site_request = requests.get(input_url)
        except ValueError:
            abort(500, "Please provide a working URL with  http://... or https://.")

        link_list = re.findall(r'<a[^>]* href="([^"]*)"', str(site_request.content))

        # sort links into internal/external
        internal_links = []
        external_links = link_list.copy()

        url_in_db = session.query(exists().where(BaseUrl.baseUrl == input_url)).scalar()

        # checking for links that have not yet been added to search history/db
        if not url_in_db:
            sort_links(external_links, internal_links, link_list, site_request)
            add_to_db(input_url, link_list)
        # if in db - read entries from db
        else:
            base_url_object = session.query(BaseUrl).filter_by(baseUrl=input_url).one()
            db_link_list = base_url_object.links
            sort_db_list(external_links, internal_links, db_link_list, site_request)

        internal_links.sort()
        external_links.sort()

        return render_template("results.html", inputUrl=input_url, intern=internal_links, extern=external_links)

    else:
        return render_template("results.html")


def sort_db_list(external_links, internal_links, linkList, site_request):
    for link in linkList:
        linkUrl = link.linkUrl
        if linkUrl.startswith(site_request.url) or linkUrl.startswith('#') or linkUrl.startswith('/'):
            new_link = linkUrl.split(site_request.url)
            internal_links.append(new_link[-1])
            if linkUrl in external_links:
                external_links.remove(linkUrl)


def sort_links(external_links, internal_links, link_list, site_request):
    for link in link_list:
        if link.startswith(site_request.url) or link.startswith('#') or link.startswith('/'):
            new_link = link.split(site_request.url)
            internal_links.append(new_link[-1])
            if link in external_links:
                external_links.remove(link)


def add_to_db(input_url, link_list):
    # database communication, add base-Url and related links

    new_base_url = BaseUrl(baseUrl=input_url)
    session.add(new_base_url)
    session.flush()

    for link in link_list:
        new_related_link = RelatedLinks(linkUrl=link, linklist_id=new_base_url.id)
        session.add(new_related_link)

    session.commit()


if __name__ == '__main__':
    app.run()
