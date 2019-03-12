import os
import subprocess
import xml, shutil
from datetime import datetime

import Configurations
from PCParser import PCParser
from SyslogNgAutomator import SyslogNgAutomator


class HibernateAutomator(object):

    def __init__(self):
        print ""

    @classmethod
    def findParameters(cls, root, valuesFound, tuningparameters):
        if root.tag in tuningparameters:
            if bool(root.attrib):
                for attrib in root.attrib:
                    if root.attrib[attrib] in tuningparameters[root.tag][attrib]:
                        if root.tag not in valuesFound:
                            tempDict = {}
                            tempDict[attrib] = [root.attrib[attrib]]
                            valuesFound[root.tag] = tempDict
                        else:
                            valuesFound[root.tag][attrib].append(root.attrib[attrib])


    @classmethod
    def recursiveIter(cls, root, valuesFound, tuningparameters):
        if len(root):
            cls.findParameters(root, valuesFound, tuningparameters)
            for root in root:
                cls.recursiveIter(root, valuesFound, tuningparameters)
        else:
            cls.findParameters(root, valuesFound, tuningparameters)

    @classmethod
    def automate(cls, hibernatePath, logger):
        valuesFound = {}
        valuesNotFound = {}
        def modifyHibernateFile(hibernatePath, logger):
            # # Get Permissions on a File
            permissions = oct(os.stat(hibernatePath).st_mode & 0777)

            # If the permissions donot allow to edit, make it editable
            if (permissions != 0755):
                subprocess.call(['chmod', '0755', hibernatePath])

            file = open(hibernatePath, 'r')
            parser = PCParser()
            xmlTreeFile = xml.etree.ElementTree.parse(file, parser)
            root = xmlTreeFile.getroot()

            HibernateAutomator().recursiveIter(root, valuesFound, Configurations.hibernateTuningParameters)

            # ValuesNotFound = hibernateTuningParameters - valuesFound
            for value in Configurations.hibernateTuningParameters:
                if value in valuesFound:
                    for childValue in Configurations.hibernateTuningParameters[value]:
                        for value1 in  Configurations.hibernateTuningParameters[value][childValue]:
                            if value1 not in valuesFound[value][childValue]:
                                if root.tag not in valuesNotFound:
                                    tempDict = {}
                                    tempDict[childValue] = [value1]
                                    valuesNotFound[value] = tempDict
                                else:
                                    valuesNotFound[value][childValue].append(value1)
                else:
                    valuesNotFound[value] = Configurations.hibernateTuningParameters[value]

            logger.info("values that need to be added in HibernateXml: ")
            print valuesNotFound

            proceedAnswer = SyslogNgAutomator().proceedAnswer()

            if proceedAnswer == 'yes' or proceedAnswer == 'YES':

                # Take a backup of the file
                shutil.copy2(hibernatePath, hibernatePath + '_backup_' + str(datetime.now()))

                iter = xmlTreeFile.getiterator()
                for elem in iter:
                    if elem.tag == "session-factory":
                        for value in valuesNotFound:
                            for childValue in valuesNotFound[value]:
                                for childValue1 in valuesNotFound[value][childValue]:
                                    xml.etree.ElementTree.SubElement(elem, value).set(childValue,childValue1)

                xmlTreeFile.write(open(hibernatePath, 'w'), "UTF-8")

            else:
                logger.info("hibernate.xml was not modified.")

            # Reset the file permissions to the original value:
            if (permissions != 0755):
                subprocess.call(['chmod', permissions, hibernatePath])

        try:
            modifyHibernateFile(hibernatePath, logger)
        except Exception as e:
            logger.error(" Error occured while processing application-context.xml file: ")
            print e
            pass
