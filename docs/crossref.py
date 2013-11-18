#!/usr/bin/env python
#encoding: utf-8
#originally from http://www.thamnos.de/misc/look-up-bibliographical-information-from-a-doi/

#
# to use -- do a chmod a+x crossref.org, find a doi and then do (for example):
# crossref.py 10.5194/acp-13-9855-2013, which will produce:

#@ARTICLE{Gettelman13,
#author = {Gettelman, A. and Morrison, H. and Terai, C. R. and Wood, R.},
#title = {Microphysical process rates and global aerosolcloud interactions},
#journal = {Atmos. Chem. Phys.},
#volume = {13},
#number = {19},
#year = {2013},
#pages = {9855-9867},
#doi = {10.5194/acp-13-9855-2013},
#resource = {http://ezproxy.library.ubc.ca/login?url=http://www.atmos-chem-phys.net/13/9855/2013/},
#}

#
# in this case visiting the resource url will fail, because ACP is an open access
# journal, so just edit it to:
# resource = {http://www.atmos-chem-phys.net/13/9855/2013/},
#


debug = False

#register for an api key (your ubc email address) from
#http://www.crossref.org/requestaccount/

crossref_api_key = 'put email address here'
 
# get the doi
import sys
from string import strip
for arg in sys.argv[1:]:
    arg = strip(arg)
    arg = strip(arg, chars="doi:")
    arg = strip(arg, chars="http://")
    arg = strip(arg, chars="dx.doi.org/")
    doi = strip(arg)
 
    # clear from previous
    text_journal_title = ""
    text_year = ""
    text_volume = ""
    text_issue = ""
    text_title = ""
    text_first_author_surname = ""
    text_first_page = ""
    text_last_page = ""
    authorlist = []
 
    # download the xml
    import urllib
    from xml.dom import minidom
    usock = urllib.urlopen('http://www.crossref.org/openurl/?id=doi:'+doi+'&noredirect=true&pid='+crossref_api_key+'&format=unixref')
    xmldoc = minidom.parse(usock)
    usock.close()
 
    if debug:
        out=xmldoc.toxml()
        print out.encode('ascii','ignore')
    print ""
 
    a = xmldoc.getElementsByTagName("doi_records")[0]
    b = a.getElementsByTagName("doi_record")[0]
    c = b.getElementsByTagName("crossref")[0]
    d = c.getElementsByTagName("journal")[0]
 
    journal_meta = d.getElementsByTagName("journal_metadata")[0]
    journal_title = journal_meta.getElementsByTagName("full_title")[0]
    abbrev_title = journal_meta.getElementsByTagName("abbrev_title")[0]
    text_journal_title = journal_title.firstChild.data.encode('ascii', 'ignore')
    abbrev_journal_title = abbrev_title.firstChild.data.encode('ascii', 'ignore')
    journal_issue = d.getElementsByTagName("journal_issue")[0]
    date = journal_issue.getElementsByTagName("publication_date")[0]
    year = date.getElementsByTagName("year")[0]
    text_year = year.firstChild.data.encode('ascii', 'ignore')
    resource = d.getElementsByTagName("resource")[0]
    resource=resource.firstChild.data.encode('ascii', 'ignore')
 
    try:
        journal_volume = journal_issue.getElementsByTagName("journal_volume")[0]
        volume = journal_issue.getElementsByTagName("volume")[0]
        text_volume = volume.firstChild.data.encode('ascii', 'ignore')
    except IndexError:
        pass
 
    try:
        issue = journal_issue.getElementsByTagName("issue")[0]
        text_issue = issue.firstChild.data.encode('ascii', 'ignore')
    except IndexError:
        pass
 
    journal_article = d.getElementsByTagName("journal_article")[0]
    titles = journal_article.getElementsByTagName("titles")[0]
    title = titles.getElementsByTagName("title")[0]
    text_title = title.firstChild.data.encode('ascii', 'ignore')
 
    contributors = journal_article.getElementsByTagName("contributors")[0]
    for person_name in contributors.getElementsByTagName("person_name"):
        text_given_name = ""
        text_surname = ""
        # get names
        given_name = person_name.getElementsByTagName("given_name")[0]
        text_given_name = given_name.firstChild.data.encode('ascii', 'ignore')
        surname = person_name.getElementsByTagName("surname")[0]
        text_surname = surname.firstChild.data.encode('ascii', 'ignore')
        authorlist.append(text_surname+", "+text_given_name)
        #first author?
        sequence = person_name.attributes.getNamedItem("sequence")
        if sequence.nodeValue == 'first':
            text_first_author_surname = text_surname
 
    try:
        pages = journal_article.getElementsByTagName("pages")[0]
    except:
        pages = None
    try:
        first_page = pages.getElementsByTagName("first_page")[0]
        text_first_page = first_page.firstChild.data.encode('ascii', 'ignore')
    except:
        pass
    try:
        last_page = pages.getElementsByTagName("last_page")[0]
        text_last_page = last_page.firstChild.data.encode('ascii', 'ignore')
    except:
        pass
    # physical review
    if pages == None:
        try:
            pages = journal_article.getElementsByTagName("publisher_item")[0]
        except:
            pages = None
        try:
            first_page = pages.getElementsByTagName("item_number")[0]
            text_first_page = first_page.firstChild.data.encode('ascii', 'ignore')
        except:
            pass
 
    # output
 
    print "@ARTICLE{"+text_first_author_surname+text_year[-2:]+","
    print "author = {"+" and ".join(authorlist)+"},"
    print "title = {"+text_title+"},"
    print "journal = {"+abbrev_journal_title+"},"
    if not text_volume == "":
        print "volume = {"+text_volume+"},"
    if not text_issue == "":
        print "number = {"+text_issue+"},"
    print "year = {"+text_year+"},"
    if ((text_first_page != "") and (text_last_page != "")):
        print "pages = {"+text_first_page+"-"+text_last_page+"},"
    if ((text_first_page != "") and (text_last_page == "")):
        print "pages = {"+text_first_page+"},"
    print "doi = {"+doi+"},"
    print "resource = {http://ezproxy.library.ubc.ca/login?url="+resource+"},"
    print "}"
