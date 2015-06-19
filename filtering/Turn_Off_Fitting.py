import sys
import os.path

inputFileName = sys.argv[1]
save_path = sys.argv[2]
outputFileName = os.path.join( save_path, "output.par" )



with open(inputFileName,'r') as readFile:
    with open(outputFileName,'w') as writeFile:
        for line in readFile:
            if("mode" in line.lower() or "nits" in line.lower()):
                writeFile.write(line)
            else:
                temp = line.replace(" 1 "," 0 ")
                temp = temp.replace(" 1\n"," 0\n")
                writeFile.write(temp)

