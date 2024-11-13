                                MT5 V2

# Basic info
1. This bot use 50 on 100 SMA to check serials of pair in the froxe broker for signals of trade and place trades
2. Serials of pairs e.g "EUR", "USD", "GBP", "JPY", "CHF", "NZD", "CAD"
3. After the first run of the program a symbols.csv file will be in the MT5_V2.1 folder
4. This bot run in invertval at 30 seconds.
5. The setup.py is to build for .exe file for MAC OS system.


------------------ General info -----------------------------------------
2. This trading bot uses the schdeuler to look for signals, trade at intervals and shut down when the day ends.
3. You can change the currency pair you want to trade by going to /raw code folder, then the server.py file, in the funtion "get_currency_list()"
4. You can change the SMA  you want to trade by going to /raw code folder, then the server.py file, find the variable "short_window" and "long_window"
5. This changes will not take place in the scheduler.exe unless you run the builder.py file after the changes.


---------------- Running the raw script ----------------------------
1. You can change the currency pair you want to trade in the server.py file, in the funtion "get_currency_list()"
2. you can change the interval in the schdeuler file in line 50.
3. Install all dependcies 
4. run the schdeuler.py to start
5. put in login details and watch the bot start the process


---------------- Running the .exe file ----------------------------
# How to Run the .exe file
1. Go to the build folder and run the builder.py file
2. Follow the instructions on the screen and install all needed 
3. double-click and run the scheduler.exe in the bulder-EXE folder inside the build folder.
4. Follow the instructions on the screen.
5. it should be running after this 

If you see a security warning, click "Run" or "Yes" to allow the program to execute.


-------------- For errors ---------------------------

1.If you encounter any error while building the .exe file with the build script go to the build folder then log folder and get the log file.
2.If you encounter any error while running the .exe file pls go the log folder and get the log file.
3.This log files would be used to note and solve the problem encountered while the program was running.





Thank you for using this script!
