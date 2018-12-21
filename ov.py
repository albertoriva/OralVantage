#!/usr/bin/env python

import sys		#import systems module
import sqlite3	#import SQLite used for lightweight disk-based database

## fields types:
## -1 = skip
##  0 = field should be stored as is
##  1 = link to lookup table
##  2 = one-to-many table

# Default show function
def show(field, value, conn):
    return value;

def lookup(field, value, conn):
    conn.execute("SELECT v FROM {} WHERE idx=?".format(field.table), (value,))
    # print "SELECT v FROM {} WHERE idx={}<br>".format(field.table, value)
    row = conn.fetchone()
    return row[0]

def genbankField(field, value, conn):
    return "<A href='https://www.ncbi.nlm.nih.gov/gquery/?term={}' target='ncbi'>{}</A>".format(value, value)

def pubmedField(field, value, conn):
    ids = []
    for row in conn.execute("SELECT v FROM {} WHERE idx=?".format(field.table), (value,)):
        ids.append(row[0])
    if ids:
        links = []
        for id in ids:
            links.append("<A href='https://www.ncbi.nlm.nih.gov/pubmed/{}' target='pubmed'>{}</A>".format(id, id))
        return "<BR>".join(links)
    else:
        return "."

class Field():
    name = ""
    type = 0
    desc = ""
    label = ""
    placeholder = ""
    func = None
    srch = False
    showf = show
    page = 1

    def __init__(self, name, label="", func=None, srch=False, showf=show, page=1, desc=""):
        self.name = name
        self.label = label or name
        self.func = func
        self.srch = srch
        self.placeholder = "Enter " + self.label.lower()
        self.showf = showf
        self.page = page
        self.desc = desc

    def mkInput(self, conn):
        sys.stdout.write("""<tr><td><label><b>{}</b></label></td>
<td><input name="{}" class="w3-input w3-border w3-round-large w3-hover-yellow" type="text" placeholder="{}"><br></td><td>&nbsp;&nbsp;<abbr title="{}"><span class="glyphicon glyphicon-question-sign"></span></abbr></td></tr>
        """.format(self.label, self.name, self.placeholder, self.desc))

class IgnoreField(Field):
    type = -1

    def __init__(self, name):
        self.name = name

class TableField(Field):
    type = 1
    encoding = {}               # For lookup tables

    def __init__(self, name, label="", func=None, srch=False, table="", showf=lookup, page=1, desc=""):
        self.name = name
        self.label = label or name
        self.func = func
        self.srch = srch
        self.table = table
        self.placeholder = "Enter " + self.label.lower()
        self.showf = showf
        self.page = page
        self.desc = desc

    def mkInput(self, conn):
        sys.stdout.write("""<tr><td><label><b>{}</b></label></td>
<td><SELECT class="w3-select w3-border w3-white w3-round-large w3-hover-yellow" name="{}">
""".format(self.label, self.name))
        getMenu(conn, self.table)
        sys.stdout.write("""</SELECT><br><br></td><td>&nbsp;&nbsp;<abbr title="{}"><span class="glyphicon glyphicon-question-sign"></span></abbr></td></tr>\n""".format(self.desc))

class MultiTableField(TableField):
    type = 2

def removeCommas(s, c=None):  #definition of a function to remove commas from variables values.
    return s.replace(",", "")

def storeVirulence(s, c):  # define a function to store virulence values in lockup tables, 'c' make connection to datbase
    if s == '' or s == '.':    # handeling missing values, by turning them into 0.
        return 0
    virs = s.split(",")			# removes commas within a string
    c.execute("SELECT max(idx) FROM Virulence;")
    m = c.fetchone()[0]
    if m == None:
        idx = 1
    else:
        idx = m + 1
    for p in virs:
        p = p.strip(" ") # strip: removes commas
        c.execute("INSERT INTO Virulence (idx, v) VALUES (?, ?);", (idx, p))
    return idx
    
