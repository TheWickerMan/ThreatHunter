# ThreatHunter
```
usage: ThreatHunter.py [-h] [-run RUN] [-passive] [-settings]

----------ThreatHunter-Help-Page----------

optional arguments:
  -h, --help  show this help message and exit
  -run RUN    Enter The Target Organisation's Name.
  -passive    Ensures that only passive, non-direct communication to the target.
  -settings   Modify the application settings.
```

Dependencies:
```
pip install requests censys
```
#How to submit log entries
Logging.Log(Main.BaseInformation["LogFile"], "Level", "Message")
