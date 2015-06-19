# Turn_Off_Fitting.py
# A script that takes in a .par file, and an output directory
# as a result, it creates a new .par file with fit option turned OFF
# sample input:
# python Turn_Off_Fitting.py /Users/fkeri/Desktop/B1855+09_NANOGrav_9yv0.par /Users/fkeri/Desktop/
# we can see that it takes in 2 line arguments: [INPUT FILE], [OUTPUT DIRECTORY]
# the output file will have the same name as the input file, with "NoFit_" as a prefix: "NoFit_B1855+09_NANOGrav_9yv0.par"
# it is possible to name the output file differently by putting the file name in [OUTPUT DIRECTORY]: /Users/fkeri/Desktop/filename.par

import sys
import os.path

inputFileName = sys.argv[1]
save_path = sys.argv[2]
if save_path[-4] != '.':
    outputFileName = os.path.join( save_path, "NoFit_"+sys.argv[1].split("/")[-1] )
else:
    outputFileName = save_path

with open(inputFileName,'r') as readFile:
    with open(outputFileName,'w') as writeFile:
        for line in readFile:
            if("mode" in line.lower() or "nits" in line.lower()):
                writeFile.write(line)
            else:
                temp = line.replace(" 1 "," 0 ")
                temp = temp.replace(" 1\n"," 0\n")
                writeFile.write(temp)

