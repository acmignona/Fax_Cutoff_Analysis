import tkinter as tk
from tkinter import *
import PIL
from PIL import Image, ImageSequence, ImageTk
import os
from datetime import datetime
from datetime import date, timedelta
import time

# Start of tkinter GUI
root = tk.Tk()
root.title('Cutoff Analysis - version 1.10.23') # version = y.mm.dd, but drop the decade y
frame = LabelFrame(root, padx=50, pady= 50)
frame.pack(padx=50, pady=10)

# Input Fields
directory_text = tk.Label(frame, text= "Enter Directory to Analyze: ")
directory_input = Entry(frame)
start_date_text = tk.Label(frame, text= "Enter Starting Date (MM/DD/YYYY): ")
start_date_input = Entry(frame)
end_date_text = tk.Label(frame, text= "Enter End Date (MM/DD/YYYY): ")
end_date_input = Entry(frame)
log_export_dir = tk.Label(frame, text= "Export Log Files to: ")
log_export_input = Entry(frame)
ctl_directory_text = tk.Label(frame, text= "Enter CTL Directory:")
ctl_directory_input = Entry(frame)
custom_ctl_text = tk.Label(frame, text= "Enter Custom CTL Field (Optional):")
custom_ctl_input = Entry(frame)

# Element Grid
directory_text.grid(column=0, row=2)
directory_input.grid(column = 1, row = 2, columnspan=1)
start_date_text.grid(column=0, row=3)
start_date_input.grid(column = 1, row = 3)
end_date_text.grid(column=0, row=4)
end_date_input.grid(column = 1, row = 4)
log_export_dir.grid(column=0, row=5)
log_export_input.grid(column = 1, row = 5)
ctl_directory_text.grid(column=0, row=6)
ctl_directory_input.grid(column = 1, row = 6)
custom_ctl_text.grid(column=0, row=7)
custom_ctl_input.grid(column = 1, row = 7)

overview_statistics = ''

def check_config_file(input_field):
    with open('default_configs.txt', 'r') as file:
        # loop through each line in the file
        for line in file:
            # check if the line starts with the input field
            if line.startswith(input_field):
                return line.replace(input_field, "").strip()

def check_ctl_file(ctl_file_path, input_field):
    with open(ctl_file_path, 'r') as file:
        # loop through each line in the file
        for line in file:
            # check if the line starts with the input field
            if line.startswith(input_field):
                return line.replace(input_field, "").strip()

def script_call():
    #if check_inputs():
    processing_mess2 = tk.Label(frame, text='Running..', fg='red')
    processing_mess2.grid(column=1, row=9)
    time.sleep(5)
    start_time = time.time()

    # Generates Time Stamps
    now = datetime.now()
    dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")
    exec_date = now.strftime("%Y/%m/%d")

# GET START DATE
    if not start_date_input.get():
        x_days_back = int(str(check_config_file('DAYS_BACK:')))
        x_days_back = date.today() - timedelta(days=x_days_back)
        x_days_back = x_days_back.strftime("%m/%d/%Y")
        start_date = datetime.strptime(x_days_back, '%m/%d/%Y')
    else:
        start_date = datetime.strptime(start_date_input.get(), '%m/%d/%Y')

