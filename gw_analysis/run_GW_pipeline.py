from __future__ import division
import numpy as np
from PAL2 import PALmodels
from PAL2 import PALutils
from PAL2 import PALdatafile
from scipy.optimize import fmin
import matplotlib.pyplot as plt
import matplotlib.ticker
import scipy.special as ss
import json
import glob, os

import argparse


parser = argparse.ArgumentParser(description = 'Run PAL2 Frequentist GW pipeline')

parser.add_argument('--partim', dest='partim', action='store', type=str, default='./',
                   help='Full path to par/tim directory')
parser.add_argument('--outdir', dest='outdir', action='store', type=str, default='./',
                   help='Full path to output directory (default = ./)')
parser.add_argument('--pulsar', dest='pname', action='store', nargs='+', \
                    type=str, required=True, help='names of pulsars to use')
parser.add_argument('--pta', dest='pta', action='store', type=str, 
                    help='Which PTA set to use [nano9, nano5, pptadr1] (default=None)')
parser.add_argument('--noisedir', dest='noisedir', action='store', type=str, default=None,
                   help='Full path to noisefile directory (default = None)')
parser.add_argument('--pipeline', dest='pipeline', action='store', type=str, default='OS',
                   help='Which pipeline to run (default = OS) [Fstat, OS]')

# parse arguments
args = parser.parse_args()

fig_width_pt = 245.27 #513.17  # Get this from LaTeX using \showthe\columnwidth
inches_per_pt = 1.0/72.27               # Convert pt to inches
golden_mean = (np.sqrt(5)-1.0)/2.0         # Aesthetic ratio
fig_width = fig_width_pt*inches_per_pt  # width in inches
fig_height =fig_width*golden_mean       # height in inches
fig_size = [fig_width,fig_height]


params = {'backend': 'pdf',
        'axes.labelsize': 10,
        'lines.markersize': 4,
        'font.size': 10,
        'xtick.major.size':6,
        'xtick.minor.size':3,  
        'ytick.major.size':6,
        'ytick.minor.size':3, 
        'xtick.major.width':0.5,
        'ytick.major.width':0.5,
        'xtick.minor.width':0.5,
        'ytick.minor.width':0.5,
        'lines.markeredgewidth':1,
        'axes.linewidth':1.2,
        'legend.fontsize': 7,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'savefig.dpi':200,
        'path.simplify':True,
        'font.family': 'serif',
        'font.serif':'cm',
        'text.usetex':False,
        'axes.color_cycle': ['b', 'lime', 'r', 'purple', 'g', 'c', 'm',
                             'orange', 'darkblue', 'darkcyan', 'y',
                             'orangered','chartreuse','brown','deeppink',
                             'lightgreen', 'k'],
        'figure.figsize': fig_size}
plt.rcParams.update(params)

# find data
parFiles = glob.glob(args.partim + '/*.par')
timFiles = glob.glob(args.partim + '/*.tim')

# make HDF5 file
outdir = args.outdir
if not os.path.exists(args.outdir):
    try:
        os.makedirs(args.outdir)
    except OSError:
        pass
h5filename = outdir + '/h5file.hdf5'
df = PALdatafile.DataFile(h5filename)
for t,p in zip(timFiles[:], parFiles[:]):
    df.addTempoPulsar(p, t, iterations=3, sigma=10000)

if args.pname[0] != 'all':
    pulsar_names = args.pname
elif args.pname[0] == 'all':
    print 'Using all pulsars'
    pulsar_names = [str(name) for name in df.getPulsarList()]


# set noise model based on PTA
incEquad = False
incJitterEquad = False
incDM = False
print args.pta
if args.pta in ['nano9', 'nano5']:
    incEquad = True
    incJitterEquad = True
elif args.pta in ['pptadr1']:
    incEquad = True
    incDM = True

