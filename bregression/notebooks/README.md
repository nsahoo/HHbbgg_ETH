Prepare b-jet regerssion training, check perfomance, fit the distibutions, make plots

All notebooks were written only as a starting point, once a notebook is written to some working level , I convert them to python scripts for speed reasons. All code here makes use of functions written in ../python directory 

### Training Regression
```
ipython trainBreg_jobs.py
ipython trainBreg_quatile.py alpha
where alpha equals to the qunatile you want to train to
```
This will save the weight '.pkl' file in the ../output_files/ directory
### Applying Regression

For quantile regerssion then we need to add 3 BDT outputs (3 quantiles 0.2,0.4,0.7) to the tree
```
ipython applyRegQuantile.py
```
Other 3 scripts are availbale with different python or ROOT minimization and fiing packages:
```
applyRegQuantile_advanced.py  applyRegQuantile_curve.py  applyRegQuantile.py  applyRegQuantile_root.py
```
### Evaluating and comparing performance of the regression

Once this is done we can make compare the performance of different regressions :
```
ipython compare.py sample_name
where samplename = ttbar or ZHbbll or for DiHiggs sm, res500 and res700
```
For all of the 3 samples one need to change the root file name unfotnately at this moment
This compare script will fit Bukin funciton to the Jet_mcPt/Jet_regerssed_pt in all given pt and eta regions

Then to compare the Bukin sigma and peak value Xp:
```
ipython chooseTheBest.py sample_name
where sample_name= ttbar or ZHbbll or for DiHiggs sm, res500 and res700
```
To create Bukin fits in the bins of resolution obtained with Quantile regression
```
ipython resolution.py sample_name
```
Then to compare the Bukin sigma and peak value Xp:
ipython sigma_resolution.py ttbar

To create inclusive plots to compare all samples at the same time :
```
sigma_resolution_all.py
chooseTheBest_all.py  -  need to recomment things , because this script can make 2 plots : inclusive sigma for all samples and different regressions and also al sample pT regions for only 1 regression
```

### Study that was done with quantiles
```
ipython plotQuantiles.py
```

### Plotting
## Plot inputs features
```
plotFeatures.py
```
## Plot regerssion profile
```
RegressionProfile.py
```
## Helping scripts that were used only as intermediary 
```
CaterinaComparison.py
compareScale.py
```
