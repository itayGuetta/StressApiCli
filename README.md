

```
   _____ __                         ___    ____  ____                 ___ 
  / ___// /_________  __________   /   |  / __ \/  _/           _____/ (_)
  \__ \/ __/ ___/ _ \/ ___/ ___/  / /| | / /_/ // /   ______   / ___/ / / 
 ___/ / /_/ /  /  __(__  |__  )  / ___ |/ ____// /   /_____/  / /__/ / /  
/____/\__/_/   \___/____/____/  /_/  |_/_/   /___/            \___/_/_/   
                                                                          



```


# Stress Api Cli

Cli tool to simulate stress on server Api by multiplying different requests to the server in "parallel" 

## Description

Create CLI tool to simulate stress on our Reputation service using

## Getting Started




### Installing

1. Activate Virtual Env python  On Unix or MacOS, using the csh 
    + `$ source /path/to/venv/bin/activate.csh`
2. Install with [`pip`](https://pypi.org/project/stronghold/)
    + `$ pip3 install -r ./requirements.txt`


### Executing program

* for Example 
```
python3 stress_cli.py --config_file api_config.ini --threads 10  --domains 5000  --domain_list_file_path domains_url.txt  --timeout 10 
```
* Consol Example Output : 

```
URL is valid and exists on the internet
Read Data from Config file Successfully !
Starting test with the following params config file path: api_config.inidomain list file: domains_url.txt threads amount:2 timeout:10 
Total Active threads are 3
Reason: timeout/ KeyboardInterrupt
Total in Time 11 seconds
Avg time for one request 0.40965858 ms
Requests in Total - 50
Error Rate is - 0%
Max Time for one Request 0.436576
Min Time for one Request 0.383879
All threads successfully closed
```




Extra Args Examples: 

1. Log_file - To add log life please add --log_file parmarter 

2. Debug Mode - This argument ( --debug_mode )  will trigger logger level to debug mode and print to console important data ( also if enabled , will also save to log file ) 

## Help

Any advise for common problems or issues.
```

usage: stress_cli.py [-h] [--config_file CONFIG_FILE] [--domain_list_file_path DOMAIN_LIST_FILE_PATH] [--threads THREADS_AMOUNT] [--domains DOMAINS_AMOUNT] [--timeout TIMEOUT] [--use_docker] [--log_file]
                     [--debug_mode]

Stress API test

optional arguments:
  -h, --help            show this help message and exit
  --config_file CONFIG_FILE
                        Please provide Config ini file for api connectionExample can be found in project folder [ api_config.ini ]
  --domain_list_file_path DOMAIN_LIST_FILE_PATH
                        Please provide domain Files Path [ domains_url.txt ]
  --threads THREADS_AMOUNT
                        Number Of threads to run in parallel
  --domains DOMAINS_AMOUNT
                        Number Of Domains to run send request from
  --timeout TIMEOUT     timeout in seconds value ([seconds])
  --use_docker          Run test with dockers [ True when flag is written ]Not implemented yet :)
  --log_file            Define if you want log file , saves in dir you started the cli
  --debug_mode          Change logger to level of Debug to get output from functions

```

## Authors

Contributors names and contact info

ex.Itay Guetta  
