import argparse
import configparser
import logging
import os
import random
import sys
import threading
import time
import time
from datetime import datetime

import requests
from pyfiglet import Figlet

DOMAINS_MAX = 5000
THREADS_MAX = 150


def Average(lst):
    return sum(lst) / len(lst)


class StressApiTasker(threading.Thread):
    def __init__(self, threadID, thread_name, api_url, api_token, domain_list, domains_amount, timeout_in_sec):
        threading.Thread.__init__(self,)
        self.threadID = threadID
        self.domains_amount = domains_amount
        self.thread_name = thread_name
        self.api_url = api_url
        self.api_token = api_token
        self.domain_list = self.get_random_domain_list(domain_list)
        self.success_requests = 0
        self.error_requests = 0
        self.time_for_each_request = []
        self.timeout_in_sec = timeout_in_sec

    def get_random_domain_list(self, domain_list):
        """
        return specific amount of domains from the list of domains
        Each domain selected randomly from the list, each one can be chosen more then once
        """
        return random.choices(domain_list, k=self.domains_amount)

    def send_api_request_with_domain(self, domain_name):
        """
        Send Api Request with specific domain

        Making request to specific domain name

        Parameters
        ----------
        domain_name : str
            domain name
        """

        headers = {'Authorization': '{}'.format(self.api_token)}
        try:
            api_response = requests.get(self.api_url + domain_name, headers=headers)
            logging.debug(api_response.json())
            if api_response.status_code == 200:
                self.success_requests = self.success_requests + 1
            else:
                self.error_requests = self.error_requests - 1

        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)
        return api_response.elapsed.total_seconds()

    def stress_load_requests(self):
        """
        This function is thread Run process , all threads are controlled by the thread
        poll so while true have a return back from timeout of thread
        """
        while True:
            self.time_for_each_request.append(self.send_api_request_with_domain(random.choice(self.domain_list)))


    def run(self):
        logging.debug(f"Starting {self.thread_name}")
        self.stress_load_requests()
        logging.debug(f"Exiting {self.thread_name}")


#Read data from file
def get_domains_list(domain_list_file_path):
    domain_list = []
    with open(domain_list_file_path) as file:
        for line in file:
            if (not line.startswith((".", '/'))) and line.endswith((".", '/')) :
                domain_list.append(line.rstrip())
    return domain_list


#Parser Config File
def get_api_config_data(config_file_path):
    """
    Parsing Config file to get configuration about the API we testing
    url = api url
    Authorization = token for api request
    """

    parser_data = {}
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file_path)

    # Read Config File Data
    for section in ['API_CONF']:
        logging.debug('%s section exists: %s' % (section, config_parser.has_section(section)))
        for candidate in ['url', 'Authorization']:
            if config_parser.has_option(section, candidate) is False:
                logging.critical(f"There is no section in Config_Api of ** {candidate} ** ,"
                                 f" please look at the example file and add it to try again !")
                sys.exit(100)
            logging.debug('%s.%-12s  : %s' % (section, candidate, config_parser.has_option(section, candidate)))
            parser_data[candidate] = config_parser.get(section, candidate)
    logging.debug(parser_data)

    # Validated Api URL Connection
    headers = {'Authorization': '{}'.format(parser_data['Authorization'])}
    try:
        requests.get(parser_data['url'], headers=headers)
        logger.info("URL is valid and exists on the internet")
    except requests.ConnectionError as exception:
        logger.critical(f"URL is not valid cant continue {exception} ")

    # Print Config File Data
    logging.info("Read Data from Config file Successfully !")
    for k, v in parser_data.items():
        print(k + ":" + v)

    return parser_data


def test_summarize(stress_threads):
    """
    Function get all Threads objects and summarize all data

    Each Tread is an StressApiTasker Object that contains all the info about the thread process.

    Parameters
    ----------
    stress_threads : str
        stress_threads - is a list that contains all threads objects, Each thread is StressApiTasker
        that contains all data from each thread that rand
    """
    # Combine all data from threads
    requests_times_from_all_requests = []
    total_error_requests = 0
    total_success_requests = 0

    for thread in stress_threads:
        # Combine all recorded times
        requests_times_from_all_requests = requests_times_from_all_requests + thread.time_for_each_request

        # Counting all success requests from all threads
        total_success_requests = total_success_requests + thread.success_requests

        # Counting all error requests from all threads
        total_error_requests = total_error_requests + thread.error_requests

        # Debug Output
        logger.debug(f"Thread name {thread.thread_name}, Ran {total_success_requests + total_error_requests} requests "
                     f"Thread max Time request {max(requests_times_from_all_requests)}")

    total_requests = total_success_requests + total_error_requests

    logger.info(f"Avg time for one request {Average(requests_times_from_all_requests)} ms")
    logger.info(f"Requests in Total - {total_requests}")
    logger.info(f"Error Rate is - {(int(total_error_requests / total_requests))}%")
    logger.info(f"Max Time for one Request {(max(requests_times_from_all_requests))}")
    logger.info(f"Min Time for one Request {min(requests_times_from_all_requests)}")
    logger.info("All threads successfully closed")


