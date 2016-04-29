#############################
##   Hunt Group Reporter   ##
##      Python 2.7         ##
##   By Redemption.Man     ##
#############################

import csv
import argparse
import os.path
import time
import sys

## CLI switches
parser = argparse.ArgumentParser(prog='Hunt_Group_Reporter.py', description='Reports on a hunt group for the length of Cisco cdr file')
parser.add_argument('--input', required=True, help='CDR file input(must be csv)')
parser.add_argument('--huntgroup', required=True, help='extension of the hunt group')

args = parser.parse_args()

## END of CLI switches

## Var's that can be changed
parsedoutputfile = "Parsed_CDR_"+args.huntgroup+".csv"
outputfile = "HuntGroup_Report_"+args.huntgroup+".csv"

## arg.input is the input file
huntgroup = args.huntgroup

#create parsed output cvs 
parsedoutput = open(parsedoutputfile, 'w+')
parsedoutput.write("dateTimeOrigination,dateTimeConnect,dateTimeDisconnect,Duration,finalCalledPartyUnicodeLoginUserID\n")

## columns needed:
## starting at zero
## 2 - globalCallID_callId
## 4 - dateTimeOrigination
## 47 - dateTimeConnect
## 48 - dateTimeDisconnect
## 55 - Duration
## 31 - finalCalledPartyUnicodeLoginUserID
## 101 - huntPilotDN
#### Opens and parses cdr extracting only records with the gateway
maxduration = 0
firstrecord = 999999999999999
lastrecord = 0
totalagents = 0
totalduration = 0
totalcalls = 0
with open(args.input, 'Ur') as f:
	print "Collecting all records for " + huntgroup + "\n\n"
	parserreader = csv.reader(f)
	for row in parserreader:
		if row[101] == huntgroup:
			totalduration = totalduration + int(row[55])
			totalcalls = totalcalls + 1
			## finding longest call
			if maxduration <= int(row[55]):
				maxduration = int(row[55])
			## finding first call
			if int(row[4]) <= firstrecord:
				firstrecord = int(row[4])
			## finding last call
			if int(row[48]) >= lastrecord:
				lastrecord = int(row[48])
			
			## extracting call records
			parsedoutput.write(row[4]+","+row[47]+","+row[48]+","+row[55]+","+row[31]+"\n")
parsedoutput.close()
f.close() 
if totalcalls == 0:
	sys.exit("***ERROR*** No calls found for Hunt Group "+huntgroup)
else:
	averageduration = totalduration / totalcalls
print "Average Call Duration is " + str(averageduration) + " Seconds"
convertstarttime = time.localtime(float(firstrecord))
convertendtime = time.localtime(float(lastrecord))



starttimeoutput = str(convertstarttime.tm_year)+"/"+str(convertstarttime.tm_mon)+"/"+str(convertstarttime.tm_mday)+" "+str(convertstarttime.tm_hour) + ":00"
endtimeoutput = str(convertendtime.tm_year)+"/"+str(convertendtime.tm_mon)+"/"+str(convertendtime.tm_mday)+" "+str((convertendtime.tm_hour+1)) + ":00"

print starttimeoutput
print endtimeoutput
## START OF REPORTING
input = parsedoutputfile
agents = []
currenttime = firstrecord
## generating report
firstagent = 1
## find agents
with open(input, 'Ur') as g:
	reader = csv.reader(g)
	reader.next()
	for row in reader:
		## duration check to stop looping if passed call records to do with current time
		if firstagent == 1:
			agents.append(row[4])
			firstagent = 0
		else:
			if agents.count(row[4]) == 0:
				agents.append(row[4])
g.close()
totalagents = len(agents) - 1
agentsduration = []
agenttotalcalls = []
currentagent = 0
## finding agent stats
with open(input, 'Ur') as g:
	reader = csv.reader(g)
	while currentagent <= totalagents:
		##
		agentsduration.append(0)
		agenttotalcalls.append(0)
		## makes sure your at the start of the file
		g.seek(0)
		## skips 1 row that has headings
		reader.next()		
		for row in reader:
			## duration check to stop looping if passed call records to do with current time
			if agents[currentagent] == row[4]:
				agenttotalcalls[currentagent] = agenttotalcalls[currentagent] + 1
				agentsduration[currentagent] = agentsduration[currentagent] + int(row[3])
		currentagent = currentagent + 1
g.close()
		
## create output csv file
output = open(outputfile, 'w+')
output.write("Report on Hunt Group : "+huntgroup+"\n")
output.write("Report Duration : "+starttimeoutput+" - "+endtimeoutput+"\n")
output.write("\n")
output.write("Agent,Calls Taken,Average Duration\n")
currentagent = 0
while currentagent <= totalagents:
	currentagentaverage = agentsduration[currentagent]/agenttotalcalls[currentagent]
	output.write(agents[currentagent]+","+str(agenttotalcalls[currentagent])+","+str(currentagentaverage)+"\n")
	currentagent = currentagent + 1
## Last part of Report
output.write("\n")
output.write("Total Calls,"+str(totalcalls)+"\n")
output.write("Average DurationCalls Taken(Seconds),,"+str(averageduration)+"\n")