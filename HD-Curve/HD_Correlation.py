# Filip Keri
# HD_Correlation.py
# A script that takes in a directory that contains all .par and .tim, and an output directory
# as a result, it creates a Hellings and Downs curve (.png file); it also creates a bunch of .tim and .par files (come from Average_Epochs.py)
# sample input:
# python HD_Correlation.py /home/ipta/Dropbox/NANOGrav_9y/ALL_DATA/ /home/ipta/results
# we can see that it takes in 2 (or 3) line arguments: [INPUT DIRECTORY], [OUTPUT DIRECTORY], [FILENAME]*
# [FILENAME] is an optional argument - if we leave it out, the output file will be named "CorrelationDATA.png"
# ** the script might take a couple of minutes to run (especially if running for the first time)

import sys
import math
import libstempo as T
import numpy as N
import matplotlib.pyplot as P
import resource
import gc
import copy
import os
import time

def Ecl2Cel( lambdaa, betaa, TT ): # transform ecliptic to celestial coordinates
	t = ( TT-51544.5 )/3652500
	E = 84381.448-4680.93*t-1.55*(t**2)+1999.25*(t**3)-51.38*(t**4)-249.67*(t**5)-39.05*(t**6)+7.12*(t**7)+27.87*(t**8)+5.79*(t**9)+2.45*(t**10)
	E /= 3600
	deltaa = math.asin( math.sin( betaa )*math.cos( E )+math.cos( betaa )*math.sin( E )*math.sin( lambdaa ) )
	alfaa = math.acos( math.cos( lambdaa )*math.cos( betaa )/math.cos( deltaa ) )
	return (alfaa, deltaa)

def angsep( CEL1, CEL2 ):
	ra1rad, dec1rad = CEL1
	ra2rad, dec2rad = CEL2

	x = math.cos( ra1rad )*math.cos( dec1rad )*math.cos( ra2rad )*math.cos( dec2rad )
	y = math.sin( ra1rad )*math.cos( dec1rad )*math.sin( ra2rad )*math.cos( dec2rad )
	z = math.sin( dec1rad )*math.sin( dec2rad )

	rad = math.acos( x+y+z ) # Sometimes gives warnings when coords match

	# use Pythargoras approximation if rad < 1 arcsec
	if rad < 0.000004848:
		sep = math.sqrt( ( math.cos( dec1rad )*( ra1rad-ra2rad ) )**2+( dec1rad-dec2rad )**2 )
	else:
		sep = rad
	
	# Angular separation
	sep = sep*180/math.pi

	return sep

def ABS( NUM ):
	if NUM > 0:
		return NUM
	return -NUM

def mean( nums ):
	M = 0
	for i in range( len( nums ) ):
		M += nums[i]
	if len(nums) == 0:
		return 0
	M /= len( nums )
	return M

def stand_deviation( nums, M ):
	S = 0
	for i in range( len( nums ) ):
		S += ( nums[i]-M )**2
	if len( nums ) < 2:
		return 0
	S /= len( nums )-1
	return math.sqrt( S )

def find_C( psr1, psr2 ): # a function that calculates correlation between two pulsars
	TOA1 = [ w[0] for w in psr1 ]
	TOA2 = [ w[0] for w in psr2 ]
	Residuals1 = [ w[1] for w in psr1 ]
	Residuals2 = [ w[1] for w in psr2 ]

	R1 = [] # residuals for correlation
	R2 = []

	used = {}
	for i in range( len( TOA1 ) ):
		mini = 100000
		idx = 0
		for j in range( len( TOA2 ) ):
			diff = ABS( TOA1[i]-TOA2[j] )
			if( diff < 7 and diff < mini ):
				mini = diff
				idx = j
		if( mini < 7 ):
			if( idx not in used.keys() ):
				used[idx] = (mini, i)
			else:
				if( used[idx][0] > mini ):
					used[idx] = (mini, i)
	for i in range( len( used.keys() ) ):
		idx = used.keys()[i]
		R2.append( Residuals2[idx] )
		R1.append( Residuals1[ used[idx][1] ] ) 


	# testfile.close()

	# if len( R1 ) < 10: # if there is not enough residuals to calculate the correlation
	# 	return -500

	mR1 = mean( R1 )
	mR2 = mean( R2 )
	sR1 = stand_deviation( R1, mR1 )
	sR2 = stand_deviation( R2, mR2 )

	if len( R1 ) < 10: # if there is not enough residuals to calculate the correlation
		return -500

	ret = 0.0
	for i in range( len( R1 ) ):
		ret += ( R1[i]-mR1 )/sR1*( R2[i]-mR2 )/sR2
	ret /= len( R1 )-1

	return ret

