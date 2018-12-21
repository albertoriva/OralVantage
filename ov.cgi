#!/usr/bin/env python

import ov
import sys
import cgi
import sqlite3 as sql

DBNAME = "OralVantage.db"

# Form fields

class FormField():
    name = ""
    label = ""
    placeholder = ""

    def __init__(self, name, label, placeholder=None):
        self.name = name
        self.label = label
        if placeholder:
            self.placeholder = placeholder
        else:
            self.placeholder = "Enter " + self.label.lower()

class LookupField(FormField):
    table = ""

    def __init__(self, name, label, table):
        self.name = name
        self.label = label
        self.table = table
    
# Queries

def getIntroTable(dbname):
    total = 0
    db = sql.connect(dbname)
    try:
        c = db.cursor()
        for row in c.execute("select g.v, s.v, count(*) from OralVantage o, Genus g, Species s where o.genus=g.idx and o.species=s.idx group by genus, species;"):
            sys.stdout.write("<tr><td>{}</td><td>{} {}</td><td class='w3-right-align'>{}</td></tr>\n".format(row[0], row[0], row[1], row[2]))
            total += row[2]
        sys.stdout.write("<tr><td><b>Total genomes:</b></td><td></td><td class='w3-right-align'><b>{}</b></td></tr>\n".format(total))
    finally:
        db.close()

def resultsTable():
    for ff in ov.GOODFIELDS:
        if ff.desc:
            sys.stdout.write("<tr><td>{}</td><td>{}</td></tr>\n".format(ff.label, ff.desc))

def buildQuery(fields):
    terms = []
    for ff in ov.FIELDS:
        if ff.srch and ff.name in fields:
            val = fields[ff.name].value
            if val != '0':
                w = "{}='{}'".format(ff.name, fields[ff.name].value)
                terms.append(w)
    return " AND ".join(terms)

# Page generation

def getFields():
    form = cgi.FieldStorage()
    return form

def writeHeader(pg):
    sys.stdout.write("""<!DOCTYPE html>
<html>
  <head>
    <title>OralVantage - Human Oral Pathogens Database</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="ov.css">
    <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
  </head>
  <body>

    <div class="w3-cell-row w3-indigo">
      <div class="w3-cell w3-cell-middle m2 w3-left-align"><IMG src="OV_logo_small.png" /></div>
      <div class="w3-cell w3-cell-middle m4 w3-right-align w3-xxlarge">OralVantage</div>
      <div class="w3-cell w3-cell-middle m4 w3-left-align w3-xlarge"> - Human Oral Pathogens Database</div>
      <div class="w3-cell w3-cell-middle m2 w3-cell-middle w3-right-align"><IMG src="uf-logo-white.png" /></div>
    </div>

  <div class="w3-bar w3-light-blue">
    <a href="?pg=home" class="w3-bar-item w3-button{}">Home</a>
    <a href="?pg=what" class="w3-bar-item w3-button{}">What is OV?</a>
    <a href="?pg=search" class="w3-bar-item w3-button{}">Search OV</a>
    <a href="?pg=results" class="w3-bar-item w3-button{}">Results guide</a>
    <a href="?pg=submit" class="w3-bar-item w3-button{}">Submit sequence info</a>
    <a href="?pg=publications" class="w3-bar-item w3-button{}">Publications</a>
  </div>

  <div class="w3-container">
    """.format(" w3-white" if pg == "home" else "",
               " w3-white" if pg == "what" else "",
               " w3-white" if pg == "search" else "",
               " w3-white" if pg == "results" else "",
               " w3-white" if pg == "submit" else "",
               " w3-white" if pg == "publications" else ""))

def writeFooter():
    sys.stdout.write("""  </div>
<br><br>
<div class='footer w3-indigo'>&nbsp; &copy; 2018 Y. Alsahafi, A. Riva, University of Florida.</test>
</body>
</html> 
""")

# Pages

