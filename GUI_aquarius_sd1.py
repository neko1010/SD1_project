from datetime import datetime, timedelta
import numpy as np
import csv
import glob
import os
import sys
import matplotlib.pyplot as plt     
from tkinter import filedialog, messagebox
from tkinter import *
from tkinter import ttk

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

    params = ["gageheight_ft", "discharge_cfs", "precip_in", "temp_c", "do_mgL", "pH_su",
            "cond_umhos", "turb_ntu", "velocity_ft_s", "nitrate_mgL"]

    y_labels = ["Gage height (ft)", "Discharge (cfs)", "Precipitation (in)", "Temperature (deg C)",
            "Dissolved Oxygen (mg/L)", "pH", "Specific Conductance @ 25 deg C (uS/cm)",
            "Turbidity (FNU)", "Velocity (ft/s)", "Nitrate (mg/L)"]

    for param in params:
        for key in gage_dict:
            ## Matching dict key to appropriate y axis label
            for i in range(len(params)):
                if param == params[i]:
                    y_label = y_labels[i] 
            if param == key:
                try:
                
                    fig = plt.figure()
                    ax = fig.add_subplot(111)
                    ax.plot(gage_dict["dt_range"], gage_dict[param])
                    plt.xlabel('Date' )
                    ## Rotating x axis labels
                    plt.xticks( rotation = 45)
                    ## Gridlines on
                    ax.grid(True)
                    ## Text to include summary stats
                    ## transform = ax.transAxes places text in relative location
                    ## with (1,1) as top right corner
                    ax.text(0.75, 0.8, "Mean: " + str(round(np.nanmean(gage_dict[param]), 2)) + 
                        "\nMin: " + str(round(np.nanmin(gage_dict[param]),2)) + 
                        "\nMax: " + str(round(np.nanmax(gage_dict[param]),2)), 
                        transform = ax.transAxes, bbox = dict(fc = 'white'))
                    plt.ylabel(y_label)
                    fig.subplots_adjust(bottom = 0.2)
                    fig.savefig("figs/" + param + ".png")
                    plt.close()
            
                except:
                    ## For instances where param values are entirely np.nan vals
                    print("Unable to plot " + param)

def browse_button():
    """
    Creating a command for the tkinter browse button below.
    Opens a file dialog window allowing for user selection of input directory.
    """
    ## Store the path as a global variable
    global folder_path
    filename = filedialog.askdirectory()
    folder_path.set(filename)
    return folder_path

def outputfile():
    """
    Creating a command for the tkinter save as button below.
    Selects name and path of output .csv file.
    """
    global out_path
    filepath = filedialog.asksaveasfilename(defaultextension = ".csv",
            filetypes = (("CSV","*.csv"),("all files","*.*")))
    out_path.set(filepath)
    return out_path


def main():
    pass
   ## tkinter functions misbehaving in main function 
    

if __name__ == "__main__":

    ## Instantiating root widget
    root = Tk()

    ## Title
    root.title("AQUARIUS water year time series")
    menu = Menu(root)
    root.config(menu= menu) 
    explanation ="Compile data from raw United States Geological Survey (USGS) AQUARIUS .csv files into a single .csv file with ease! The output file will include a complete water year time series in 15 minute intervals for data provided from a given USGS gage, as well as a plot for each. Simply insert the water year, select file path to a folder with AQUARIUS files for the appropriate gage and water year,and provide an output file name in .csv format. Progress reports will appear as files are processed, but require no interaction from the user unless a file entered is not from the correct USGS gage."

    helpmenu = Menu(menu)
    menu.add_cascade(label = "Help", menu = helpmenu)
    
    ## using lambda for a quick function call
    helpmenu.add_command(label = "About", 
            command = lambda : messagebox.showinfo("About", explanation))

    ## StringVar and IntVar are a type of control variable. 
    ## These store values needed later
    folder_path= StringVar()
    out_path = StringVar()
    h20_yr = StringVar()  

    ## Label for water year prompt
    wy_lbl= Label(root, text = "Input water year: ", font = "12")
    wy_lbl.grid( row = 1, column = 0)

    ## Entry box
    wy_entry = Entry(root, textvariable = h20_yr, width = 25)
    wy_entry.grid(row = 1, column = 1)

    ## USGS logo- note grid methods- column span, sticky (east, west)
    logo = PhotoImage(file = "logo/USGSlogo_gre_sm.png")
    insert_logo = Label(root, image = logo) 
    insert_logo.grid(row = 0, column = 0, columnspan = 3, sticky = EW)

    ## Browse button 
    browse = Button(text="Input Folder", command=browse_button, width = 25)
    browse.grid(row=2, column=1)
    
    ## Label to update folder chosen as input
    lbl1 = Label(root, textvariable = folder_path)
    lbl1.grid(row = 2, column=0)

    ## Save As button
    save_as = Button(text = 'Save Output File As', command = outputfile, width = 25)
    save_as.grid(row = 3, column = 1)
    
    ## Output file path label
    lbl2 = Label(root, textvariable= out_path)
    lbl2.grid(row =3, column = 0)

    
    ## GO Button that begins program
    process = Button(root, text = "Process Files", command = root.destroy, width = 25)
    process.grid(row = 4, rowspan = 2, column = 1)

    ##AQUARIUS logo
    #logo_aq = PhotoImage(file = "aquarius_logo.png")
    #insert_logo_aq = Label(root, image = logo_aq)
    #insert_logo_aq.grid(row = 4, rowspan = 2, column = 0)
   
    ## tkinter event loop that enables window
    root.mainloop()

    ## .get method needed to extract value from PY_VAR#
    loc = str(folder_path.get())
    wtr_yr = int(h20_yr.get())

    time_dict = time_cols(full_dt_range(wtr_yr))
    gage_data = empty_data(full_dt_range(wtr_yr))

    ## Empty list to test all files are from same gage as first file 
    gage_test = []
    
    ## looping over list of csv files in location given in argument above
    for param_file in glob.glob(loc + "/*.csv"):
        
        data_dict = aq_reader(param_file)
        gage_test.append(data_dict["station"])
        root = Tk()
        root.title("Progress Report")
        
        ## Checking gage numbers
        if data_dict["station"] != gage_test[0]:
            ## root.withdraw() removes parent widget to show only error message
            root.withdraw()
            messagebox.showerror("Invalid file entry: ", "Data file not from same station!")
            continue
        
        else:
            gage_dict = fill_empties(gage_data, data_dict)
            prompt = data_dict["param"] + " Processed!"
            img = PhotoImage(file =  "logo/USGSlogo_gre_sm.png")
            
            logo = Label(root, image = img)
            logo.grid(row = 0, column = 0, columnspan = 2)
            
            label = Label(root, compound = "center" , text = prompt,
                    font = 'Verdana 12')#, fg = 'white')
            label.grid(row = 0, column = 1)
            
            ## Message destroys itself after 10 secs to limit interaction required
            root.after(10000, lambda : root.destroy())
            root.mainloop()
    
    plot(gage_dict)
    writetocsv(gage_dict, data_dict, time_dict, out_path.get())

    root = Tk()
    root.withdraw()
    messagebox.showinfo("Processing complete", "Output written as " + out_path.get()) 