# only re-run noise estimation if required
if args.noisedir is None:

    # get ML noise parameters
    if not os.path.exists(args.outdir + '/noisefiles/'):
        try:
            os.makedirs(args.outdir + '/noisefiles')
        except OSError:
            pass
    for ct, psr in enumerate(pulsar_names):
         
        pulsars = [psr]
        model = PALmodels.PTAmodels(h5filename, pulsars=pulsars)
        
        fullmodel = model.makeModelDict(incRedNoise=True, noiseModel='powerlaw',
                        incDM=incDM, dmModel='powerlaw',
                        separateEfacs=False, separateEfacsByFreq=True,
                        separateEquads=False, separateEquadsByFreq=True,
                        separateJitter=False, separateJitterEquadByFreq=True,
                        incEquad=incEquad, incJitter=False, incJitterEquad=incJitterEquad,
                        incGWB=False, nfreqs=50, ndmfreqs=50,
                        compression='None', likfunc='mark9')
        
        model.initModel(fullmodel, memsave=True, fromFile=False,
                        verbose=False, write='no')
        
        pardes = model.getModelParameterList()
        par_names = [p['id'] for p in pardes if p['index'] != -1]
        par_out = []
        for pname in par_names:
            if psr in pname:
                par_out.append(''.join(pname.split('_'+psr)))
            else:
                par_out.append(pname)
                
        p0 = model.initParameters(fixpstart=True)

        print 'Search Parameters: {0}'.format(par_out)        
        
        # output parameter names
        if not os.path.exists(args.outdir + '/chains/{0}'.format(model.psr[0].name)):
            try:
                os.makedirs(args.outdir + '/chains/{0}'.format(model.psr[0].name))
            except OSError:
                pass
        fout = open(outdir + '/chains/{0}'.format(model.psr[0].name)+ '/pars.txt', 'w')
        for nn in par_out:
            fout.write('%s\n'%(nn))
        fout.close()
        
        def minfunc(pars):
            if model.mark3LogPrior(pars) != -np.inf:
                return -model.mark6LogLikelihood(pars)
            else:
                return 1e80
            
        p0 = model.initParameters(fixpstart=True)
            
        maxpars = fmin(minfunc, p0, ftol=1e-5, maxiter=10000, maxfun=1000, disp=False)
        
        pars = np.loadtxt(outdir + '/chains/{0}'.format(model.psr[0].name)+ \
                          '/pars.txt', dtype='S42')
        fout = open(outdir + '/noisefiles/{0}_noise.txt'.format(model.psr[0].name), 'w')
        for ii,pp in enumerate(pars):
            fout.write('{0} {1}\n'.format(pp, maxpars[ii]))
        fout.close()
        print psr, maxpars
    

# setup full model
if args.pname[0] != 'all':
    model = PALmodels.PTAmodels(h5filename, pulsars=args.pname)
elif args.pname[0] == 'all':
    print 'Using all pulsars'
    pulsars = 'all'
    model = PALmodels.PTAmodels(h5filename, pulsars=pulsars)

# likelihood function depends on pipeline
if args.pipeline == 'OS':
    if args.pta in ['nano5', 'nano9']:
        likfunc = 'mark2'
    else:
        likfunc = 'mark1'
elif args.pipeline == 'Fstat':
    likfunc = 'mark6'
    
fullmodel = model.makeModelDict(incRedNoise=True, noiseModel='powerlaw',
                    incDM=incDM, dmModel='powerlaw',
                    separateEfacs=False, separateEfacsByFreq=True,
                    separateEquads=False, separateEquadsByFreq=True,
                    separateJitter=False, separateJitterEquadByFreq=True,
                    incEquad=incEquad, incJitter=False, incJitterEquad=incJitterEquad,
                    incGWB=False, nfreqs=50, ndmfreqs=50,
                    compression='None', likfunc=likfunc)

if args.noisedir is None:
    noisedir = outdir + '/noisefiles/'
else:
    noisedir = args.noisedir + '/'

for ct, p in enumerate(model.psr):
    d = np.genfromtxt(noisedir + p.name + '_noise.txt', dtype='S42')
    pars = d[:,0]
    vals = np.array([float(d[ii,1]) for ii in range(d.shape[0])])
    sigs = [psig for psig in fullmodel['signals'] if psig['pulsarind'] == ct]
    sigs = PALutils.fixNoiseValues(sigs, vals, pars, bvary=True, verbose=False)
    
model.initModel(fullmodel, memsave=True, fromFile=False, verbose=False, write='no')

# set initial parameters
p0 = model.initParameters(fixpstart=True, startEfacAtOne=False)

if args.pta in ['nano5', 'nano9']:
    ostat = model.optimalStatisticCoarse
else:
    ostat = model.optimalStatistic

