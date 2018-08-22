import datetime

class Logging():
    def Log(File, Module, Level, Message):
        with open(File, "a") as Log:
            Log.write("{} - {} - {} - {}\n".format(datetime.datetime.now(), Module, Level, Message))