def storePubmed(s, c):		# define a function to store pubmed reference values
    if s == '' or s == '.':	# identify empty cells or (.) as missing
        return 0
    pubmeds = s.split(",")
    c.execute("SELECT max(idx) FROM Refs;")
    m = c.fetchone()[0]
    if m == None:
        idx = 1
    else:
        idx = m + 1
    for p in pubmeds:
        p = p.strip(" ")
        c.execute("INSERT INTO Refs (idx, v) VALUES (?, ?);", (idx, p))
    return idx

FIELDS = [Field("genbank",
                srch=True,
                label="GenBank",
                showf=genbankField,
                page="0",
                desc="Unique identifier for a sequence deposited in GenBank."),

          Field("biosample",
                srch=True,
                label="Biosample",
                showf=genbankField,
                page="1",
                desc="NCBI identifier for this sample."),

          TableField("genus",
                     table="Genus",
                     srch=True,
                     label="Genus",
                     page="1",
                     desc="Pathogen genus."),

          TableField("species", 
                     table="Species", 
                     srch=True, 
                     label="Species",
                     page="1",
                     desc="Pathogen species."),

          Field("strain", 
                srch=True, 
                label="Strain",
                page="1",
                desc="Pathogen strain"),

          TableField("availableseq", 
                     table="Seqtype", 
                     srch=True, 
                     label="Available sequence",
                     page="1",
                     desc="The current sequencing status or sequencing level of this genome (i.e., complete: whole genome sequenced; WGS: show shotgun genome assembly)."),

          IgnoreField("downloaded"),

          Field("genecount", 
                label="Gene count",
                page="2",
                desc="Number of genes in this pathogen's genome."),

          Field("contigcount",
                label="Contig count",
                page="2",
                desc="Number of contigs in this pathogen's genome."),

          Field("genomesize",
                func=removeCommas,
                label="Genome size",
                page="2",
                desc="Size of this pathogen's genome in basepairs."),

          Field("crisprarrays",
                label="CRISPR arrays",
                page="2",
                desc="Number, name, or sequence of CRISPR arrays."),

          MultiTableField("virulencegenes", 
                          table="Virulence", 
                          func=storeVirulence,
                          label="Virulence genes",
                          page="2",
                          desc="Name of the virulence genes (usually common to the whole species)."),

          Field("collectiondate",
                label="Collection date",
                page="2",
                desc="Date the sample was collected from the subject."),

          Field("isolationregion", 
                srch=True, 
                label="Geographic location",
                page="2",
                desc="Geographic location of sample collection (i.e., country or city of collection)."),

          IgnoreField("country"),

          IgnoreField("collsite"),

          TableField("collection", 
                     table="Collection", 
                     srch=True, 
                     label="Collection site",
                     page="3",
                     desc="Organ or body system of collection."),

          TableField("subsite", 
                     table="Subsite", 
                     srch=True,
                     label="Collection subsite",
                     page="3",
                     desc="Specific anatomical location of collection within the collection site."),

          TableField("sampletype",
                     table="Sampletype",
                     srch=True,
                     label="Sample type",
                     page="3",
                     desc="Type of the collected sample."),

          Field("diagnosis",
                srch=True,
                label="Diagnosis",
                page="3",
                desc="Diagnosis of subject or collection subsite as described in the sequence or bacterial source."),

          TableField("healthstatus",
                     table="Healthstatus",
                     srch=True,
                     label="Health status",
                     page="43",
                     desc="Classification of oral and/or general health status of the subject."),

          TableField("severity",
                     table="Severity",
                     srch=True,
                     label="Severity",
                     page="3",
                     desc="Degree of disease severity."),

          TableField("agegroup",
                     table="Agegroup",
                     srch=True,
                     label="Age",
                     page="34",
                     desc="Subject age category (i.e., child vs. adult)."),

          TableField("gender",
                     table="Gender",
                     srch=True,
                     label="Gender",
                     page="34",
                     desc="Subject gender."),

          Field("ethnicity",
                srch=True,
                label="Ethnicity",
                page="34",
                desc="Subject ethnicity."),

          MultiTableField("reference",
                          label="References",
                          table="Refs",
                          func=storePubmed,
                          showf=pubmedField,
                          page="4",
                          desc="PubMed id(s) for sequence and/or strain related publications."),

          Field("contact",
                label="Contact",
                page="4",
                desc="Contact information for sequence and/or source bacteria laboratory."),

          Field("institution",
                label="Institution",
                page="4",
                desc="Name of the institution where the bacteria were isolated or sequenced.")]

