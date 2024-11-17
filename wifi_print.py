#############################################
#                                           #
#      Program for printing and             #
#      connecting to the best               #
#      RSSI wifi spot(Works on Mac only).   #
#      written by Yoni Danzig 24/10/21      #
#                                           #
#############################################

####### Importing Modules######
#Importing the subprocess module - used to record the airport network console command
import subprocess as sp

###### Internal Functions######
#Path of airport program (default path - only in apple mac)
airportPath = '/System/Library/PrivateFrameworks/Apple80211.framework/Versions/A/Resources/'

#Computer wifi validation: returns False if wifi is off and returns True if wifi is on.
def is_wifi_on():
    result = sp.check_output(["airport", "-I"])
    if result.decode('ascii').replace("\n", "") == 'AirPort: Off':
        return False
    else:
        return True

#Validation function on user input (y/n)
def inputYn(message):
    userInput = input(message)
    while userInput not in ['y', 'n']:
        print("Please enter only y/n")
        userInput = input(message)
    return userInput

#Internet connection test
def connectionTest():
    import socket
    IPaddress = socket.gethostbyname(socket.gethostname())
    if IPaddress == "127.0.0.1":
        print("No internet, your localhost is " + IPaddress)
    else:
        print("Connected, with the IP address: "+ IPaddress)

#Function that connects the computer to a network given an SSID and PASSWORD. airport program path is needed to run airport program
def Wifi_connect(ssid, password, airportPath):
    try:
        Connection_trial = sp.check_output(["networksetup", "-setairportnetwork", "en0", ssid, password])
    except:
        print("Exception occurred when trying to setup the wifi network...")
        print(Connection_trial)
    else:                                                                           #This code is executed only if no exceptions were raised in the try block
        Connection_trial = Connection_trial.decode("utf-8")                         #Converting message from binary to utf-8 text
        if (Connection_trial == ""):                                                #Few scenarios can occur:
            print("Connected successfully to: ", ssid)                              ########Case (1)Connected successfully#####
            print("Connection details:")
            print(sp.check_output([airportPath + 'airport', '-I']).decode("utf-8")) #Showing connection details.
            print("-------------------")
            userInput = input("Do you want to validate your internet connection? (y/n)")
            if userInput == 'y':
                print("Internet connection test:")                                  #Verification that user can access the Internet
                connectionTest()
            else:  #inputYn == 'n':
                print("You can test in manually using your internet browser...")   #Verification can be done by the user too...
        elif ('error -3900' in Connection_trial):
            print("Wrong wifi Password...")                                        ######Case (2) Wrong wifi Password#####
        elif ("power is off" in Connection_trial):                                 ######Case (3) Wifi power is off#######
            print (Connection_trial)
        elif ("Could not find" in Connection_trial):                               ######Case (4) SSID does not exists####
            print ("could not find:", ssid, " - router might be off or you got too far from the router")

#Function that prints all the wifi hot spots around (SSID,BSSID,RSSI] and prompts the user to connect to the best RSSI wifi router
def wifiPrintConnect(airportPath=airportPath):
    devices = sp.check_output([airportPath + 'airport', '-s'])                     #Using the check_output() for having the network term retrieval
    devices = devices.decode('ascii')                                              #Decoding the bytes type to strings
    devices = devices.split('\n')                                                  #We can place every line as an array element
    devices = devices[1:-1]                                                        #Removing first and last array element
    devices_clean = []                                                             #2d array :[[ssid1,bssid1,rssi1],[ssid2,bssid2,rssi2],....]
    for each_line in devices:                                                      #2d array above is not in order, with spaces - idea is to "cut" and assign to the correct variable:
        arr = []                                                                   #arr is an inner array for every line
        arr.append(each_line[:32].strip())                                         #1st we append the SSID
        middle = [e for e in each_line[33:69].split(" ") if                        #Nice and elegant list comprehension way... leaving the spaces out.
                  e != ""]                                                         #Middle of message contains the BSSID,RSSI,CHANNEL,HT,CC.
        arr.append(middle[0])                                                      #2nd append is BSSID
        arr.append(middle[1])                                                      #3rd we append RSSI
        security = each_line[70:].strip()                                          #For future use if needed (security)
        devices_clean.append(arr)                                                  #Creating the "clean" array with [SSIDx,BSSIDx,RSSIx]|x=1,2,3..
    sorted_list = sorted(devices_clean,
                         key=lambda x: int(x[2]), reverse=True)                    #Sorting the wifi hotspots list - best RSSI (closest to zero) on the top
    ###Printing part - this method will print the sorted list in a nice and clean way...
    print("Printing wireless devices nearby....")
    print("{:<30} {:<20} {:<5}".format('SSID', 'BSSID', 'RSSI'))                   #Printing the title
    print("\033[92m" + "{:<30} {:<20} {:<5}".format(sorted_list[0][0],             #First row (best RSSI) is highlighted as requested
                                                    sorted_list[0][1],
                                                    sorted_list[0][2]))
    print("\033[0m", end="")                                                       #Getting the text highlight off
    for v in sorted_list[1:]:                                                      #Printing all the other ordered wifi devices
        ssid, bssid, rssi = v
        print("{:<30} {:<20} {:<5}".format(ssid, bssid, rssi))
    print()
    userInput = inputYn("Do you want to connect to the best wifi spot: " + sorted_list[0][0] + " ? (y/n)")
    if userInput == 'y':
        password = input("Please enter wifi password")
        Wifi_connect(sorted_list[0][0], password ,airportPath=airportPath)         #Connecting the the best RSSI spot
    else:                                                                          # inputYn == 'n':
        print("Goodbye...")

    #########Main Function########
def main():
    if is_wifi_on():                                                               #wifi is on
        wifiPrintConnect()
    else:                                                                          #wifi is off
        print("Enable your wifi first...")

if __name__ == '__main__':
    main()