# run optimal statistic
if args.pipeline == 'OS':
    xi, rho, sig, Opt, Sig = ostat(p0)

    # average data
    avexi, averho, avesig = PALutils.binresults(xi, rho, sig, nbins=18)
    ORF = PALutils.computeORF(model.psr)

    f = plt.figure(figsize=(fig_width, fig_height*2))
    ymajorLocator2 = matplotlib.ticker.MaxNLocator(nbins=5, integer=False, prune='upper')

    ax1 = f.add_subplot(211)
    ax1.errorbar(avexi* 180/np.pi, averho/1e-30, avesig/1e-30, fmt='.')
    ind = np.argsort(xi)
    ax1.plot(xi[ind]*180/np.pi, Opt*ORF[ind]/1e-30, lw=1.5, color='r', ls='--')
    #ax1.set_ylim(-10, 10)
    ax1.minorticks_on()
    ax1.axhline(0, ls='--', color='k')
    plt.setp(ax1.get_xticklabels(), visible=False)
    ax1.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(
        nbins=6, integer=False, prune='both'))
    ax1.set_ylabel(r'$A_{\rm gw}^2\Gamma_{ab}(\zeta)$ [$10^{-30}$]')

    ax2 = f.add_subplot(212, sharex=ax1)
    ax2.hist(xi*180/np.pi, 18, weights=1/sig, normed=True, histtype='step', lw=1.5)

    ax2.minorticks_on()
    ax2.yaxis.set_major_locator(ymajorLocator2)
    ax2.set_xlabel('$\zeta$ [deg]')
    ax2.set_ylabel(r'Prob.')

    ax3 = ax2.twinx()
    ax3.hist(xi*180/np.pi, 18, normed=False, histtype='step', color='r', lw=1.5)
    ax3.set_ylim(ymax=140)
    ax3.minorticks_on()
    extra = ax3.set_ylabel(r'number of pulsar pairs')
    ax3.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(
        nbins=8, integer=False, prune='both'))

    #plt.tight_layout(pad=0.3, rect=[0, 0, 1.3, 1])
    f.subplots_adjust(hspace=0.0)


    #plt.errorbar(xi*180/np.pi, rho, sig, fmt='.')
    #plt.xlabel('Angular Separation [degrees]')
    #plt.ylabel('Correlation Coefficient')
    plt.savefig(outdir+'/hd.pdf', bbox_inches='tight')
    print 'A_gw = {0}'.format(np.sqrt(Opt))
    print 'A_95 = {0}'.format(np.sqrt(Opt + np.sqrt(2)*Sig*ss.erfcinv(2*(1-0.95))))
    print 'SNR = {0}'.format(Opt/Sig)
    x = {}
    x['A_gw'] = np.sqrt(Opt)
    x['A_95'] = np.sqrt(Opt + np.sqrt(2)*Sig*ss.erfcinv(2*(1-0.95)))
    x['SNR'] = Opt/Sig
    with open(outdir + '/os_out.json', 'w') as f:
        json.dump(x, f)

    
elif args.pipeline == 'Fstat':
    from scipy.interpolate import interp1d

    # call likelihood once to set noise
    model.mark6LogLikelihood(p0, incCorrelations=False, incJitter=incJitterEquad,
                             varyNoise=True, fixWhite=False)
    f = np.logspace(-9, -7, 1000)
    fpstat = np.zeros(len(f))
    for ii in range(1000):
        fpstat[ii] = model.fpStat(f[ii])

    ind = np.argmax(fpstat)

    # get lines of Fpstat for different FAPs
    faps = [1e-3, 1e-4, 1e-5]
    fstat = np.linspace(0.001, 1000, 10000)
    fap = np.array([PALutils.ptSum(len(model.psr), fp) for fp in fstat])
    func = func = interp1d(fap, fstat)

    print('ML frequency = {0} Hz'.format(f[ind]))
    print('FAP = {0}'.format(PALutils.ptSum(len(model.psr), fpstat[ind])))
    x = {}
    x['ML frequency'] = f[ind]
    x['FAP'] = PALutils.ptSum(len(model.psr), fpstat[ind])
    with open(outdir + '/fstat_out.json', 'w') as fl:
        json.dump(x, fl)
    
    plt.semilogx(f, fpstat)
    ls = ['-', '--', ':']
    for ct, fap in enumerate(faps):
        plt.axhline(func(fap), label=r'FAP = %3.3f percent'%(fap*100), 
                    color='k', ls=ls[ct])
    plt.xlabel(r'GW Frequency [Hz]')
    plt.ylabel(r'$2\mathcal{F}_p$')
    plt.legend(loc='best', frameon=False)
    plt.minorticks_on()
    plt.savefig(outdir+'/fpstat.pdf', bbox_inches='tight')
    plt.show()
    
