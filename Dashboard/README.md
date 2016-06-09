# Web Dashboard

## Step 1 Log Parser
The log parser parses through all the Neutu logs produced and extracts metrics. It produces a JSON file.

**Required**
* Python 2.7 

It expects that all of your log files to be produced by NeuTu. The directory structure should look like this

    neutu-logs/
        user1/
            log.txt
            log.txt.1
        user2/
            log.txt

NeutuLogParser.py

    usage: NeutuLogParser.py [-h] [--log-directory DIRECTORY] [--output OUTPUT-FILE]

    Parse Neutu Logs for Progress Data
    
    optional arguments:
      -h, --help            show this help message and exit
      --log-directory DIRECTORY
                            Directory that contains log files
      --output OUTPUT-FILE  Filename for output Default: neutu.json
      

**Example:**

    python NeutuLogParser.py --log-directory /neutu-logs --output /path/to/save/neutu.json
    
_TODO_ Output file structure

    
## Step 2 Load Data To DVID

The next step is to load the JSON file created by NeutuLogParser into DVID.

**Required**

* Python 2.7
* [libdvid-cpp](https://github.com/janelia-flyem/libdvid-cpp)

DVIDLoad.py

    usage: DVIDLoad.py [-h] [--insert] [--uuid UUID] [--dvid DVID] [--key-name KEY_NAME] [--key-value-store KEY_VALUE_STORE] [--input INPUT]

    optional arguments:
      -h, --help            show this help message and exit
      --insert              Flag, loads to DVID if set
      --uuid UUID           Which uuid to use in DVID
      --dvid DVID           Which DVID server to use
      --key-name KEY_NAME   Name of key to store data under in DVID
      --key-value-store KEY_VALUE_STORE
                            Name of keyvalue data instance to put key-values under
      --input INPUT         Path to input JSON

**Example**

    /python DVIDLoad.py --uuid abcde --dvid emdata5.janelia.org  --key-name dashboard --key-value-store external_dashboard --input neutu.json --insert

