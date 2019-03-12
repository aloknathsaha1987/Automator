import os, subprocess, shutil
import re
from datetime import datetime
import Configurations, fileinput
from sys import version_info

class SyslogNgAutomator(object):

    def __init__(self):
        print ""


    @classmethod
    def proceedAnswer(cls):
        py3 = version_info[0] > 2

        if py3:
            proceedAnswer = input("\n \n Do you wish to proceed (yes/no): ")
        else:
            proceedAnswer = raw_input("\n \n Do you wish to proceed (yes/no): ")

        return proceedAnswer

    @classmethod
    def automate(cls, syslogNgPath, logger):
        print ""
        valuesFoundInSyslogNg = []
        valuesNotFoundInSyslogNg = []
        valuesNeedToBeModifiedInSyslogNg = {}


        # Function To Modify The syslog-ng.conf File
        def modifySyslogNgFile(syslogNgPath, logger):
            # Get Permissions on a File
            permissions = oct(os.stat(syslogNgPath).st_mode & 0777)

            # If the permissions donot allow to edit, make it editable
            if (permissions != 0755):
                subprocess.call(['chmod', '0755', syslogNgPath])

            # Take a backup of the file
            shutil.copy2(syslogNgPath, syslogNgPath + '_backup_' + str(datetime.now()))

            lineNeedsReplacement = False
            keyReference = ""
            indexOfLine = 0
            file = fileinput.input(syslogNgPath, inplace=True, backup='.bak')

            for line in file:
                indexSearch = re.search('\s?'+"options"+'\s?\{', line)
                if indexSearch:
                    indexOfLine = file.filelineno()
                for key in sorted(Configurations.syslogNgTuningParameters, key=lambda x: len(Configurations.syslogNgTuningParameters[x])):
                    value = re.search('\s+'+key+'\s?\((.+?)\)', line)
                    if value and not valuesNotFoundInSyslogNg.__contains__(key):
                     # match found, get the value and compare, also store the values that have been found
                        valuesFoundInSyslogNg.append(key)

                        if value.group(1) != Configurations.syslogNgTuningParameters[key]:
                            lineNeedsReplacement = True
                            keyReference = key
                            valuesNeedToBeModifiedInSyslogNg[key] = Configurations.syslogNgTuningParameters[key]
                        break

                # Append the values that need to be modified
                if lineNeedsReplacement is True:
                    line = line.replace(line, "\t" + keyReference + "(" + Configurations.syslogNgTuningParameters[keyReference] + ");")
                    print line
                    lineNeedsReplacement = False
                else:
                    print line.rstrip()

            file.close()

            # Get the values that were not found
            for value in Configurations.syslogNgTuningParameters:
                if not valuesFoundInSyslogNg.__contains__(value):
                    valuesNotFoundInSyslogNg.append(value)

            logger.info("Values found: ")
            print valuesFoundInSyslogNg
            logger.info("Values to be modified: ")
            print valuesNeedToBeModifiedInSyslogNg
            logger.info("Values not found and to be added: ")
            print valuesNotFoundInSyslogNg

            # Append the values not found in the syslog file inside the options tab
            file = fileinput.input(syslogNgPath, inplace=True, backup='.bak')
            linesToAdd = ""

            for valueNotFound in valuesNotFoundInSyslogNg:
                linesToAdd += "\n\t" + valueNotFound + "(" + Configurations.syslogNgTuningParameters[
                    valueNotFound] + ");"

            for line in file:
                if file.filelineno() == indexOfLine:
                    line = line.replace(line, line + linesToAdd)
                    print line
                else:
                    print line.rstrip()

            file.close()
            logger.info("Syslog-ng got modified.")

            # Reset the file permissions to the original value:
            if (permissions != 0755):
                subprocess.call(['chmod', permissions, syslogNgPath])

        try:
            modifySyslogNgFile(syslogNgPath, logger)
        except Exception as e:
            logger.error(" Error occured while processing syslog-ng.conf file: ")
            print e
            pass