def main_func(config_file, domain_list_file_path, threads_amount, domains_amount, timeout):
    """
    Main function
    Creating Thread Poll tasker , each Thread is an object that runs independently,
    gathering all information about Api config and all the other parameters
    """
    start_time = time.time()
    stress_threads = []
    pill2kill = threading.Event()
    config_data = get_api_config_data(config_file)
    domain_list = get_domains_list(domain_list_file_path)
    logger.info(f"Starting test with the following params config file path: {config_file}"
                f"domain list file: {domain_list_file_path} threads amount:{threads_amount} timeout:{timeout} ")
    try:
        # Creating Threads jobs with Stress_api_tasker Class
        for thread_id in range(0, threads_amount):
            Tasker_thread = StressApiTasker(thread_name=f"Tasker_{str(thread_id)}", threadID=thread_id,
                                            api_url=config_data['url'], api_token=config_data['Authorization'],
                                            timeout_in_sec=timeout, domains_amount=domains_amount,
                                            domain_list=domain_list)
            stress_threads.append(Tasker_thread)
            thread_id += 1

        # Running Threads
        for thread in stress_threads:
            try:
                thread.daemon = True
                thread.start()
            except Exception as err:
                logger.exception(f"Error Starting the Thread {err}")
        logger.info(f"Total Active threads are {threading.activeCount() - 1}")

        # Wait all threads to finish in timeout by user
        for thread in stress_threads:
            thread.join(timeout=int(timeout/threads_amount))


        # Print test outputs
        logger.info(f"Total in Time {int(time.time() - start_time)} seconds")
        test_summarize(stress_threads)

    except KeyboardInterrupt:
        # join(0) is sending signal to all the threads to finish
        for thread in stress_threads:
            thread.join(0)
        logger.info("Reason: timeout/ KeyboardInterrupt")
        logger.info(f"Total in Time {int(time.time() - start_time)} seconds")
        test_summarize(stress_threads)
    pass


def check_input_args(input_args):
    # Check if config file is exits
    if not os.path.isfile(input_args.config_file):
        raise argparse.ArgumentTypeError(f"config file -  {input_args.config_file} path to file is not exits!"
                                         f" Please provide valid config file path")

    # Check if domain list file is exits
    if not os.path.isfile(input_args.domain_list_file_path):
        raise argparse.ArgumentTypeError(f"{input_args.domain_list_file_path} is not exits! "
                                         f"Please provide valid domain list file path ")

    # Valid timeout is positive
    if input_args.timeout < 0:
        raise argparse.ArgumentTypeError(f"timeout {input_args.timeout} is not positive ( bigger then 0 ) ")

    # Valid threads is positive
    if not 0 < input_args.threads_amount < THREADS_MAX:
        raise argparse.ArgumentTypeError(f"threads_amount {input_args.threads_amount}is not positive"
                                         f"( bigger then 0 ) or bigger the system can get {THREADS_MAX}")

    # Domains amount should be more then 0 and less then DOMAINS_MAX
    if not 0 < input_args.domains_amount <= DOMAINS_MAX:
        raise argparse.ArgumentTypeError(f"domains_amount {input_args.domains_amount}"
                                         f"is not positive ( bigger then 0 ) or bigger then {DOMAINS_MAX}")


if __name__ == "__main__":

    # Custom Text At start
    f = Figlet(font='slant')
    print(f.renderText('Stress API - cli'))

    # Logger Init , create logging formatter
    logFormatter = logging.Formatter(fmt='%(levelname)s :: %(message)s')
    # create logger
    logger = logging.getLogger()
    # create console handler
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    # Add console handler to logger
    timestr = time.strftime("%Y_%m_%d_%H_%M_%S")
    logger.addHandler(consoleHandler)
    #######

    parser = argparse.ArgumentParser(description='Stress API test')

    parser.add_argument("--config_file",
                        dest='config_file',
                        action='store', default='api_config.ini',
                        help='Please provide Config ini file for api connection'
                             'Example can be found in project folder [ api_config.ini ]')

    parser.add_argument("--domain_list_file_path",
                        dest='domain_list_file_path',
                        action='store', default='domains_url.txt',
                        help='Please provide domain Files Path [ domains_url.txt ] ')
    # CR: What will happen is the domain list is not good + make sure we have maximum of 5000 domains

    parser.add_argument("--threads",
                        dest='threads_amount',
                        action='store', default=1, type=int,
                        help='Number Of threads to run in parallel')
    # what will happen if too much threads is there any limitation
    parser.add_argument("--domains",
                        dest='domains_amount',
                        action='store', default=1, type=int,
                        help='Number Of Domains to run send request from')

    parser.add_argument("--timeout",
                        dest='timeout',
                        action='store', default=1, type=int,
                        help='timeout in seconds value ([seconds])')

    parser.add_argument("--use_docker",
                        dest='timeout',
                        action='store_true',
                        help='Run test with dockers [ True when flag is written ]Not implemented yet :) ')

    parser.add_argument("--log_file",
                        dest='log_file',
                        action='store_true',
                        help='Define if you want log file , saves in dir you started the cli')

    parser.add_argument("--debug_mode",
                        dest='debug',
                        action='store_true',
                        help='Change logger to level of Debug to get output from functions')

    input_args = parser.parse_args()
    if len(sys.argv) == 1:
        # display help message when no args are passed.
        parser.print_help()
        sys.exit(1)

    # Change logger level depends on debug mode
    if input_args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Add Log file
    if input_args.log_file:
        log_file_name = f'logs_{timestr}_DEBUG.log'
        logger.info(f"Log File Crated ֿ{log_file_name}  ")
        if input_args.debug:
            fh = logging.FileHandler(f'logs_{timestr}_DEBUG.log')
            fh.setLevel(logging.DEBUG)
        else:
            fh = logging.FileHandler(f'logs_{timestr}_INFO.log')
            fh.setLevel(logging.INFO)
        logger.addHandler(fh)

    # Validated input arguments
    check_input_args(input_args)

    main_func(config_file=input_args.config_file, domain_list_file_path=input_args.domain_list_file_path,
              domains_amount=input_args.domains_amount, threads_amount=int(input_args.threads_amount),
              timeout=int(input_args.timeout))
    sys.exit(0)
