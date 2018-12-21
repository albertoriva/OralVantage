#!/bin/bash

CMD=$(basename $0)
DB=OralVantage.db

echo Content-type: text/html
echo

if [ "$CMD" == "ovquery.cgi" ];
then
  ./ovqueries.py $DB intro
elif [ "$CMD" == "ovresults.cgi" ];
then
  ./ovqueries.py $DB results
fi
