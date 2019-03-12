import fileinput
import os, subprocess, shutil, re
from datetime import datetime

import Configurations
from SyslogNgAutomator import SyslogNgAutomator


class ConfAutomator(object):
    def __init__(self):
        print ""


    @classmethod
    def automate(cls, ninentynProcPath, logger, tuningParameters, regexPassed, delimiter):

        ninentynProcParametersFound = []
        ninentynProcParametersNotFound = []
        ninentynProcParametersToBeModified = []

        def representsInt(s):
            try:
                int(s)
                return True
            except ValueError:
                return False

        def modify90NProc(ninentynProcPath, logger,  tuningParameters, regexPassed, delimiter):
            # # # Get Permissions on a File
            # permissions = oct(os.stat(ninentynProcPath).st_mode & 0777)
            #
            # # If the permissions donot allow to edit, make it editable
            # if (permissions != 0755):
            #     subprocess.call(['chmod', '0755', ninentynProcPath])

            # Take a backup of the file
            # shutil.copy2(ninentynProcPath, ninentynProcPath + '_backup_' + str(datetime.now()))

            file = fileinput.input(ninentynProcPath, inplace=True, backup='.bak')
            lineNeedsReplacement = False
            parameterToUpdate = ""
            valueFoundTemp = 0
            indexCount = 0

            if delimiter == "equal":
                delimiter = " = "
            else:
                delimiter = " "

            for line in file:
                indexCount = indexCount + 1
                for searchParameter in tuningParameters:
                    valueFound = re.search(searchParameter+ regexPassed, line)
                    if valueFound and representsInt(valueFound.group(1)):
                        ninentynProcParametersFound.append(searchParameter)
                        if valueFound.group(1) != tuningParameters[searchParameter]:
                            ninentynProcParametersToBeModified.append(searchParameter)
                            lineNeedsReplacement = True
                            parameterToUpdate = searchParameter
                            valueFoundTemp = valueFound.group(1)
                            logger.info("value found: " + valueFoundTemp)

                if lineNeedsReplacement is True:
                    logger.info(valueFoundTemp)
                    logger.info(parameterToUpdate)
                    line = line.replace(parameterToUpdate + delimiter + valueFoundTemp, parameterToUpdate + delimiter
                                        + tuningParameters[parameterToUpdate])
                    print line
                    lineNeedsReplacement = False
                else:
                    print line.rstrip()

            for parameter in tuningParameters:
                if parameter not in ninentynProcParametersFound:
                    ninentynProcParametersNotFound.append(parameter)

            linesToAdd = ""

            file.close()

            if len(ninentynProcParametersNotFound) > 0:
                for parameter in ninentynProcParametersNotFound:
                    if parameter in Configurations.softHardTuningParameters:
                        linesToAdd = linesToAdd + "\n* " + parameter + delimiter + tuningParameters[
                        parameter]
                    else:
                        linesToAdd = linesToAdd + "\n" + parameter + delimiter + tuningParameters[
                            parameter]


                file = fileinput.input(ninentynProcPath, inplace=True, backup='.bak')

                for line in file:
                    if file.filelineno() == indexCount:
                        line = line.replace(line, line + linesToAdd)
                        print line
                    else:
                        print line.strip()

                file.close()

            logger.info("Values found: ")
            print ninentynProcParametersFound
            logger.info("Values to be modified: ")
            print ninentynProcParametersToBeModified
            logger.info("Values not found and to be added: ")
            print ninentynProcParametersNotFound

            logger.info("90-nproc.conf got modified.")

            # # Reset the file permissions to the original value:
            # if (permissions != 0755):
            #     subprocess.call(['chmod', permissions, ninentynProcPath])

        try:
            modify90NProc(ninentynProcPath, logger, tuningParameters, regexPassed, delimiter)
        except Exception as e:
            logger.error(" Error occured while processing 90-nproc.conf file: ")
            print e
            pass