def homePage():
    sys.stdout.write("""<h2>OralVantage - Home</h2>
<p><strong>OralVantage</strong> is a database of oral disease-associated bacteria. It was developed by 
<A href="https://www.linkedin.com/in/yaser-alsahafi-49b73255" target="_blank">Yaser Alsahafi</A> at the 
<A href="http://egh.phhp.ufl.edu/" target="_blank">Department of Environmental & Global Health</A> and the <A href="http://www.epi.ufl.edu/" target="_blank">Emerging Pathogens Institute</A> 
at the <A href="http://www.ufl.edu/" target="_blank">University of Florida</A>.</p>

<p>The <A href="?pg=what">What is OV?</A> page describes the contents of the OralVantage database and provides summary information
about it. Use the <A href="?pg=search">Query OV</A> page to query the database. The <A href="?pg=results">Results guide</A> page
provides a description of the query results. If you would like to submit an entry to the 
OralVantage database, please use the form in the <A href="?pg=submit">Submit sequence info</A> page. The <A href="?pg=publications">Publications<A>
page lists publications about OralVantage.</P>
""")


def whatPage():
    sys.stdout.write("""<h2>OralVantage - Introduction</h2>
    <P>OralVantage is a reference database containing full genomes of oral disease-associated bacteria, corresponding both to health or disease conditions.
    The meta-information of sequences describes both patient's characteristics (including demographic and clinical attributes) and bacterial
      characteristics (including isolation, sequencing, and genetic information).</P>
    <P>The database contains the description for the following oral bacteria:</P>

    <div class="w3-row">
      <div class="w3-col m2 w3-center">&nbsp;</div>
      <div class="w3-col m8 w3-center">
	<table class="w3-table w3-bordered w3-striped w3-small">
	  <tr><th>Genus</th><th>Species</th><th class="w3-right-align">No. of genomes</th></tr>
""")
    getIntroTable(DBNAME)
    sys.stdout.write("""
	</table>
      </div>
      <div class="w3-col m2 w3-center">&nbsp;</div>
    </div>
""")

def searchPage():
    conn = sql.connect(DBNAME)
    sys.stdout.write("""<h2>OralVantage - Search</h2>
    <P>Please enter your search terms in the form below and press the <b>Search</b> button. Hover over the question mark for a description of each field.</P>
    <div class="w3-row">
      <div class="w3-col m2 w3-center">&nbsp;</div>
      <div class="w3-col m8 w3-left">
        <table>
        <form class="w3-container" method="post" action="ov.cgi">
          <input type="hidden" name="cmd" value="search">
          <input type="hidden" name="pg" value="search">
""")
    for ff in ov.FIELDS:
        if ff.srch:
            ff.mkInput(conn)
    sys.stdout.write("""
          <tr><td colspan="3"><button class="w3-btn w3-indigo w3-round">Search</button></td></tr>
          </form>
        </table>
      </div>
      <div class="w3-col m2 w3-center">&nbsp;</div>
    </div>
""")
    conn.close()

def resultsPage():
    sys.stdout.write("""<h2>OralVantage - Results Guide</h2>
    <P>The following table describes the content of each column in the output result.</P>

    <div class="w3-row">
      <div class="w3-col m2 w3-center">&nbsp;</div>
      <div class="w3-col m8 w3-center">
	<table class="w3-table w3-bordered w3-striped w3-small">
	  <tr><th>Column Title</th><th>Description</th></tr>
""")
    resultsTable()
    sys.stdout.write("""
	</table>
      </div>
      <div class="w3-col m2 w3-center">&nbsp;</div>
    </div>
""")

def publicationsPage():
    sys.stdout.write("""<h2>OralVantage - Publications</h2>
<P>This page lists publications about OralVantage.</P>

<OL>
    <LI>OralVantage: Comprehensive Database for Disease-associated Oral Bacteria, Yaser Alsahafi, Carla Mavian, Alberto Riva, Marco Salemi, <i>J Dent Res</i>: 1652,218 (<A href="www.iadr.org">www.iadr.org</A>). </LI>
</OL>
""")

