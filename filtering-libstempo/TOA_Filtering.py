# TOA_Filtering.py
# A script that takes in a .par file, .tim file, start time and end time, and an output directory
# as a result, it creates a new file with TOAs in the time range, stored in output directory
# sample input:
# python TOA_Filtering.py /Users/fkeri/Desktop/B1855+09_NANOGrav_9yv0.par /Users/fkeri/Desktop/B1855+09_NANOGrav_9yv0.tim 51000 56000 /Users/fkeri/Desktop/
# we can see that it takes in 5 line arguments: [INPUT .par], [INPUT .tim], [TIME START], [TIME END], [OUTPUT DIRECTORY]
# [TIME START] and [TIME END] formats: MJD or YYYY/MM/DD
# the output file will have the same name as the input file, with "TOArange_" as a prefix: "TOArange_B1855+09_NANOGrav_9yv0.tim"
# it is possible to name the output file differently by putting the file name in [OUTPUT DIRECTORY]: /Users/fkeri/Desktop/filename.tim

import sys
import math
import datetime
import libstempo as T
#import jdcal
import glob
import os.path

def remove_empty( A ):
	ret = []
	for i in range( len( A ) ):
		if A[i] != "":
			ret.append( A[i] )
	return ret

def date2mjd(year, month, day):
    """
    function that converts date in YYYY/MM/DD to MJD
    """
    jd = sum(jdcal.gcal2jd(year, month, day))
    mjd = jd -2400000.5
    return mjd

def isFloat( X ):
	try:
		float( X )
		return True
	except ValueError:
		return False

def transform( X ):
	X = str( X )
	A = [ "", "", "", "", "" ]
	ch = 0
	cnt = 0
	for i in range( len( X ) ):
		ch = X[i]
		if not ( ord( ch ) > 44 and ord( ch ) < 58 ):
			return "not ok"
		if ch == "-" or ch == "/":
			cnt += 1
		else:
			A[ cnt ] += ch
	if cnt == 2:
		if int( A[1] ) > 12 or int( A[2] ) > 31:
			return "not ok"
		return date2mjd( int( A[0] ), int( A[1] ), int( A[2] ) )
	return float( X )

inFile = open( sys.argv[2], "r" )

save_path = sys.argv[5]
if save_path[-4] != '.':
    nameFile = os.path.join( save_path, "TOArange_"+sys.argv[2].split("/")[-1] )
else:
    nameFile = save_path
outFile = open( nameFile, "w" )

inFile.readline() #omit first line
ALLlines = inFile.readlines()

start = str( sys.argv[3] )
end = str( sys.argv[4] )
start = transform( start )
end = transform( end )

psr = T.tempopulsar( parfile = sys.argv[1], timfile = sys.argv[2], maxobs = 100000 )
cnt = 0

if ( start == "not ok" ) or ( end == "not ok" ):
	outFile.write( "Wrong format! Please enter the data again! (either MJD or YYYY/MM/DD format)" )
else:
	if ( start < 0 ) or ( end < 0 ):
		outFile.write( "Your starting and ending points cannot be less than zero! Please enter the data again! (either MJD or YYYY/MM/DD format)" )
	else:
		if ( start > end ):
			outFile.write( "Your starting point cannot be greater than your ending point! Please enter the data again! (either MJD or YYYY/MM/DD format)" )
		else:
			for i in range( len( ALLlines ) ):
				X = ALLlines[i].split(' ')
				X = remove_empty( X )
				for j in range( len( X ) ):
					if isFloat( X[j] ):
						if float( X[j] ) == psr.freqs[cnt]:
							if ( psr.stoas[cnt] >= start ) and ( psr.stoas[cnt] <= end ):
								outFile.write( ' '.join( X ) )
							cnt += 1
							break

inFile.close()
outFile.close()
