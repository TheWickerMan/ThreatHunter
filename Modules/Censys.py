import json
import requests
import censys.ipv4
import censys.certificates

from Modules.LoggingModule import Logging

class Main():
    ConnectionInformation = {"UID":"", "Secret":"", "BaseURL":"", "API Rate Limit":"", "Web Rate Limit":""}
    ModuleSettings = "./Modules/ModuleSettings"
    GatheredInformation = {}

    def Initialise(LogFile, API_Keys):
        #Reads API keys from file
        with open(API_Keys) as API_Directory:
            LoadedAPI = json.load(API_Directory)
            Logging.Log(LogFile, "CENSYS", "INFO", "Loaded API keys")
        Main.ConnectionInformation["UID"] = LoadedAPI["Censys"]["UID"]
        Main.ConnectionInformation["Secret"] = LoadedAPI["Censys"]["Secret"]

        #Reads Module Settings
        with open(Main.ModuleSettings) as ModuleSettingsDirectory:
            LoadedSettings = json.load(ModuleSettingsDirectory)
            Logging.Log(LogFile, "CENSYS", "INFO", "{} - Loaded module settings".format(LoadedSettings))
        Main.ConnectionInformation["BaseURL"] = LoadedSettings["Censys"]["BaseURL"]
        Main.ConnectionInformation["API Rate Limit"] = LoadedSettings["Censys"]["API Rate Limit"]
        Main.ConnectionInformation["Web Rate Limit"] = LoadedSettings["Censys"]["Web Rate Limit"]

    def Run(LogFile, API_Keys, OrganisationName):
        Main.Initialise(LogFile, API_Keys)
        Logging.Log(LogFile, "CENSYS", "INFO", "Censys Initialisation Complete")
        CensysSearch = censys.ipv4.CensysIPv4(api_id=Main.ConnectionInformation["UID"], api_secret=Main.ConnectionInformation["Secret"])
        Logging.Log(LogFile, "CENSYS", "INFO", "Requesting IPv4 Addresses")
        counter = 0
        for IP in CensysSearch.search(OrganisationName):
            #Compiles a nested dictionary to store useful information.clear
            TemporaryDictionary = {IP["ip"]: {"Hosting Country":IP["location.country"], "Timezone":IP["location.timezone"], "Postcode":IP["location.postal_code"], "Protocols":IP["protocols"]}}
            Main.GatheredInformation.update(TemporaryDictionary)
            Logging.Log(LogFile, "CENSYS", "INFO", "Compiling {} information".format(IP))
            counter+=1
        Logging.Log(LogFile, "CENSYS", "DEBUG", "Identified {} IPv4 Addresses".format(counter))
        return Main.GatheredInformation
