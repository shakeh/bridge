# Filip Keri
# Average_Epochs.py
# A script that takes in a .par file, a .tim file, and an output directory
# as a result, it creates a new file with TOAs compressed in epochs, stored in output directory
# sample input:
# python Average_Epochs.py /Users/fkeri/Desktop/B1855+09_NANOGrav_9yv0.par /Users/fkeri/Desktop/B1855+09_NANOGrav_9yv0.tim /Users/fkeri/Desktop/
# we can see that it takes in 3 line arguments: [INPUT .par FILE], [INPUT .tim FILE], [OUTPUT DIRECTORY]
# the output file will have the same name as the input file, with "Output_for_plotting_" as a prefix: "Output_for_plotting_B1855+09_NANOGrav_9yv0.tim"
# it is possible to name the output file differently by putting the file name in [OUTPUT DIRECTORY]: /Users/fkeri/Desktop/filename.tim

import sys
import math
import numpy as N
import matplotlib.pyplot as P
import libstempo as T
import os.path

def freq_idx( F ):
	freq=[ [100, 360], [361, 600], [601, 999], [1000, 2100], [2101, 3000] ]
	for i in range( 5 ):
		if ( F >= freq[ i ][ 0 ] ) and ( F <= freq[ i ][ 1 ] ):
			return i
	return 0
	
F = [ 350, 450, 800, 1400, 2300 ]

output_dir = str(sys.argv[ 3 ])
psr = T.tempopulsar( parfile = str( sys.argv[ 1 ] ), timfile = str( sys.argv[ 2 ] ) )
sort_cmp = N.argsort( psr.stoas )
bin = [] # format: residuals, error, TOA, frequency

# sorting residuals, errors, frequencies, and TOAs by TOAs
Residuals = psr.residuals()[ sort_cmp ]
Errors = psr.toaerrs[ sort_cmp ]
TOA = psr.stoas[ sort_cmp ]
FREQ = psr.freqs[ sort_cmp ]

curr = [ Residuals[ 0 ], Errors[ 0 ], TOA[ 0 ], FREQ[ 0 ] ]
for i in range( 1, len( TOA ) ):
	if( TOA[ i ]-TOA[ i-1 ] > (3.0/144.0) ):
		bin.append( curr )
		curr = []
	curr.append( Residuals[ i ] )
	curr.append( Errors[ i ] )
	curr.append( TOA[ i ] )
	curr.append( FREQ[ i ] )
if len( curr ) > 0:
	bin.append( curr )

avgResidual = []
avgError = []
avgTOA = []
avgFREQ = []

for i in range( len( bin ) ):
	sum1 = [ 0.0, 0.0, 0.0, 0.0, 0.0 ]
	sum2 = [ 0.0, 0.0, 0.0, 0.0, 0.0 ]
	sum3 = [ 0.0, 0.0, 0.0, 0.0, 0.0 ]
	sumTOA = [ 0, 0, 0, 0, 0 ]
	for j in range( 0, len( bin[ i ] ), 4 ):
		currRes = bin[ i ][ j ]
		currErr = bin[ i ][ j+1 ]
		currTOA = bin[ i ][ j+2 ]
		idx = freq_idx( bin[ i ][ j+3 ] )
		sum1[ idx ] += currRes/( currErr**2 )
		sum2[ idx ] += 1/( currErr**2 )
		sum3[ idx ] += currTOA
		sumTOA[ idx ] += 1
	for j in range( 5 ):
		if sumTOA[ j ] > 0:
			avgResidual.append( sum1[ j ]/sum2[ j ] )
			avgError.append( math.sqrt( 1/sum2[ j ] ) )
			avgTOA.append( sum3[ j ]/sumTOA[ j ] )
			avgFREQ.append( F[ j ] )

pulsar_path = str( sys.argv[ 1 ] )
pulsar_file = pulsar_path.split('/')
pulsar_name = pulsar_file[-1].split('.')

if sys.argv[3][-4] != '.':
    outFile = open( os.path.join( str(sys.argv[ 3 ]), "Output_for_plotting_"+pulsar_name[0]+".tim" ), "w" )
else:
    outFile = open( sys.argv[3], "w" )

outFile.write( psr.name+"\n" )
outFile.write( "This program comes with ABSOLUTELY NO WARRANTY.\nThis is free software, and you are welcome to redistribute it\n" )
outFile.write( "under conditions of GPL license.\n\n\n\n" )

for i in range( len( avgTOA ) ):
	outFile.write( str("{0:.15f}".format(avgTOA[ i ]))+"\t"+str("{0:.19f}".format(avgResidual[ i ]))+"\t"+str(avgFREQ[ i ])+"\t"+str("{0:.19f}".format(avgError[ i ]))+"\n" )

outFile.close()
