#!/usr/bin/env python

import sys
import sqlite3 as sql

def getIntroTable(dbname):
    db = sql.connect(dbname)
    try:
        c = db.cursor()
        for row in c.execute("select g.v, s.v, count(*) from OralVantage o, Genus g, Species s where o.genus=g.idx and o.species=s.idx group by genus, species;"):
            sys.stdout.write("<tr><td>{}</td><td>{} {}</td><td class='w3-right-align'>{}</td></tr>\n".format(row[0], row[0], row[1], row[2]))
    finally:
        db.close()

def resultsTable():
    rows = [ ("GenBank accession no.", "a unique identifier for a sequence deposited in GenBank.") ]
    for row in rows:
        sys.stdout.write("<tr><td>{}</td><td>{}</td></tr>\n".format(row[0], row[1]))

if __name__ == "__main__":
    dbname = sys.argv[1]
    what = sys.argv[2]
    if what == 'intro':
        getIntroTable(dbname)
    elif what == 'results':
        resultsTable()
