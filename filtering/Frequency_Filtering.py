import sys
import os.path

inFile = open( sys.argv[1], "r" )

inFile.readline() #omit first line
ALLlines = inFile.readlines()

start = float( sys.argv[2] )
end = float( sys.argv[3] ) 

save_path = sys.argv[4]
nameFile = os.path.join( save_path, "FreqRange"+sys.argv[1].split("/")[-1] )
outFile = open( nameFile, "w" )

L = []
for i in range( 0, len( ALLlines ) ):
    L.append( ALLlines[i].split(' ') )
#L.sort(key = lamda row: row[2] )

for i in range( 0, len( ALLlines )):
    Frequency = float( L[i][1] )
    if(Frequency >= start and Frequency <= end ):
         X = ' '.join( L[i] )
         outFile.write( X )

inFile.close()
outFile.close()
