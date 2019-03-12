import os, shutil, subprocess, Configurations
import re
from datetime import datetime
from sys import version_info
from shutil import move
from os import remove, close
from tempfile import mkstemp
from MyCnfAutomator import MyCnfAutomator
from SyslogNgAutomator import SyslogNgAutomator

class StartupShAutomator(object):

    def __init__(self):
        print ""

    @classmethod
    def automate(cls, startupPath, logger):
        print ""
        valuesFoundInStartupSh = []
        valuesNotFoundInStartupSh = {}
        valuesNeedToBeModifiedInStartupSh = {}

        # Function To update the file after modifyting its contents:
        def replace(file_path, pattern, subst):
            # Create temp file
            fh, abs_path = mkstemp()
            with open(abs_path, 'w') as new_file:
                with open(file_path, 'r') as old_file:
                    for line in old_file:
                        new_file.write(line.replace(pattern, subst.lstrip()))
            close(fh)
            # Remove original file
            remove(file_path)
            # Move new file
            move(abs_path, file_path)

        # Function To Modify The Startup.sh File
        def modifyStartupFile(startupPath, logger):
            # Get Permissions on a File
            permissions = oct(os.stat(startupPath).st_mode & 0777)

            # If the permissions donot allow to edit, make it editable
            if (permissions != 0755):
                subprocess.call(['chmod', '0755', startupPath])

            file = open(startupPath, 'r')

            xmxWordIndex = 0
            xmsWordIndex = 0
            memorySize = MyCnfAutomator().getMemorySize()
            lineToReplace = ''
            finalLine = ''
            xLoggPath = ''
            proceedAnswer = ''

            for line in file:
                # If the line starts with export CATALINA_OPTS, then pickup the line
                if re.match('export CATALINA_OPTS=', line):
                    lineToReplace = line
                    words = line.split(' ')

                    # Split export and CATALINA_OPTS=" as separate words
                    catalinaIndex = [i for i, item in enumerate(words) if "CATALINA_OPTS" in item]
                    catalinaWord = words[tuple(catalinaIndex)[0]]
                    catalinaIndexSplit = catalinaWord.split('"')
                    words[tuple(catalinaIndex)[0]] = catalinaIndexSplit[1]
                    words.insert(tuple(catalinaIndex)[0], catalinaIndexSplit[0] + "\"")

                    # Get the values present in Startup.sh (valuesFoundInStartupSh)
                    for key in Configurations.startupTuningParameters:
                        keyValue = Configurations.startupTuningParameters[key]
                        if (type(keyValue) is dict):
                            for childKey in keyValue:
                                if (0.8 <= int(childKey) / int(memorySize) <= 1):
                                    startupWordIndex = [i for i, item in enumerate(words) if key in item]
                                    if startupWordIndex:
                                        valuesFoundInStartupSh.append(words[startupWordIndex[0]])
                                    else:
                                        valuesNotFoundInStartupSh[key] = keyValue[childKey]

                        else:

                            if not re.search('Print', keyValue) and not re.search('Aggre', keyValue) and not re.search(
                                    'UseG',
                                    keyValue):
                                startupWordIndex = [i for i, item in enumerate(words) if key in item]
                                if startupWordIndex:
                                    valuesFoundInStartupSh.append(words[startupWordIndex[0]])
                                else:
                                    valuesNotFoundInStartupSh[key] = keyValue

                            else:
                                startupWordIndex = [i for i, item in enumerate(words) if key in item]
                                if startupWordIndex:
                                    valuesFoundInStartupSh.append(words[startupWordIndex[0]])
                                else:
                                    valuesNotFoundInStartupSh[key] = keyValue

                    for key in Configurations.startupTuningParameters:
                        keyValue = Configurations.startupTuningParameters[key]
                        if (type(keyValue) is dict):
                            for childKey in keyValue:
                                if (0.8 <= int(childKey) / int(memorySize) <= 1):
                                    for word in valuesFoundInStartupSh:
                                        if re.search(key, word):
                                            if word != key + keyValue[childKey]:
                                                valuesNeedToBeModifiedInStartupSh[key] = keyValue[childKey]

                        else:
                            if not re.search('Print', keyValue) and not re.search('Aggre', keyValue) and not re.search(
                                    'UseG',
                                    keyValue):
                                for word in valuesFoundInStartupSh:
                                    if re.search(key, word):
                                        if word != key + keyValue:
                                            valuesNeedToBeModifiedInStartupSh[key] = keyValue
                            else:
                                for word in valuesFoundInStartupSh:
                                    if re.search(key, word):
                                        if word != keyValue:
                                            valuesNeedToBeModifiedInStartupSh[key] = keyValue

                    logger.info("\n \nThe values found in startup.sh: \n")
                    print MyCnfAutomator().displayParameterValues(valuesFoundInStartupSh)

                    logger.info("\nThese are the values in startup that need to be modified: \n")
                    print MyCnfAutomator().displayParameterValues(valuesNeedToBeModifiedInStartupSh)

                    logger.info("\n \nThese are values that were not found in startup.sh file and will be added to the file: \n")
                    print MyCnfAutomator().displayParameterValues(valuesNotFoundInStartupSh)

                    proceedAnswer = SyslogNgAutomator().proceedAnswer()

                    if proceedAnswer == 'yes' or proceedAnswer == 'YES':

                        # Take a backup of the file
                        shutil.copy2(startupPath, startupPath + '_backup_' + str(datetime.now()))

                        # Replace the values in startup.sh that need to be modified:
                        for key in valuesNeedToBeModifiedInStartupSh:
                            keyValue = valuesNeedToBeModifiedInStartupSh[key]
                            wordIndex = [i for i, item in enumerate(words) if key in item]
                            if wordIndex:
                                if not re.search('Print', keyValue) and not re.search('Aggre',
                                                                                      keyValue) and not re.search(
                                        'UseG', keyValue):
                                    words[wordIndex[0]] = key + valuesNeedToBeModifiedInStartupSh[key]
                                else:
                                    words[wordIndex[0]] = valuesNeedToBeModifiedInStartupSh[key]

                        # Get the index of the first word for the change to be made
                        for word in words:
                            if re.search('Xmx', word):
                                xmxWordIndex = words.index(word)
                            if re.search('Xms', word):
                                xmsWordIndex = words.index(word)
                            if xmxWordIndex != 0 and xmsWordIndex != 0:
                                break

                        # Replace the parameters not found in the list:
                        wordIndex = xmxWordIndex if xmxWordIndex > xmsWordIndex else xmsWordIndex

                        if int(childKey) < 128 and "UseCompressedOops" not in line:
                            words.insert(wordIndex + 1, "-XX:+UseCompressedOops")

                        if "-Xloggc" not in line:
                            py3 = version_info[0] > 2

                            if py3:
                                xLoggPath = input("Enter the path for the gc logger: ")
                            else:
                                xLoggPath = raw_input("Enter the path for the gc logger: ")

                        if xLoggPath != '':
                            words.insert(wordIndex + 1, "-Xloggc:" + xLoggPath)

                        # Append the values not found in startup.sh into the file
                        for key in valuesNotFoundInStartupSh:
                            keyValue = valuesNotFoundInStartupSh[key]
                            if not re.search('Print', keyValue) and not re.search('Aggre', keyValue) and not re.search(
                                    'UseG',
                                    keyValue):
                                words.insert(wordIndex + 1, key + keyValue)
                            else:
                                words.insert(wordIndex + 1, keyValue)

                    elif proceedAnswer == 'no' or proceedAnswer == 'NO':
                        logger.info("No changes were made to the Startup.sh file.")

            file.close()

            if proceedAnswer == 'yes' or proceedAnswer == 'YES':
                for word in words:
                    finalLine = finalLine + ' ' + word

                if (lineToReplace != ''):
                    replace(startupPath, lineToReplace, finalLine)

            # Reset the file permissions to the original value:
            if (permissions != 0755):
                subprocess.call(['chmod', permissions, startupPath])
        try:
            modifyStartupFile(startupPath, logger)
        except Exception as e:
            logger.error(" Error occured while processing Startup.sh file: ")
            print e
            pass
