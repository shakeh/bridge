# A script that takes in a .tim file, frequency range, and an output directory
# as a result, it creates a new file with frequencies in the frequency range, stored in output directory
# sample input:
# python Frequency_Filtering.py /Users/fkeri/Desktop/B1855+09_NANOGrav_9yv0.tim 51000 55000 /Users/fkeri/Desktop/
# we can see that it takes in 4 line arguments: [INPUT FILE], [FREQ START], [FREQ END], [OUTPUT DIRECTORY]
# the output file will have the same name as the input file, with "FreqRange_" as a prefix: "FreqRange_B1855+09_NANOGrav_9yv0.tim"
# it is possible to name the output file differently by putting the file name in [OUTPUT DIRECTORY]: /Users/fkeri/Desktop/filename.tim

import sys
import os.path

inFile = open( sys.argv[1], "r" )

inFile.readline() #omit first line
ALLlines = inFile.readlines()

start = float( sys.argv[2] )
end = float( sys.argv[3] ) 

save_path = sys.argv[4]
if save_path[-4] != '.':
    nameFile = os.path.join( save_path, "FreqRange_"+sys.argv[1].split("/")[-1] )
else:
    nameFile = save_path
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