def submitPage():
    sys.stdout.write("""<h2>OralVantage - Submit</h2>
<P>To submit new sequences to the OralVantage database, please contact <A href='mailto:dr.alsahafi@alum.bu.edu'>Yaser Alsahafi</a>.</P>
""")

# Search results

def doSearch(form):
    ids = []
    q = buildQuery(form)
    conn = sql.connect(DBNAME)
    try:
        c = conn.cursor()
        if q:
            query = "SELECT genbank FROM OralVantage WHERE " + q + ";"
        else:
            query = "SELECT genbank FROM OralVantage;"
        for row in c.execute(query):
            ids.append(row[0])

        sys.stdout.write("""<h2>OralVantage - Search Results</h2>
    <P>The following table contains the results of your search ({} records returned). The table is divided into four sections for readability; please use the buttons below to switch between sections.</P>
        """.format(len(ids)))

        if ids:
            sys.stdout.write("""<SCRIPT lang="javascript">
            function openTab(tabName, btnName) {
    var i;
    var x = document.getElementsByClassName("tabletab");
    for (i = 0; i < x.length; i++) {
        x[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablink");
    for (i = 0; i < x.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" w3-red", "");
    }
    document.getElementById(tabName).style.display = "block";
    document.getElementById(btnName).className += " w3-red";
}
</SCRIPT>
""")
            sys.stdout.write("""<DIV class="w3bar w3-grey">
            <button id='btn1' class="tablink w3-bar-item w3-button w3-red" onclick="openTab('tab1', 'btn1')">General</button>
            <button id='btn2' class="tablink w3-bar-item w3-button" onclick="openTab('tab2', 'btn2')">Genome</button>
            <button id='btn3' class="tablink w3-bar-item w3-button" onclick="openTab('tab3', 'btn3')">Sample</button>
            <button id='btn4' class="tablink w3-bar-item w3-button" onclick="openTab('tab4', 'btn4')">Subject</button>
</DIV>
""")
            colnames = ov.colNames()
            for tab in ["1", "2", "3", "4"]:
                disp = " style='display:none'"
                sys.stdout.write("<div id='tab{}' class='tabletab'{}>".format(tab, "" if tab=="1" else disp))
                sys.stdout.write("<table class='w3-table w3-bordered w3-striped w3-small'>\n")
                sys.stdout.write("<TR>")
                for ff in ov.GOODFIELDS:
                    if ff.page == "0" or tab in ff.page:
                        sys.stdout.write("<TH>{}</TH>".format(ff.label))
                sys.stdout.write("</TR>\n")
                for id in ids:
                    row = ov.getRow(c, id, colnames)
                    sys.stdout.write("  <TR>")
                    i = 0
                    for ff in ov.GOODFIELDS:
                        if ff.page == "0" or tab in ff.page:
                            value = row[i]
                            showf = ff.showf
                            display = showf(ff, value, c)
                            sys.stdout.write("<TD>{}</TD>".format(display))
                        i += 1
                    sys.stdout.write("  </TR>\n")
                sys.stdout.write("</table>\n</div>\n")
                
        else:
            sys.stdout.write("No results.")
    finally:
        conn.close()

def main():
    form = getFields()
    if "pg" in form:
        pg = form["pg"].value
    else:
        pg = "home"
    writeHeader(pg)
    if "cmd" in form:
        cmd = form["cmd"].value
        if cmd == "search":
            doSearch(form)
    elif pg == "home":
        homePage()
    elif pg == "what":
        whatPage()
    elif pg == "search":
        searchPage()
    elif pg == "results":
        resultsPage()
    elif pg == "publications":
        publicationsPage()
    elif pg == "submit":
        submitPage()
    writeFooter()

if __name__ == "__main__":
   sys.stdout.write("Content-type: text/html\n\n")
   main()

