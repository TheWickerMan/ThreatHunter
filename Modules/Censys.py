import json
import requests
import censys.ipv4
import censys.certificates

from Modules.LoggingModule import Logging

class Main():
    ConnectionInformation = {"UID":"", "Secret":"", "BaseURL":"", "API Rate Limit":"", "Web Rate Limit":""}
    ModuleSettings = "./Modules/ModuleSettings"
    GatheredInformation = {"IPv4":{"Tool":"Censys"},"Certificates":{"Tool":"Censys"}}

    def Initialise(LogFile, API_Keys):
        #Reads API keys from file
        with open(API_Keys) as API_Directory:
            LoadedAPI = json.load(API_Directory)
            Logging.Log(LogFile, "CENSYS", "INFO", "Loaded API keys")
        if LoadedAPI["Censys"]["UID"] == "" or LoadedAPI["Censys"]["Secret"] == "":
            Logging.Log(LogFile, "CENSYS", "ERROR", "No Censys keys provided. Returning to main application.")
            return False
        Main.ConnectionInformation["UID"] = LoadedAPI["Censys"]["UID"]
        Main.ConnectionInformation["Secret"] = LoadedAPI["Censys"]["Secret"]

        #Reads Module Settings
        with open(Main.ModuleSettings) as ModuleSettingsDirectory:
            LoadedSettings = json.load(ModuleSettingsDirectory)
            Logging.Log(LogFile, "CENSYS", "INFO", "{} - Loaded module settings".format(LoadedSettings))
        Main.ConnectionInformation["BaseURL"] = LoadedSettings["Censys"]["BaseURL"]
        Main.ConnectionInformation["API Rate Limit"] = LoadedSettings["Censys"]["API Rate Limit"]
        Main.ConnectionInformation["Web Rate Limit"] = LoadedSettings["Censys"]["Web Rate Limit"]
        return True

    def Run(LogFile, API_Keys, OrganisationName):

        Result = Main.Initialise(LogFile, API_Keys)
        if Result == True:
            Logging.Log(LogFile, "CENSYS", "INFO", "Censys Initialisation Complete")
            CensysSearch = censys.ipv4.CensysIPv4(api_id=Main.ConnectionInformation["UID"], api_secret=Main.ConnectionInformation["Secret"])
            Logging.Log(LogFile, "CENSYS", "INFO", "Requesting IPv4 Addresses")
            counter = 0
            try:
                for IP in CensysSearch.search(OrganisationName):
                    #Compiles a nested dictionary to store useful information.clear
                    TemporaryDictionary = {IP["ip"]:{}}
                    try:
                        TemporaryDictionary[IP["ip"]]["Hosting Country"] = IP["location.country"]
                    except KeyError:
                        print(KeyError)
                        continue

                    try:
                        if IP["location.timezone"]:
                            TemporaryDictionary[IP["ip"]]["Timezone"] = IP["location.timezone"]
                    except KeyError:
                        print(KeyError)
                        continue
                    try:
                        if IP["location.postal_code"]:
                            TemporaryDictionary[IP["ip"]]["Postcode"] = IP["location.postal_code"]
                    except KeyError:
                        print(KeyError)
                        continue
                    try:
                        if IP["protocols"]:
                            TemporaryDictionary[IP["ip"]]["Protocols"] = IP["protocols"]
                    except KeyError:
                        print(KeyError)
                        continue
                    Main.GatheredInformation["IPv4"].update(TemporaryDictionary)
                    Logging.Log(LogFile, "CENSYS", "INFO", "Compiling {} information".format(IP))
                    counter+=1
            except Exception as CensysError:
                if "upgrade your Censys account" in CensysError:
                    print("     Maximum depth search reached with account provided.")
                    Logging.Log(LogFile, "CENSYS", "INFO", "Maximum depth has been reached while searching the target using the API details provided.")
                pass


            Logging.Log(LogFile, "CENSYS", "DEBUG", "Identified {} IPv4 Addresses".format(counter))

            Logging.Log(LogFile, "CENSYS", "INFO", "Requesting Certificate Information")
            try:
                CensysCerts = censys.certificates.CensysCertificates(api_id=Main.ConnectionInformation["UID"], api_secret=Main.ConnectionInformation["Secret"])
            except Exception as CensysError:
                if "upgrade your Censys account" in str(CensysError):
                    print("     Maximum depth search reached with account provided.")
                    Logging.Log(LogFile, "CENSYS", "INFO", "Maximum depth has been reached while searching the target using the API details provided.")
                pass

            try:
                for Cert in CensysCerts.search(OrganisationName):
                    try:
                        TemporaryDictionary = {Cert["parsed.subject_dn"]:Cert["parsed.fingerprint_sha256"]}
                    except KeyError:
                        continue
                    Main.GatheredInformation["Certificates"].update(TemporaryDictionary)
            except Exception as CensysError:
                if "upgrade your Censys account" in str(CensysError):
                    print("     Maximum depth search reached with account provided.")
                    Logging.Log(LogFile, "CENSYS", "INFO", "Maximum depth has been reached while searching the target using the API details provided.")
                pass

            return Main.GatheredInformation
        else:
            return False
