from datetime import datetime, timedelta
import numpy as np
import csv
import glob
import os
import sys
import matplotlib.pyplot as plt     

def datetime_range(start, end, delta):
    """
    Creates full time series of interest.
    """
    
    current = start
    while current < end:
        yield current
        current += delta

def full_dt_range(wtr_yr):
    """
    Uses datetime_range to return a full datetime range list object with 15 minute
    increments for a specific water year (10/1 to 9/30) determined by the only required argument
    """
    dt_range = []
    
    ## Water year (10/1 - 9/30) full range- 15 minute increments
    dts = datetime_range(datetime(wtr_yr -1, 10,1, 0, 0, 0),
        datetime(wtr_yr, 10, 1, 0, 0, 0),
        timedelta(minutes = 15))
    for dt in dts:
        dt_range.append(dt)
   
    return dt_range     


def empty_data(dt_range):

    """
    Accepts only a datetime range list argument returned in full_dt_range and returns
    a dictionary with a key for each column needed in the SD1 file. Each key value is 
    an np.array created with a length the same as the full datetime range
    """
    dt_range = np.asarray(dt_range)
    
    ## Numpy NaN arrays for each param equal in length to the datetime range
    gageheight_ft = np.full_like(dt_range, np.nan, dtype = np.double)
    discharge_cfs= np.full_like(dt_range, np.nan, dtype = np.double)
    precip_in = np.full_like(dt_range, np.nan, dtype = np.double)
    temp_c = np.full_like(dt_range, np.nan, dtype = np.double)
    do_mgL = np.full_like(dt_range, np.nan, dtype = np.double)
    pH_su = np.full_like(dt_range, np.nan, dtype = np.double)
    conduct_umhos = np.full_like(dt_range, np.nan, dtype = np.double)
    turb_ntu = np.full_like(dt_range, np.nan, dtype = np.double)
    velocity = np.full_like(dt_range, np.nan, dtype = np.double)
    nitrate = np.full_like(dt_range, np.nan, dtype = np.double)

    ## Dictionary for datetime range and empty param arrays
    empties = { "dt_range" : dt_range, "gageheight_ft" : gageheight_ft, 
            "discharge_cfs" : discharge_cfs, "precip_in" : precip_in, 
            "temp_c" : temp_c, "do_mgL" : do_mgL, "pH_su" : pH_su, 
            "cond_umhos" : conduct_umhos, "turb_ntu" : turb_ntu, 
            "velocity_ft_s" : velocity, "nitrate_mgL": nitrate} 

    return empties


