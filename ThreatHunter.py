import argparse
from argparse import RawTextHelpFormatter
import datetime
import os
import json
import re

from Modules.LoggingModule import Logging
from Modules.Censys import Main as Censys


#Header on the help page
parser = argparse.ArgumentParser(description="----------ThreatHunter-Help-Page----------", formatter_class=RawTextHelpFormatter)

#Inline Arguments
parser.add_argument("-run", help="Enter The Target Organisation's Name. \n")
parser.add_argument("-passive", help="Ensures that only passive, non-direct communication to the target. \n", action="store_true")
parser.add_argument("-settings", help="Modify the application settings. \n", action="store_true")

#Allocates the method to call the arguments to 'args'
args = parser.parse_args()

class Main():
    BaseInformation = {"OrganisationName":"", "LogFile":"", "API_Keys_Directory":"./Modules/API_Keys", "ModuleSettingsDirectory":"./Modules/ModuleSettings"}
    APIKeys = {}
    ModuleSettings = {}
    GatheredInformation = {}
    InformationStockpile = {"Domains/IPAddresses":[], "FoundEmailAddresses":"", "GeneratedEmailAddresses":"", "EmailFormat":""}

class Settings():
    #Menu system to allow modification of script settings
    def Menu():
        while True:
            MenuSelection = input("\n1) Modify tool authentication information \n2) Modify tool settings \n0) Exit \n Select an option: ")
            if MenuSelection == "1":
                print("\nModifying API Keys: \n(Press enter to skip)")
                Settings.ModifyAPIKeys()

            #Tool Selection
            if MenuSelection == "2":
                while True:
                    ToolSelection = input("\n1) Censys\n0) Back\n")

                    #CENSYS SETTINGS
                    if ToolSelection == "1":
                        with open(Main.BaseInformation["ModuleSettingsDirectory"]) as Module_Directory:
                            Main.ModuleSettings = json.load(Module_Directory)
                        for x in Main.ModuleSettings["Censys"]:
                            SettingsValue = input("     [{}:{}]".format(x, Main.ModuleSettings["Censys"][x]))
                            if SettingsValue == None or SettingsValue == "":
                                pass
                            else:
                                Main.SettingsValue["Censys"][x] = SettingsValue
                        with open(Main.BaseInformation["ModuleSettingsDirectory"], "w") as Module_Directory:
                            Module_Directory.write(json.dumps(Main.ModuleSettings))

                    if ToolSelection == "0":
                        break

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

class Run():
    #Initialises the  project
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
                Logging.Log(Main.BaseInformation["LogFile"], "THREATHUNTER", "INFO", "Generated \'{}/{}\' project.".format(CurrentMonth, Main.BaseInformation["OrganisationName"]))
                break
        #Loads the APIKeys
        with open(Main.BaseInformation["API_Keys_Directory"]) as API_Directory:
            Main.APIKeys = json.load(API_Directory)
            Logging.Log(Main.BaseInformation["LogFile"], "THREATHUNTER", "INFO", "Loaded API keys from file.")

    def OrganisationInformation():
        Logging.Log(Main.BaseInformation["LogFile"], "THREATHUNTER", "INFO", "Starting initial information requests.")
        InformationStore = {"OrganisationName":Main.BaseInformation["OrganisationName"], "EmailFormat":"", "Domains":[], }
        print("\nPlease enter any known information: \n(Press enter to skip a section)\n")
        #Allows the user to specify the email format for the target.
        while True:
            EmailFormat = (input("---Email format\n   [Firstname = [FN], Surname = [SN], First Initial = [FI], Surname Initial = [SI]\n   (EG: [FN].[SN]@test.com)\n\n   Email Format:"))
            print()
            if EmailFormat == None or EmailFormat == "":
                break
            else:
                Logging.Log(Main.BaseInformation["LogFile"], "THREATHUNTER", "INFO", "{} - Email format set.".format(EmailFormat))
                InformationStore["EmailFormat"] = EmailFormat
                Main.InformationStockpile["EmailFormat"] = EmailFormat
                break
        #Allows the user to specify a file containing known domains
        while True:
            DomainList = input("---Known Domain Names\n   Specify a file containing a list of known domain names: ")
            if DomainList == "" or DomainList == None:
                break
            try:
                if os.path.isfile(DomainList):
                    Logging.Log(Main.BaseInformation["LogFile"], "THREATHUNTER", "INFO", "{} - File confirmed to be available.".format(DomainList))

                    with open(DomainList) as DomainListFile:
                        ProvidedDomains = DomainListFile.read().splitlines()
                        Logging.Log(Main.BaseInformation["LogFile"], "THREATHUNTER", "INFO", "{} - File opened".format(DomainListFile))
                    for x in ProvidedDomains:
                        StrippedString = re.sub("(http:\/\/|https:\/\/|www.)", "", x)
                        Logging.Log(Main.BaseInformation["LogFile"], "THREATHUNTER", "DEBUG", "{}:{} - Stripped unneeded substrings".format(x, StrippedString))
                        InformationStore["Domains"].append(StrippedString)

                    #Strips empty values and removes duplicates
                    InformationStore["Domains"] = set(filter(None, InformationStore["Domains"]))
                    for x in (list(InformationStore["Domains"])):
                        Main.InformationStockpile["Domains/IPAddresses"].append(x)
                    Logging.Log(Main.BaseInformation["LogFile"], "THREATHUNTER", "DEBUG", "{} - Confirmed that Domain list is unique".format(InformationStore["Domains"]))
                    break
                else:
                    Logging.Log(Main.BaseInformation["LogFile"], "THREATHUNTER", "ERROR", "{} - File is inaccessible.".format(DomainList))
                    print("{} file does not exist or file permissions are preventing access.\n".format(DomainList))
            except OSError as Error:
                Logging.Log(Main.BaseInformation["LogFile"], "THREATHUNTER", "ERROR", "{} - File access returns the following error: {}".format(Error))
                print("A system error has occurred.  You may need to check file permissions to access the file.\n")

    def Passive(OrganisationName):
        PassiveDict = {}

        print("\nCommencing Censys Checks...")
        PassiveDict.update({"Censys":Censys.Run(Main.BaseInformation["LogFile"], Main.BaseInformation["API_Keys_Directory"], OrganisationName)})
        for x in PassiveDict["Censys"]:
            if x != None:
                Main.InformationStockpile["Domains/IPAddresses"].append(x)

        return PassiveDict

    def Active():
        print("Do active stuff")


print()
if args.run:
    RunDictionary = {}
    Main.BaseInformation["OrganisationName"] = args.run
    Run.Initialise()
    Run.OrganisationInformation()
    RunDictionary.update({"Passive":Run.Passive(Main.BaseInformation["OrganisationName"])})
    print(Main.InformationStockpile)

if args.settings:
    Settings.Menu()
print()
