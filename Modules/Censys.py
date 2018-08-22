import json

from Modules.LoggingModule import Logging

class Main():
    ConnectionInformation = {"UID":"", "Secret":"", "BaseURL":"", "API Rate Limit":"", "Web Rate Limit":""}
    ModuleSettings = "./Modules/ModuleSettings"

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

    def Run(LogFile, API_Keys):
        Main.Initialise(LogFile, API_Keys)
        print(Main.ConnectionInformation)