# GET END DATE
    if not end_date_input.get():
        today = date.today()
        today = today.strftime("%m/%d/%Y")
        end_date = datetime.strptime(today, '%m/%d/%Y')
    else:
        end_date = datetime.strptime(end_date_input.get(), '%m/%d/%Y')

    directories = [directory_input.get()]
    if directories[0] == '':
        directories = []
        lookup_value = check_config_file('FAX_DIRECTORY:')
        dirs = [os.path.join(lookup_value, d) for d in os.listdir(lookup_value) if os.path.isdir(os.path.join(lookup_value, d))]
        if dirs:
            for d in dirs:
                directories.append(d)
                # append the existing directory if tif files exist in it, else ignore.
            if any(file.endswith(".tif") for file in os.listdir(lookup_value)):
                directories.append(lookup_value)
            else:
                print("did not detect any tifs in parent dir")
        else:
            directories.append(lookup_value)


    # Grab CTL folder Path
    ctl_directory = ctl_directory_input.get()
    if not ctl_directory:
        ctl_directory = 'CTL_DIRECTORY:'
        ctl_directory = check_config_file(ctl_directory)

    # print the value of the variable
    print(ctl_directory)

    # Fax Log Directory
    fax_log_dir = log_export_input.get()
    if not fax_log_dir: # If the user left the field blank, resort to the default configuration in config.txt
        fax_log_dir = 'LOG_DIRECTORY:'
        fax_log_dir = check_config_file(fax_log_dir)

    custom_ctl = custom_ctl_input.get()
    custom_header = ""
    if not custom_ctl:
        if check_config_file("CUSTOM_CTL_FIELD:"):
            custom_ctl = check_config_file("CUSTOM_CTL_FIELD:")
            custom_header = custom_ctl
        else:
            custom_ctl = None
            print("TESTING - CTL CUSTOM")
    else:
        custom_header =custom_ctl


    faxlog_name = str(fax_log_dir + "\cutoff_faxes_" + dt_string + ".csv") # Defines the name of the cutoff csv.
    faxlog = open(faxlog_name, "a") # TO DO : Have it open then close per fax.
    csv_header = "CLI Number, Receiving_Number, File Path, Page, Total_Pages, Call_Start_Time, File_Date, File_Time, Status, Confidence_Level"

    print("IF CUSTOMCTL")
    if custom_ctl:
        csv_header = csv_header + "," + custom_header + ",\n"
        print(csv_header)
    else:
        csv_header = csv_header + ",\n"
        print(csv_header)


    faxlog.write(csv_header)  # Creates header for csv file

    # Counters Below
    total_faxes = 0
    
    total_pages = 0
    corrupted_faxes = 0
    cutoff_faxes = 0
    low_con_cut = 0

    # Actual Script Below
    for directory in directories:
        print(directory)
        all_faxes = os.listdir(directory)  # Lists all files within the specified directory
        for fax in all_faxes:  # Iterates through each file found in the directory
            if ".tif" in fax:  # If the file ends in .tif, it will process the below script
                file_path = str(directory + "\\" + fax)

                # Parse CTL Data
                ctl_path = str(ctl_directory + "\\" + fax[:-4] + ".ctl")
                if os.path.exists(ctl_path):
                    cli = check_ctl_file(ctl_path, "CLI: ")
                    dmtf = check_ctl_file(ctl_path, "DTMF: ")
                    accepted_time_stamp = check_ctl_file(ctl_path, "Accepted: ")
                    accepted_time_stamp = datetime.strptime(accepted_time_stamp, "%y-%m-%d %H:%M:%S").strftime("%H:%M:%S")
                    if custom_ctl:
                        custom_CTL_field = check_ctl_file(ctl_path, custom_ctl)
                else:
                    cli = "CTL Not Found"
                    dmtf = "CTL Not Found"
                    accepted_time_stamp = "CTL Not Found"
                    custom_CTL_field = "CTL Not Found"

                file_date_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_date_time > start_date and file_date_time < end_date:
                    faxlog = open(faxlog_name, "a")
                    try:  # This attempts to open the actual file. If the fax is corrupted, it will fail.
                        total_faxes = total_faxes + 1
                        faxpath = Image.open(str(file_path))  # Specifies the exact path of the fax that's being evaluated
                        for i, page in enumerate(ImageSequence.Iterator(faxpath)):  # iterates through the pages
                            total_pages = total_pages + 1
                            fax_page_num = ("%d" % i)
                            # Variable below outputs the page's details, which is then written to the CSV.
                            variable_data = str(
                                f"{cli},"
                                f"{dmtf},"                                
                                f"{file_path},"
                                f"{(int((fax_page_num)) + 1)},"
                                f"{(int(faxpath.n_frames))},"
                                f"{accepted_time_stamp},"
                                f"{file_date_time.strftime('%Y-%m-%d')},"
                                f"{file_date_time.strftime('%H:%M:%S')}"
                            )
                            if (page.height / page.width) > 1.2:  # Tests cutoff criteria
                                print(str(fax) + " was evaluated as clean.")
                                faxlog.write(
                                    f"{variable_data},"
                                    f"Clean,High,"
                                    )
                            elif (page.height / page.width) < .6 and (page.height / page.width) != 0:
                                cutoff_faxes = cutoff_faxes + 1
                                print(str(fax) + " was evaluated as cutoff.")
                                faxlog.write(
                                    f"{variable_data},"
                                    f"Cutoff,Very High,"
                                    )
                            elif page.height == 0:
                                corrupted_faxes = corrupted_faxes + 1
                                print(str(directory + "\\" + fax) + " was likely a corrupted file.")
                                faxlog.write(
                                    f"{variable_data},"
                                    f"Corrupted,"
                                )
                            elif (page.height / page.width) < .7:
                                print(str(fax) + " was evaluated as clean.")
                                faxlog.write(
                                    f"{variable_data},"
                                    f"Clean,Med,"
                                    )
                            elif (page.height / page.width) < 1:
                                cutoff_faxes = cutoff_faxes + 1
                                print(str(fax) + " was evaluated as cutoff.")
                                faxlog.write(
                                    f"{variable_data},"
                                    f"Cutoff,VERY HIGH,"
                                )
                            elif (page.height / page.width) < 1.15:
                                cutoff_faxes = cutoff_faxes + 1
                                print(str(fax) + " was evaluated as cutoff.")
                                faxlog.write(
                                    f"{variable_data},"
                                    f"Cutoff,Med,"
                                )
                            elif (page.height / page.width) < 1.2:
                                cutoff_faxes = cutoff_faxes + 1
                                print(str(fax) + " was evaluated as cutoff.")
                                faxlog.write(
                                    f"{variable_data},"
                                    f"Cutoff,LOW,"
                                )
                            else:
                                cutoff_faxes = cutoff_faxes + 1
                                print(str(fax) + " was evaluated as cutoff.")
                                faxlog.write(
                                    f"{variable_data},"
                                    f"Cutoff,Med2,"
                                )
                            if custom_ctl:
                                faxlog.write(
                                    f"{custom_CTL_field},"
                                )
                            faxlog.write(
                                f"\n"
                            )
                    except PIL.UnidentifiedImageError:
                        corrupted_faxes = corrupted_faxes + 1
                        faxlog.write(
                            f"{variable_data},"
                            f"Corrupted, \n"
                        )
                    faxlog.close()
                else:
                    print(fax + " did not meet date criteria.")
            else:
                print(fax + " was an inappropriate extension and has been omitted from analysis")

    # Defined function below
    def percentage(insert_number):
        insert_number = (str("{:.0%}".format((insert_number))))
        return insert_number

    # variables needed for summary csv
    exec_dur = (time.time()- start_time)

    # Summary Log Information
    summary_log_dir = fax_log_dir
    summary_log_name = str(summary_log_dir + "\Summary_Cutoff_Statistics.csv") # Defines the name of the summary stat csv file.

    # Checks if summary file already exists. If it doesnt, it creates it and adds a header.
    if os.path.isfile(summary_log_name):
        print("\nFile already exists. No action needed.")
    else:
        summary_log = open(summary_log_name, "a")
        summary_log.write(
            'Total Faxes, Total Pages, Total Corrupted, Total Cutoff Pages, Page Cutoff Ratio, Script Execution Time, Script Execution Date\n'
        )
        summary_log.close()

    if cutoff_faxes == 0 or total_faxes == 0:
        cutoff_ratio = 0
    else:
        cutoff_ratio = cutoff_faxes / total_faxes

    # Appends cutoff data to the summary log
    summary_log = open(summary_log_name, "a")
    summary_log.write(f'{total_faxes}, {total_pages}, {corrupted_faxes}, {cutoff_faxes},{cutoff_ratio},{exec_dur:.2f} seconds, {exec_date}\n')
    summary_log.close()

    # Summary statistics presented below:
    if corrupted_faxes == 0 or total_faxes == 0:
        corrupted_fax_str = str(f"Total Corrupted Faxes: {corrupted_faxes} - (0%)")
    else:
        corrupted_fax_str = str(f"Total Corrupted Faxes: {corrupted_faxes} - ({percentage(corrupted_faxes / total_faxes)})")

    if cutoff_faxes == 0 or total_faxes == 0:
        cutoff_fax_str = str(f"Total Cutoff Pages: {cutoff_faxes}  - (0%)")
    else:
        cutoff_fax_str = str(f"Total Cutoff Pages: {cutoff_faxes} - ({percentage(cutoff_ratio)})")

    script_time = "{:.2f}".format((time.time() - start_time))

    global overview_statistics
    overview_statistics = str(f"Total Faxes: {(total_faxes)} \nTotal Pages: {total_pages}\n{corrupted_fax_str}\n{cutoff_fax_str}\n--------------------------------------------\n Script execution time: {script_time} seconds \n -------------------------------------------- \n Report path below: \n {faxlog_name}")
    print(overview_statistics)
    processing_mess = tk.Label(frame, text='FINISHED!', fg='red')
    processing_mess.grid(column=1, row=9)

    overview_gui_window = tk.Label(root, text=overview_statistics)
    overview_gui_window.pack(pady=20)

 ## GUI - Picture
logo = Image.open('gsd2.png')
logo = logo.resize((75, 75))  # resizing the photo since it was massive.
logo = ImageTk.PhotoImage(logo)
logo_label = tk.Label(image=logo)
logo_label.image = logo
logo_label.pack(pady=0)

# GUI - Text
instructions = tk.Label(frame, text= "Cutoff Analysis Adhoc Program. \n \n*TIP* - Leave all or some fields blank to use the default values in default_configs.txt!\n")
instructions.grid(columnspan=3, column=0, row=0, pady=0)

# GUI - Button
browse_text = tk.StringVar()
browse_btn = tk.Button(frame, textvariable=browse_text, command = lambda:script_call(), bg ='brown', fg='white')
browse_text.set("Start Analysis")
browse_btn.grid(column=1, row=8, pady= 10)

# End of GUI
frame.mainloop()


