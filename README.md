## SD1 Project

This tool parses raw [USGS](https://water.usgs.gov/osw/) [AQUARIUS](http://aquaticinformatics.com/products/aquarius-time-series/) .csv files outputs a .csv file of a complete water year 
time series in 15 minute intervals.

Designed to be run from the command line, the program accepts **three additional arguments**:
	1. The water year that reflects the data - ex. **2017**
	2. The location of the raw AQUARIUS files - ex. **lickingriverdata/**
	3. The desired filename of the output file - ex **lickingriver.csv**

Also output from this tool are summary statistics printed to the command prompt and 
time series plots for each parameter file parsed.

Example plot for discharge:

![Licking River discharge measurments](https://github.com/neko1010/SD1_project/blob/master/figs_ex/discharge_cfs.png)

~

