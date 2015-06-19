# Residual_Plotting.py
# A script that takes in an Output_for_plotting_[PULSAR].tim file created by Average_Epochs.py, and an output directory
# as a result, it creates a plot of pulsar residuals, stored in the output directory
# sample input:
# python Residual_Plotting.py /Users/fkeri/Desktop/Output_for_plotting_B1855+09_NANOGrav_9yv0.tim /Users/fkeri/Desktop/
# we can see that it takes in 2 line arguments: [INPUT FILE], [OUTPUT DIRECTORY]
# the output file will have the name of the pulsar: "1713+0747.png"

import matplotlib.pyplot as plt
import sys

#Opens the residual file
fawes=open(sys.argv[1], "r")

psrname = fawes.readline()
lines_after_7=fawes.readlines()[7: ] #Skip the text lines 

#Create a list from data
L=[]
#print lines_after_7[0:2]
for i in range(0, len(lines_after_7)):
	L.append(str(lines_after_7[i]).split('\t'))
	#print float(L[i][0])
#print L[0]
#print float(L[0][0])

#Creates x and y lists
X=[[] for i in range(5)]
er=[[] for i in range(5)]
Y=[[] for i in range (5)]
clrs=['green', 'red', 'blue', 'orange', 'yellow']
freq=[[100, 360], [361, 601], [601, 999], [1000, 2100], [2101, 3000]]
band_p=[]
bandf=['100-360 MHz','361-601 MHz','601-999 MHz', '1000-2100 MHz', '2101-3000 MHz']
bandf_p=[]

#Get X, Y and Er lista for each frequency band
for j in range(5):
	for i in range(0, len(lines_after_7)):
	#print L[i][0]
		if float(L[i][2])>=freq[j][0] and float(L[i][2])<=freq[j][1]:
			X[j].append(float(L[i][0]))
			Y[j].append(float(L[i][1])*10**6)
			er[j].append(float(L[i][3]))
fawes.close()

#Ploting of the residuals for the 5 bandwidths

for i in range (5):
	if X[i]:
		band_i,=plt.plot(X[i], Y[i], marker='o', color=clrs[i], linestyle='none')
		plt.errorbar(X[i], Y[i], yerr=er[i], ls='none', color=clrs[i])
		band_p.append(band_i)
		bandf_p.append(bandf[i])

save_path = sys.argv[2]
plt.title( "Pulsar "+psrname[:len(psrname)-1] )
plt.legend(band_p, bandf_p)
plt.axhline(0, color='blue', linestyle='--')
plt.xlabel("TOAs(MJD)", fontsize=14, color="black")
plt.ylabel("Residuals ($\mu$s)", fontsize=14, color="black")
plt.savefig( save_path+psrname[:len(psrname)-1]+".png" )
#plt.clf()
