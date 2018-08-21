import datetime

class Logging():
    def Log(File, Level, Message):
        with open(File, "a") as Log:
            Log.write("{} - {} - {}\n".format(datetime.datetime.now(), Level, Message))
