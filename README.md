# Fax_Cutoff_Analysis

## Description
Within the faxing world, there's a phenomenon known as "cut off/incomplete" faxes. This manifests as receiving fax machine not receiving an entire fascilmile page. This program will determine whether a page of an image is cut off based on the expected 8.5 x 11 page ratio. 

## How to use

### Executable
1. For transparency, the Python code is provided within this repository. If you trust this executable, you can download it and use the tool. 

2. Run the program. This program will prompt you to enter in fields. Alternatively, you can use the default_configs.txt to predefine these settings and simply leave the GUI fields blank.  Click "Start Analysis". 
![image](https://github.com/acmignona/Fax_Cutoff_Analysis/assets/81653524/5c7134de-05d7-4f80-8e45-ba289662f096)

The program will crawl through the image directory and open all the images within the defined critera. Once the program is finished, the GUI will indicate that it's done and display some summary metrics: 

The complete report data will be found within the configured export directory field. 

### Python
To run this program within Python, you will need to install the following libraries: 
- Tkinter
- PIL (pillow)

## Potential Use Cases
While cutoff faxes can be an annoying issue for a sender, usually a sender can simply re-attempt sending the fax without issues. However, this can become a major issue within environments that process a large volume of inbound faxes. After creating this program, I used it within an enterprise environment to analyze the correlation between certain telephony carriers and our inbound cut off fax rate. We idenfitied the best performing carrier and reduced our daily cutoff fax rate from 5% (~900 faxes monthly) to less than 0.20% (~36 faxes monthly). This drastically reduced the amount of work required from technicians since they no longer had to reach out to the sender to re-transmit the fax. Unfortunately, due to the antiquated nature of faxing technology, completely eliminating cut off faxes is almost an impossibility.

## Requirements
- This program was made to interface with Zetafax Server fax files: .tif iamges and .ctl meta data files. While this program can analyze images from other files, it has not been tested to pull transmission data from corresponding meta data files that other faxing solutions might use. 
- This program requires that you store your fax images within a centralized folder. This can easily be achieved via a PowerShell script/Batch file
- This program has only been tested on Windows machines.