def main():
	save_path = sys.argv[2]

	try:
		completeName = os.path.join( save_path, sys.argv[3] )
	except IndexError:
		completeName = os.path.join( save_path, "CorrelationDATA.txt" )

	outFile = open( completeName, 'w' )

	pList = []
	FILES = os.listdir( sys.argv[1] )
	FILESpar = [ x for x in FILES if x.endswith(".par") ]
	FILEStim = [ x for x in FILES if x.endswith(".tim") ]

	for par in FILESpar:
		for tim in FILEStim:
			if par.split('.')[0] == tim.split('.')[0]:
				pList.append( ( par, tim ) )

	T.data = sys.argv[1]

	DATA = [] # DATA[i] contains two lists - first one has all TOAs, second one has all residuals
	COOR = [] # COOR[i] contains celestial coordinates (tuple) of pulsar i
	for i in range( len( pList ) ):
		PSR = T.tempopulsar( parfile = T.data+pList[i][0], timfile = T.data+pList[i][1], maxobs = 100000 )

		try: # different data sets use different coordinate systems
			PSR['RAJ'].val
			COOR.append( (PSR['RAJ'].val, PSR['DECJ'].val) )
		except KeyError:
			COOR.append( copy.copy( Ecl2Cel( PSR['ELONG'].val, PSR['ELAT'].val, PSR['POSEPOCH'].val ) ) )

		ok = False
		FILES = os.listdir( save_path )
		for X in FILES:
			if X[:len( X )-23] == PSR.name:
				currFile = open( os.path.join( save_path, X ), "r" )
				ok = True
		if( not ok ):
			os.system( "python Average_Epochs.py "+T.data+pList[i][0]+" "+T.data+pList[i][1]+" "+save_path )
			currFile = open( os.path.join( save_path, PSR.name+"Output_for_plotting.tim" ), "r" )

		toas = []
		resid = []
		lines = currFile.readlines()[7:]
		for line in lines:
			toas.append( float( line.split('\t')[0] ) )
			resid.append( float( line.split('\t')[1] ) )
		currFile.close()

		DATA.append( [ copy.copy( toas ), copy.copy( resid ) ] ) # send a copy because DATA[i] points to objects
		del PSR
		gc.collect() # free up some memory

		DATA[i] = [ [ DATA[i][0][x], DATA[i][1][x] ] for x in range( len( DATA[i][0] ) ) ]
		DATA[i].sort( key = lambda row: row[0] ) # sort by TOAs

	nPSR = len( pList ) # number of all pulsars

	for i in range( nPSR-1 ):
		for j in range( i+1, nPSR ):
			C = find_C( DATA[i], DATA[j] ) # find correlation between pulsar i and pulsar j
			ANG_SEP = angsep( COOR[i], COOR[j] ) # find angular separation between pulsar i and pulsar j
			if C != -500: # C becomes -500 when there is not enough residuals to calculate the correlation
				outFile.write( str( ANG_SEP )+" "+str( C )+"\n" )

	outFile.close()

	try:
		where = sys.argv[3]
		if where[-4] != '.':
			where += ".txt"
		os.system( "python HD_Plot.py "+sys.argv[1]+" "+sys.argv[2]+" "+where )
	except IndexError:
		os.system( "python HD_Plot.py "+sys.argv[1]+" "+sys.argv[2]+" "+"CorrelationDATA.txt" )

main()
