import os, subprocess, shutil, socket, Configurations
from sys import version_info
from datetime import datetime
import re
import math
from SyslogNgAutomator import SyslogNgAutomator

class MyCnfAutomator(object):

    def __init__(self):
        print ""

        # Function to convert the memory size of the server into GB.

    @classmethod
    def convertSize(cls, size):
        if (size == 0):
            return '0B'
        i = int(math.floor(math.log(size, 1024)))
        p = math.pow(1024, i)
        s = round(size / p, 2)
        return s

    # Function to get the memory size of the server.
    @classmethod
    def getMemorySize(cls):
        meminfo = open('/proc/meminfo').read()
        matched = re.search(r'^MemTotal:\s+(\d+)', meminfo)
        if matched:
            mem_total_kB = int(matched.groups()[0])
            return cls.convertSize(mem_total_kB)

    # Function to print the passed dictionary
    @classmethod
    def displayParameterValues(cls, dictionary):
        if type(dictionary) is dict:
            for key in dictionary:
                if not re.search('Print', dictionary[key]) and not re.search('Aggre',
                                                                             dictionary[key]) and not re.search('UseG',
                                                                                                                dictionary[
                                                                                                                    key]):
                    print key + ":" + dictionary[key]
                else:
                    print dictionary[key]
            print "\n"
        else:
            for value in dictionary:
                print value
            print "\n"

    @classmethod
    def automate(cls, myCnfPath, parser, logger):
        valuesFoundInMyCnf = {}
        valuesNotFoundInSystemMyCnf = {}
        valuesNeedToBeModifiedInMyCnf = {}
        valuesThatGotModifiedInMyCnf = {}

        # Function to change the permissions of the my.cnf file, take a back-up and make changes to the file if required.
        def modifyMycnfFile(source, parser, logger):
            # Get Permissions on a File
            permissions = oct(os.stat(source).st_mode & 0777)

            # If the permissions donot allow to edit, make it editable
            if (permissions != 0755):
                subprocess.call(['chmod', '0755', source])

            # Search For the String Pattern
            memorySize = cls.getMemorySize()
            # memorySize = 64
            parseMyCnfFile(parser, memorySize, Configurations.mysqlVariableTuningValues, source, logger)

            # Reset the file permissions to the original value:
            if (permissions != 0755):
                subprocess.call(['chmod', permissions, source])

        # Function to parse the My.cnf file and update it's parameters if required.
        def parseMyCnfFile(parser, memorySize, mysqlVariableTuningValues, dirpathsource, logger):
            parser.read(dirpathsource)
            mysqldValues = dict(parser.items('mysqld'))
            tempdictionary = []

            # 1. Check if the values are present in the my.cnf file, get a list of values present and not present
            for parameter in mysqldValues:
                valuesFoundInMyCnf[parameter] = parser.get('mysqld', parameter)
                if parameter in mysqlVariableTuningValues:
                    # To check for the keys that are present in the dictionary
                    tempdictionary.append(parameter)

            for key in mysqlVariableTuningValues:
                if key not in tempdictionary:
                    keyValue = mysqlVariableTuningValues[key]
                    if (type(keyValue) is dict):
                        for childKey in keyValue:
                            if (0.8 <= int(childKey) / int(memorySize) <= 1):
                                valuesNotFoundInSystemMyCnf[key] = keyValue[childKey]
                    else:
                        valuesNotFoundInSystemMyCnf[key] = mysqlVariableTuningValues[key]

            # Compare the original values with the values found in the dictionary:
            for key in valuesFoundInMyCnf:
                if key in mysqlVariableTuningValues:
                    keyValue = mysqlVariableTuningValues[key]
                    if (type(keyValue) is dict):
                        for childKey in keyValue:
                            if (0.8 <= int(childKey) / int(memorySize) <= 1):
                                if keyValue[childKey] not in valuesFoundInMyCnf[key]:
                                    valuesNeedToBeModifiedInMyCnf[key] = valuesFoundInMyCnf[key]
                                    valuesThatGotModifiedInMyCnf[key] = keyValue[childKey]

                    else:
                        if keyValue not in valuesFoundInMyCnf[key]:
                            valuesNeedToBeModifiedInMyCnf[key] = valuesFoundInMyCnf[key]
                            valuesThatGotModifiedInMyCnf[key] = mysqlVariableTuningValues[key]

            logger.info("\nThese are the values in my.cnf that need to be modified: \n")
            print cls.displayParameterValues(valuesNeedToBeModifiedInMyCnf)

            logger.info("\n \nThe recommended values for the parameters: \n")
            print cls.displayParameterValues(valuesThatGotModifiedInMyCnf)

            logger.info("\n \nThese are values that were not found in my.cnf file: \n")
            print cls.displayParameterValues(valuesNotFoundInSystemMyCnf)

            proceedAnswer = SyslogNgAutomator().proceedAnswer()

            if proceedAnswer == 'yes' or proceedAnswer == 'YES':

                # Take a backup of the file
                shutil.copy2(dirpathsource, dirpathsource + '_backup_' + str(datetime.now()))

                # a. Modify the parameters with the values that are recommended. (valuesNeedToBeModified)
                for parameter in valuesNeedToBeModifiedInMyCnf:
                    if parameter in mysqlVariableTuningValues:
                        # Get and Replace the parameter value based on the memory
                        keyValue = mysqlVariableTuningValues[parameter]
                        if (type(keyValue) is dict):
                            for childKey in keyValue:
                                if (0.8 <= int(childKey) / int(memorySize) <= 1):
                                    parser.set('mysqld', parameter, keyValue[childKey])
                        else:
                            parser.set('mysqld', parameter, mysqlVariableTuningValues[parameter])

                # b. Append the values that were not found in my.cnf file. (valuesNotFoundInSystemMyCnf)
                for value in valuesNotFoundInSystemMyCnf:
                    keyValue = mysqlVariableTuningValues[value]
                    if (type(keyValue) is dict):
                        for childKey in keyValue:
                            if (0.8 <= int(childKey) / int(memorySize) <= 1):
                                parser.set('mysqld', value, keyValue[childKey])
                    else:
                        parser.set('mysqld', value, mysqlVariableTuningValues[value])

                # Writing our configuration file to 'example.ini'
                with open(dirpathsource, 'wb') as configfile:
                    parser.write(configfile)

                logger.info("\n\n\n****Important Message****\n Please restart \"mysql\" service, since my.cnf was updated \n *********************** \n")

            elif proceedAnswer == 'no' or proceedAnswer == 'NO':
                logger.info("The file was not modified.")

            errorCheck = False

            py3 = version_info[0] > 2

            if py3:
                proceedAnswer = input(
                    "\n \n Do you want to add the disaster recovery parameters to my.cnf file (yes/no): ")
            else:
                proceedAnswer = raw_input(
                    "\n \n Do you want to add the disaster recovery parameters to my.cnf file (yes/no): ")

            print ""

            if proceedAnswer == 'yes' or proceedAnswer == 'YES':
                if py3:
                    proceedAnswer = input("\n \n Is this the master node file (yes/no): ")
                else:
                    proceedAnswer = raw_input("\n \n Is this the master node file (yes/no): ")

                print ""

                # Modify the master my.cnf file:
                if proceedAnswer == 'yes' or proceedAnswer == 'YES':
                    if py3:
                        ipAddress = input("\n \n Enter the IpAddress of the master node: ")
                    else:
                        ipAddress = raw_input("\n \n Enter the IpAddress of the master node: ")
                    print ""

                    try:
                        # legal IP Address Check
                        socket.inet_aton(ipAddress)

                        Configurations.drReplicationParameters["bind-address"] = ipAddress
                        Configurations.drReplicationParameters["skip-name"] = "resolve"
                        Configurations.drReplicationParameters["server-id"] = "1"
                        Configurations.drReplicationParameters["auto-increment-increment"] = "1"
                        Configurations.drReplicationParameters["auto-increment-offset"] = "2"
                        Configurations.drReplicationParameters["transaction-isolation"] = "READ-UNCOMMITTED"
                        Configurations.drReplicationParameters["log_queries_not_using_indexes"] = "1"
                        Configurations.drReplicationParameters["log_bin"] = "/var/lib/mysql/mysql-bin.log"

                        # Check if the fields in drReplicationParameters is present in my.cnf, if so then update the parameters as per the dictionary

                        for drReplicationParameter in Configurations.drReplicationParameters:
                            if drReplicationParameter in mysqldValues:
                                # update the value in my.cnf
                                parser.set('mysqld', drReplicationParameter,
                                           Configurations.drReplicationParameters[drReplicationParameter])
                            else:
                                # Append the value in my.cnf
                                parser.set('mysqld', drReplicationParameter,
                                           Configurations.drReplicationParameters[drReplicationParameter])

                        with open(dirpathsource, 'wb') as configfile:
                            parser.write(configfile)

                        logger.info("Diaster Recovery Parameters added successfully to my.cnf \n \n")

                    except socket.error:
                        # Not legal
                        logger.warn("The Entered IP address is not valid, exiting the program.")
                        errorCheck = True

                elif proceedAnswer == 'no' or proceedAnswer == 'NO':

                    if py3:
                        proceedAnswer = input("\n \n Is this the Diaster Recovery node file (yes/no): ")
                    else:
                        proceedAnswer = raw_input("\n \n Is this the Diaster Recovery node file (yes/no): ")

                    print ""

                    # Modify the Diaster Recovery my.cnf file:
                    if proceedAnswer == 'yes' or proceedAnswer == 'YES':
                        if py3:
                            ipAddress = input("\n \n Enter the IpAddress of the Diaster Recovery node: ")
                        else:
                            ipAddress = raw_input("\n \n Enter the IpAddress of the Diaster Recovery node: ")
                        print ""

                        try:
                            # legal IP Address Check
                            socket.inet_aton(ipAddress)

                            Configurations.drReplicationParameters["bind-address"] = ipAddress
                            Configurations.drReplicationParameters["skip-name"] = "resolve"
                            Configurations.drReplicationParameters["server-id"] = "2"
                            Configurations.drReplicationParameters["auto-increment-increment"] = "2"
                            Configurations.drReplicationParameters["auto-increment-offset"] = "1"
                            Configurations.drReplicationParameters["slave_exec_mode"] = "IDEMPOTENT"
                            Configurations.drReplicationParameters[
                                "plugin-load"] = "thread_pool=thread_pool.so;tp_thread_state=thread_pool.so"

                            # Add the skip-external-locking, skip-character-set-client-handshake manually

                            # Check if the fields in drReplicationParameters is present in my.cnf, if so then update the parameters as per the dictionary

                            for drReplicationParameter in Configurations.drReplicationParameters:
                                if drReplicationParameter in mysqldValues:
                                    # update the value in my.cnf
                                    parser.set('mysqld', drReplicationParameter,
                                               Configurations.drReplicationParameters[drReplicationParameter])
                                else:
                                    # Append the value in my.cnf
                                    parser.set('mysqld', drReplicationParameter,
                                               Configurations.drReplicationParameters[drReplicationParameter])

                            with open(dirpathsource, 'wb') as configfile:
                                parser.write(configfile)

                            logger.info("Diaster Recovery Parameters added successfully to my.cnf \n \n")

                            logger.info("Important message: Please check if \"skip-external-locking\" and \"skip-character-set-client-handshake\" are present. \n" \
                                  "If they are present and commented, please uncomment them. If not, add them to the my.cnf file under [mysqld] \n \n")

                        except socket.error:
                            # Not legal
                            logger.info("The Entered IP address is not valid, exiting the program.")
                            errorCheck = True

                if errorCheck == False:
                    logger.info("\n\n\n****Important Message****\n Please restart \"mysql\" service, since my.cnf was updated \n *********************** \n")

            elif proceedAnswer == 'no' or proceedAnswer == 'NO':
                logger.info("The file was not modified with Diaster Recovery Parameters.")

        try:
            modifyMycnfFile(myCnfPath, parser, logger)
        except Exception as e:
            logger.error(" Error occured while processing my.cnf file: ")
            print e
            pass