def aq_reader(path):

    """
    Accepts the filepath argument to an AQUARIUS .csv file and returns a dictionary with desired data
    """
    with open(path) as f:
        
        timestamps = []
        values = []
        
        ## Reading csv
        lines = f.readlines() 
        for line in lines:
            if not line.startswith(("#", "ISO")):
                values.append(line.split(",")[2])
                timestamp =(line.split(",")[1])
                ## Returning a datetime object from date string
                timestamps.append(datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S"))
        if "AQUARIUS" in lines[0]:

            station = lines[0].split("@")[1][:8]
            print(station)
            name = lines[3].split(":")[1].split(",")[0].strip()
            print(name)
            param = lines[6].split(":")[1].split(",")[0].strip()
            units = lines[5].split(":")[1].split(",")[0].strip()
            print("Units : " + units) 
            
        else: 
            print("WRONG FILE OR FORMAT!!!")
            pass
    
    ## Dictionary for AQUARIUS file
    data_dict = {"station" : station, "name": name, "param": param, 
            "timestamps": np.asarray(timestamps), "values": np.asarray(values)}

    return data_dict


def fill_empties(gage_dict, data_dict):

    """
    Input arguments are the empty gage_dict created by the empty_data function and the data_dict
    returned from the aq_reader. Parameter values from the aq_reader data_dict are inserted
    in place of the np.nan values that exist in the gage_dict and amended gage_dict is returned.
    """

    dt_range = gage_dict["dt_range"]
    values = data_dict["values"]
    timestamps = data_dict["timestamps"]
    vals_perf = []
        
    ## Loop that finds matching timestamps and inserts data based upon index 
    ## in the full datetime range similar to excel VLOOKUP 
    
    for i in range(len(dt_range)):
        vals_perf.append(np.NaN)
        
        for j in range(len(timestamps)):
            if dt_range[i] == timestamps[j]:
                #print(timestamps[j])
                vals_perf[i] = values[j]
                break

    
    vals_perf = np.asarray(vals_perf).astype(np.float)
    
    ## Determining parameter from header information in AQUARIUS file dictionary
    ## Populating np.nan array as necessary

    if data_dict["param"] == "Precipitation":
        gage_dict["precip_in"] = vals_perf.astype(np.float)

    if data_dict["param"] == "Gage height":
        gage_dict["gageheight_ft"] = vals_perf.astype(np.float)
    
    if data_dict["param"] == "Discharge":
        gage_dict["discharge_cfs"] = vals_perf.astype(np.float)
    
    if data_dict["param"] == "Temperature":
        gage_dict["temp_c"] = vals_perf.astype(np.float)
    
    if data_dict["param"] == "Dissolved oxygen":
        gage_dict["do_mgL"] = vals_perf.astype(np.float)
    
    if data_dict["param"] == "pH":
        gage_dict["pH_su"] = vals_perf.astype(np.float)
    
    if data_dict["param"] == "Specific cond at 25C":
        gage_dict["cond_umhos"] = vals_perf.astype(np.float)
    
    if data_dict["param"] == "Turbidity":
        gage_dict["turb_ntu"] = vals_perf.astype(np.float)
    
    if data_dict["param"] == "Mean water velocity":
        gage_dict["velocity_ft_s"] = vals_perf.astype(np.float)
    
    if data_dict["param"] == "NO3+NO2":
        gage_dict["nitrate_mgL"] = vals_perf.astype(np.float)
    
    ## Printing desired stats

    print(data_dict["param"] + " Mean : " + str(np.nanmean(vals_perf)))
    print(data_dict["param"] + " Min : " + str(np.nanmin(vals_perf)))
    print(data_dict["param"] + " Max : " + str(np.nanmax(vals_perf)))
    
    ## Updated dictionary
    return gage_dict


def time_cols(dt_range):
    """
    Accepts the datetime range list produced by the full_dt_range function and returns 
    a dictionary with an np.array for date, time, and minutes as needed for the the SD1 file.
    """
    date = []
    time = []
    mins = []
    mins_val = 0
    for dt in dt_range:
        date.append(dt.strftime("%m/%d/%y"))
        time.append(dt.strftime("%H:%M"))

        ## Creating an array filled with 15 min increments
        mins.append(mins_val)
        if mins_val < 1425:
            mins_val += 15
        else:
            mins_val = 0
 
    for item in date, time, mins:
        item = np.asarray(item)
    
    ## Dictionary for time columns as per SD1 file
    time_dict= {"date" : date, "time": time, "mins": mins}
    
    return time_dict



def writetocsv(gage_dict, data_dict, time_dict, path):
    """
    Writes all data manipulated to a final .csv file. Required arguments include the updated gage_dict
    with updated parameter data, a single parameter data_dict(any) to populate the station information,
    the time_dict created in the time_cols function, and a filepath to the desired output file.
    """
    with open(path, 'w', newline = "\n") as f:
        
        writer = csv.writer(f)
        
        ## Header row per SD1 example
        writer.writerow(["station_num","station_name","station","Date","Time"," Mins","DT", "DT2",
        "gageheight_ft","discharge_cfs","precip_in", "temp_c", "do_mgL", " pH_su", "conductance_umhos",
        "turb_ntu", "Velocity", "Nitrate"] )
        
        ## Writing data to file
        for i in range(len(gage_dict["dt_range"])):

            writer.writerow([data_dict["station"], data_dict["name"], data_dict["name"].split(" ")[0],
                    time_dict["date"][i], time_dict["time"][i], time_dict["mins"][i],
                    gage_dict["dt_range"][i], "", gage_dict["gageheight_ft"][i], 
                    gage_dict["discharge_cfs"][i], gage_dict["precip_in"][i], 
                    gage_dict["temp_c"][i], gage_dict["do_mgL"][i], gage_dict["pH_su"][i],
                    gage_dict["cond_umhos"][i], gage_dict["turb_ntu"][i],
                    gage_dict["velocity_ft_s"][i], gage_dict["nitrate_mgL"][i]])



def plot(gage_dict):
    """
    Plots for each parameter
    """
    ## Create a directory for figures if not already existing
    if not "figs" in os.listdir("."):
        os.mkdir("figs")

    else:
        pass 
    
    params = ["gageheight_ft", "discharge_cfs", "precip_in", "temp_c", "do_mgL", "pH_su",
            "cond_umhos", "turb_ntu", "velocity_ft_s", "nitrate_mgL"]
    
    for param in params:
        for key in gage_dict:
            if param == key:
                try:
                
                    plt.plot(gage_dict["dt_range"], gage_dict[param])
                    plt.xlabel('Date')
                    plt.ylabel(param)
                    plt.savefig("figs/" + param + ".png")
                    plt.close()
            
                except:
                    ## For instances where param values are entirely np.nan vals
                    print("Unable to plot " + param)
                    pass
def main():

    ## First command line argument following program - water year - ex. 2017
    wtr_yr = int(sys.argv[1])   
    
    ## Second command line argument following program - location of data files - ex. test_data/
    loc = sys.argv[2]
    
    time_dict = time_cols(full_dt_range(wtr_yr))
    gage_data = empty_data(full_dt_range(wtr_yr))
    
    ## looping over list of csv files in location given in argument above
    for param_file in glob.glob(loc + "/*.csv"):
        data_dict = aq_reader(param_file)
        gage_dict = fill_empties(gage_data, data_dict)
    
    plot(gage_dict)
    
    ## Writing to output csv file to SD1 specifications
    ## Third command line argument following program - name of the csv file - ex. licking_river.csv
    writetocsv(gage_dict, data_dict, time_dict, sys.argv[3])
    

if __name__ == "__main__":
    main()
