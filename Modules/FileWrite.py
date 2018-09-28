
from Modules.LoggingModule import Logging

class Main():
    BaseInformation = {"FileName":"Output"}
    def Write(LogFile, Filepath, Data):
        with open("{}/{}".format(Filepath, Main.BaseInformation["FileName"]), "a") as WriteFile:
            #Writes the list of domains and IP addresses to file.
            if Data["Domains/IPAddresses"]:
                WriteFile.write("\n Domains/IP Addresses: \n")
                for IP in Data["Domains/IPAddresses"]:
                    if IP == "Tool":
                        pass
                    else:
                        WriteFile.write("       {}\n".format(IP))
                Logging.Log(LogFile, "FileWrite", "INFO", "Writing domain data to \'{}\' file.".format(Filepath+Main.BaseInformation["FileName"]))

            #Writes the certificate items
            if Data["Certificates"]:
                WriteFile.write("\n Certificates: \n")
                for Key, Cert in Data["Certificates"].items():
                    if Key == "Tool":
                        pass
                    else:
                        WriteFile.write("   {}:{}\n".format(Key, Cert))

            #Formats and writes the IPv4 items
            if Data["IPv4"]:
                WriteFile.write("\n IPv4 + Services: \n")
                Counter = True
                for Key, Value in Data["IPv4"].items():
                    Header = "  IP/Domain"
                    DomainValues = ""
                    if Key == "Tool":
                        pass
                    else:
                        if Counter == True:
                            for x in Value.keys():
                                Header = "{}    {}".format(Header, x)
                            Counter = False
                            WriteFile.write(Header+"\n")
                        for x in Value.values():
                            DomainValues = "{}  {}".format(DomainValues, x)
                        WriteFile.write("   {}  {}\n".format(Key, DomainValues))
