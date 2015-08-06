# Frequency_Filtering.py
# A script that takes in a .par file, a .tim file, frequency range, and an output directory
# as a result, it creates a new file with frequencies in the frequency range, stored in output directory
# sample input:
# python Frequency_Filtering.py /Users/fkeri/Desktop/B1855+09_NANOGrav_9yv0.par /Users/fkeri/Desktop/B1855+09_NANOGrav_9yv0.tim 1300.0 1600.0 /Users/fkeri/Desktop/
# we can see that it takes in 5 line arguments: [INPUT .par], [INPUT .tim], [FREQ START], [FREQ END], [OUTPUT DIRECTORY]
# the output file will have the same name as the input file, with "FreqRange_" as a prefix: "FreqRange_B1855+09_NANOGrav_9yv0.tim"
# it is possible to name the output file differently by putting the file name in [OUTPUT DIRECTORY]: /Users/fkeri/Desktop/filename.tim

import sys
import os.path
import libstempo as T

def number( B ):
	try:
		float( B )
		return True
	except ValueError:
		return False

def remove_empty( A ):
	ret = []
	for i in range( len( A ) ):
		if A[i] != "":
			ret.append( A[i] )
	return ret

inFile = open( sys.argv[2], "r" ) # the .tim file
All_Lines = inFile.readlines()

psr = T.tempopulsar( parfile = sys.argv[1], timfile = sys.argv[2], maxobs = 100000 )

start = float( sys.argv[3] ) # start and end frequency
end = float( sys.argv[4] ) 

save_path = sys.argv[5]
if not save_path.endswith('.tim'):
    nameFile = os.path.join( save_path, "FreqRange_"+sys.argv[2].split("/")[-1] )
else:
    nameFile = save_path
outFile = open( nameFile, "w" ) # outfile that will contain the filtered frequencies
outFile.write('FORMAT 1\n')

cnt = 0
for i in range( len( All_Lines ) ):
	X = All_Lines[i].split(' ')
	X = remove_empty( X )
	for j in range( len( X ) ):
		if number( X[j] ):
			if float( X[j] ) == psr.freqs[cnt]:
				if ( psr.freqs[cnt] >= start ) and ( psr.freqs[cnt] <= end ):
					outFile.write( ' '.join( X ) )
				cnt += 1
				break

inFile.close()
outFile.close()
