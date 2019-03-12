import os
import subprocess, shutil
import xml
from datetime import datetime

import Configurations
from ApplicationContextAutomator import ApplicationContextAutomator
from PCParser import PCParser
from SyslogNgAutomator import SyslogNgAutomator

class ServerXmlAutomator(object):

    def __init__(self):
        print ""

    @classmethod
    def automate(cls, serverXmlPath, logger):
        print ""
        valuesNeedToBeModifiedInServerXml = []

        def modifyServerXmlFile(serverXmlPath, logger):
            # Get Permissions on a File
            permissions = oct(os.stat(serverXmlPath).st_mode & 0777)

            # If the permissions donot allow to edit, make it editable
            if (permissions != 0755):
                subprocess.call(['chmod', '0755', serverXmlPath])

            file = open(serverXmlPath, 'r')
            parser = PCParser()
            xmlTreeFile = xml.etree.ElementTree.parse(file, parser)
            root = xmlTreeFile.getroot()

            ApplicationContextAutomator().recursiveIter(root,valuesNeedToBeModifiedInServerXml,
                                                        Configurations.serverXmlTuningParameters,False)

            logger.info("values that need to be modified in Server.Xml: ")
            print valuesNeedToBeModifiedInServerXml

            proceedAnswer = SyslogNgAutomator().proceedAnswer()

            if proceedAnswer == 'yes' or proceedAnswer == 'YES':
                # Take a backup of the file
                shutil.copy2(serverXmlPath, serverXmlPath + '_backup_' + str(datetime.now()))
                ApplicationContextAutomator().recursiveIter(root, valuesNeedToBeModifiedInServerXml,
                                                            Configurations.serverXmlTuningParameters,True)
                xmlTreeFile.write(open(serverXmlPath, 'w'), "UTF-8")
                logger.info("Server.xml got modified.")
            else:
                logger.info("Server.xml was not modified.")

            # Reset the file permissions to the original value:
            if (permissions != 0755):
                subprocess.call(['chmod', permissions, serverXmlPath])

        try:
            modifyServerXmlFile(serverXmlPath, logger)
        except Exception as e:
            logger.error(" Error occured while processing server.xml file: ")
            print e
            pass