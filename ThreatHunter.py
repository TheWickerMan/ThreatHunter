import argparse
from argparse import RawTextHelpFormatter
from Modules.LoggingModule import Logging
import datetime
import os
import json

#Header on the help page
parser = argparse.ArgumentParser(description="----------ThreatHunter-Help-Page----------", formatter_class=RawTextHelpFormatter)

#Inline Arguments
parser.add_argument("-new", help="Enter The Target Organisation's Name. \n")
parser.add_argument("-passive", help="Ensures that only passive, non-direct communication to the target. \n", action="store_true")
parser.add_argument("-settings", help="Modify the application settings. \n", action="store_true")

#Allocates the method to call the arguments to 'args'
args = parser.parse_args()

class Main():
    BaseInformation = {"OrganisationName":"", "LogFile":"", "API_Keys_Directory":"./Modules/API_Keys"}
    APIKeys = {}

class Settings():
    #Menu system to allow modification of script settings
    def Menu():
        while True:
            MenuSelection = input("\1) Modify tool authentication information \n0) Exit \n Select an option: ")

            if MenuSelection == "1":
                print("\nModifying API Keys: \n(Press enter to skip)")
                Settings.ModifyAPIKeys()
            if MenuSelection == "0":
                break
    #Responsible for modification of API details
    def ModifyAPIKeys():
        with open(Main.BaseInformation["API_Keys_Directory"]) as API_Directory:
            Main.APIKeys = json.load(API_Directory)
        for x in Main.APIKeys:
            APIValue = input("      [{}:{}]:".format(x, Main.APIKeys[x]))
            if APIValue == None or APIValue == "":
                pass
            else:
                Main.APIKeys[x] = APIValue
        with open(Main.BaseInformation["API_Keys_Directory"], "w") as API_Directory:
            API_Directory.write(json.dumps(Main.APIKeys))
        print()

class New():
    #Initialises the new project
    def Initialise():
        #Generates month directory
        CurrentMonth = datetime.date.today().strftime("%B %Y")
        if not os.path.isdir("./Projects/{}".format(CurrentMonth)):
            os.makedirs("./Projects/{}".format(CurrentMonth))
            print("Creating \'./Projects/{}\' directory.".format(CurrentMonth))

        #Allows users to re-enter organisation names if a project already exists
        while True:
            if os.path.isdir("./Projects/{}/{}".format(CurrentMonth, Main.BaseInformation["OrganisationName"])):
                OrganisationExists = input("It looks like your project already exists.\n    Please enter a new organisation name: ")
                if OrganisationExists:
                    Main.BaseInformation["OrganisationName"] = OrganisationExists
                else:
                    print("No organisation entered.  Exiting...\n")
                    exit()
            else:
                #Establishes log file and creates the organisation directory
                os.makedirs("./Projects/{}/{}".format(CurrentMonth, Main.BaseInformation["OrganisationName"]))
                print(("Creating \'./Projects/{}/{}\' project.".format(CurrentMonth, Main.BaseInformation["OrganisationName"])))
                Main.BaseInformation["LogFile"] =  "./Projects/{}/{}/Log".format(CurrentMonth, Main.BaseInformation["OrganisationName"])
                Logging.Log(Main.BaseInformation["LogFile"], "INFO", "Generated \'{}/{}\' project.".format(CurrentMonth, Main.BaseInformation["OrganisationName"]))
                break
        #Loads the APIKeys
        with open(Main.BaseInformation["API_Keys_Directory"]) as API_Directory:
            Main.APIKeys = json.load(API_Directory)
            Logging.Log(Main.BaseInformation["LogFile"], "INFO", "Loaded API keys from file.")

    def OrganisationInformation():
        Logging.Log(Main.BaseInformation["LogFile"], "INFO", "Starting initial information requests.")
        InformationStore = {"OrganisationName":Main.BaseInformation["OrganisationName"], "EmailFormat":"", "Domains":"", }
        print("\nPlease enter any known information: \n(Press enter to skip a section)\n)")

        #Allows the user to specify the email format for the target.
        while True:
            EmailFormat = (input("---Email format\n   [Firstname = [FN], Surname = [SN], First Initial = [FI], Surname Initial = [SI]\n   (EG: [FN].[SN]@test.com)\n\n   Email Format:"))
            if EmailFormat == None or EmailFormat == "":
                break
            else:
                Logging.Log(Main.BaseInformation["LogFile"], "INFO", "{} - Email format set.".format(EmailFormat))
                InformationStore["EmailFormat"] = EmailFormat
                break


        #Allows the user to specify a file containing known domains
        while True:
            DomainList = input("Specify a file containing a list of known domain names: ")
            try:
                if os.path.isfile(DomainList):
                    Logging.Log(Main.BaseInformation["LogFile"], "INFO", "{} - File confirmed to be available.".format(DomainList))

                    with open(DomainList) as DomainListFile:
                        InformationStore["Domains"] = DomainListFile.read().splitlines()
                else:
                    Logging.Log(Main.BaseInformation["LogFile"], "ERROR", "{} - File is inaccessible.".format(DomainList))
                    print("{} file does not exist or file permissions are preventing access.".format(DomainList))
            except OSError as Error:
                Logging.Log(Main.BaseInformation["LogFile"], "ERROR", "{} - File access returns the following error: {}".format(Error))
                print("A system error has occurred.  You may need to check file permissions to access the file.")

print()
if args.new:
    Main.BaseInformation["OrganisationName"] = args.new
    New.Initialise()
    New.OrganisationInformation()

if args.settings:
    Settings.Menu()
print()