GOODFIELDS = [ f for f in FIELDS if (f.type >= 0) ]

def getField(name):
    for f in FIELDS:
        if f.name == name:
            return f
    return None

OVDEFINITION = ["OralVantage", """genbank text, biosample text, genus int, species int, strain text, availableseq int, genecount int,
 contigcount int, genomesize int, crisprarrays int, virulencegenes int, collectiondate text, isolationregion text, collection int,
subsite int, sampletype int, diagnosis text, healthstatus int, severity int, agegroup text, gender int, ethnicity text, 
reference int, contact text, institution text"""]

LOOKUPS = ["Genus", "Species", "Seqtype", "Virulence", "Collection", "Subsite", "Sampletype", "Healthstatus", "Severity", "Gender", "Refs"]

def nColumns():  #define a column no. and fix it.
    n = 0
    for F in FIELDS:
        if F.type != -1:
            n += 1
    return n

def colNames(sep=","):	#define a function to give columns names and create a list of them
    names = []
    for F in GOODFIELDS:
        names.append(F.name)
    return sep.join(names)

def colPlaces():
    return ",".join(['?']*nColumns())

def initDatabase(filename):
    conn = sqlite3.connect(filename)
    c = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS {} ({});".format(OVDEFINITION[0], OVDEFINITION[1]))
    c.execute("CREATE INDEX IF NOT EXISTS ovindex ON {} (genbank);".format(OVDEFINITION[0]))

    for name in LOOKUPS:
        c.execute("CREATE TABLE IF NOT EXISTS {} (idx int, v text);".format(name))
        c.execute("CREATE INDEX IF NOT EXISTS {}_idx ON {} (idx)".format(name, name))

    conn.commit()
    conn.close()

def fillLookup(filename, col, table, c):  #defining a function to fill Lookup taples
    print "Creating lookup table {} from column {}".format(table, col)
    missing = ['', '.']
    values = []
    encoding = {'': 0, '.': 0}
    with open(filename, "r") as f:
        f.readline()            # Skip header
        for line in f:
            row = line.rstrip("\r\n").split("\t")
            if len(row) < col:
                print "Bad line: {}".format(row)
            v = row[col]
            if v not in values:
                values.append(v)

    # Now we have all unique values in the list
    c.execute("DELETE FROM {};".format(table))
    c.execute("INSERT INTO {} (idx, v) VALUES (0, NULL);".format(table))
    idx = 1
    for v in values:
        if v not in missing:
            encoding[v] = idx
            c.execute("INSERT INTO {} (idx, v) VALUES (?, ?);".format(table), (idx, v))
            idx += 1
    return encoding

def prepareDbRow(row, c):
    dbrow = []
    col = 0  
    for F in FIELDS:
        v = row[col]
        v = v.strip('"')
        if F.func != None:
            v = F.func(v, c)  
        if F.type == 0:
            dbrow.append(v)
        elif F.type == 1:
            idx = F.encoding[v]
            dbrow.append(idx)
        elif F.type == 2:
            dbrow.append(v)
        col += 1
    return dbrow

def loadDatabase(dbfile, filename):
    conn = sqlite3.connect(dbfile)
    c = conn.cursor()

    try:
        col = 0
        for F in FIELDS:
            if F.type == 1:           # Lookup table!
                F.encoding = fillLookup(filename, col, F.table, c)
            col += 1

        c.execute("DELETE FROM OralVantage;")
        c.execute("DELETE FROM Refs;")
        c.execute("DELETE FROM Virulence;")
        with open(filename, "r") as f:
            f.readline()
            for line in f:
                row = line.rstrip("\r\n").split("\t")
                dbrow = prepareDbRow(row, c)
                cmd = "INSERT INTO OralVantage ({}) VALUES ({});".format(colNames(), colPlaces())
                c.execute(cmd, dbrow)
    finally:
        conn.commit()
        conn.close()

