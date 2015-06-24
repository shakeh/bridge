import math
import numpy as N
import matplotlib.pyplot as P
from scipy.optimize import curve_fit
import sys
import os

def analytical_C( angle, p1, p2 ):
	angle = N.radians( angle )
	return p1*3.0/2.0*( (1-N.cos( angle ))/2.0*N.log( (1-N.cos( angle ))/2.0 )-(1-N.cos( angle ))/12.0+1/3 )+0.5+p2

L = []
D = {}
for i in range( 5, 185, 5 ):
	L.append( i )
	D[ i ] = []

inFile = open( os.path.join( sys.argv[2], sys.argv[3] ), "r" )
lines = inFile.readlines()
inFile.close()

for i in range( len( lines ) ):
	X = lines[i].split(' ')
	ANG_SEP = X[0][: len( X[0] )-1 ]
	C = X[1][: len( X[1] )-1 ]

	if C != 0:
		for j in range( len( L ) ):
			if float( ANG_SEP ) < L[j]:
				D[ L[j] ].append( ( float(ANG_SEP), float(C) ) )
				break

xdata = []
ydata = []
for i in range( len( L ) ):
	if len( D[ L[i] ] ) > 0:
		CORR = 0
		ANG = 0
		for j in range( len( D[ L[i] ] ) ):
			CORR += D[ L[i] ][j][1]
			ANG += D[ L[i] ][j][0]
		CORR /= len( D[ L[i] ] )
		ANG /= len( D[ L[i] ] )

		sd_CORR = 0
		for j in range( len( D[ L[i] ] ) ):
			sd_CORR += ( D[ L[i] ][j][1]-CORR )**2
		sd_CORR /= len( D[ L[i] ] )
		sd_CORR = math.sqrt( sd_CORR )

		sd_ANG = 0
		for j in range( len( D[ L[i] ] ) ):
			sd_ANG += ( D[ L[i] ][j][0]-ANG )**2
		sd_ANG /= len( D[ L[i] ] )
		sd_ANG = math.sqrt( sd_ANG )

		P.scatter( ANG, CORR, s = 15 )
		P.errorbar( ANG, CORR, xerr = sd_ANG, yerr = sd_CORR, fmt = '', color = 'b' )
		xdata.append( ANG )
		ydata.append( CORR )

xdata = N.array( xdata )
ydata = N.array( ydata )

A, B = curve_fit( analytical_C, xdata, ydata )
P.plot( N.linspace( 0.001, 180, 1000, endpoint = True ), analytical_C( N.linspace( 0.001, 180, 1000, endpoint = True ), A[0], A[1] ) )

save_path = sys.argv[2]
P.title( "HD curve for "+sys.argv[3] )
P.xlabel("Angular separation between two pulsars (degrees)", fontsize=14, color="black")
P.ylabel("Correlation between two pulsars", fontsize=14, color="black")
P.savefig( os.path.join( save_path, sys.argv[3][:len( sys.argv[3] )-4] )+".png" )