### Queries

def getLookup(c, table, idx):
    """Retrieve the label associated with index idx in lookup table `table'. `conn' is the connection to the database."""
    query = "SELECT v FROM {} WHERE idx=?".format(table)
    c.execute(query, (idx,))
    row = c.fetchone()
    if row:
        #print "{} {} => {}".format(query, idx, row[0])
        v = row[0]
        if v == None:
            return ""
        else:
            return v
    else:
        return None

def buildQuery(terms):
    queryterms = []
    for te in terms:
        eq = te.find("=")
        if eq == -1:
            sys.stderr.write("Warning: invalid query term `{}'.\n".format(te))
            continue
        name = te[:eq]
        value = te[eq+1:].strip('"')
        field = getField(name)
        if field == None or field.type == -1:
            sys.stderr.write("Warning: invalid field `{}'.\n".format(name))
            continue
        if not field.srch:
            sys.stderr.write("Warning: cannot search field `{}'.\n".format(name))
            continue
        if field.type == 0:
            q = "{} LIKE '%{}%'".format(name, value)
            queryterms.append(q)
        elif field.type == 1:
            q = "{}={}".format(name, value)
            queryterms.append(q)

    return "WHERE " + " AND ".join(queryterms)
        
def runQuery(conn, queryterms):
    ids = []
    if len(queryterms) == 0:
        where = ""
    else:
        where = buildQuery(queryterms)
    query = "SELECT genbank FROM OralVantage {};".format(where)
    c = conn.cursor()
    for row in c.execute(query):
        ids.append(row[0])
    return ids

# def getRow(c, id):
#     c.execute("SELECT {} FROM OralVantage WHERE genbank=?".format(colNames()), (id,))
#     row = c.fetchone()
#     if row is None:
#         return None
#     result = []
#     p = 0
#     for F in FIELDS:
#         if F.type == -1:
#             continue
#         elif F.type == 0:
#             #print "{} = {} (normal)<br>".format(F.name, row[p])
#             result.append(str(row[p]))
#         elif F.type == 1:
#             #print "{} = {} (lookup)<br>".format(F.name, row[p])
#             result.append(getLookup(c, F.table, row[p]))
#         elif F.type == 2:
#             #print "{} = {} (special)<br>".format(F.name, row[p])
#             result.append(str(row[p]))
#         p += 1
#     return result

def getRow(c, id, colNames):
    c.execute("SELECT {} FROM OralVantage WHERE genbank=?".format(colNames), (id,))
    return c.fetchone()

def searchOralVantage(dbname, queryterms):
    colnames = colNames()
    result = []
    conn = sqlite3.connect(dbname)
    curs = conn.cursor()
    try:
        ids = runQuery(conn, queryterms)
        for id in ids:
            row = getRow(curs, id, colNames())
            result.append(row)
    finally:
        conn.close()
    return result

def getMenu(conn, table):
    """Returns the menu items for the entries in `table'."""
    for row in conn.execute("SELECT idx, v FROM {} ORDER BY idx;".format(table)):
        sys.stdout.write("<OPTION value='{}'>{}</OPTION>\n".format(row[0], row[1]))

### Main

def main(arguments):
    oformat = 'csv'
    outfile = None
    dbname = None
    queryterms = []
    next = ""

    for a in arguments:
        if next == '-f':
            oformat = a
            next = ""
        elif next == '-o':
            outfile = a
            next = ""
        elif a in ['-f', '-o']:
            next = a
        elif dbname == None:
            dbname = a
        else:
            queryterms.append(a)

    result = searchOralVantage(dbname, queryterms)
    
    if oformat == 'csv':
        if outfile:
            with open(outfile, "w") as out:
                writeResultsCsv(out, result)
        else:
            writeResultsCsv(sys.stdout, result)

def writeResultsCsv(stream, rows):
    stream.write("#" + colNames("\t") + "\n")
    for row in rows:
        srow = [ str(w) for w in row ]
        stream.write("\t".join(srow) + "\n")

if __name__ == "__main__":
    arguments = sys.argv[1:]
    main(arguments)
