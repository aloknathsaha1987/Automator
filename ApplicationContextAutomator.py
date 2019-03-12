import os, shutil
import subprocess
import xml
import Configurations
from PCParser import PCParser
from SyslogNgAutomator import SyslogNgAutomator
from datetime import datetime

class ApplicationContextAutomator(object):

    def __init__(self):
        print ""

    @classmethod
    def findParameters(cls, root, valuesNeedToBeModified, tuningparameters,valueModificationDone ):
        if root.tag in tuningparameters:
            if bool(root.attrib):
                for attrib in root.attrib:
                    if attrib in tuningparameters[root.tag]:
                        if root.attrib[attrib] != tuningparameters[root.tag][
                            attrib]:
                            if valueModificationDone:
                                if root.tag == "Connector":
                                    if "secure" in root.attrib:
                                            root.set(attrib,tuningparameters[root.tag][attrib])
                                else:
                                    root.set(attrib, tuningparameters[root.tag][attrib])
                            else:
                                valuesNeedToBeModified.append(attrib)

            else:
                if root.text != tuningparameters[root.tag]:
                    if valueModificationDone:
                        root.text = tuningparameters[root.tag]
                    else:
                        valuesNeedToBeModified.append(root.tag)


    @classmethod
    def recursiveIter(cls, root, valuesNeedToBeModified, tuningparameters, valueModificationDone):
        if len(root):
            cls.findParameters(root, valuesNeedToBeModified, tuningparameters, valueModificationDone)
            for root in root:
                cls.recursiveIter(root, valuesNeedToBeModified, tuningparameters, valueModificationDone)
        else:
            cls.findParameters(root, valuesNeedToBeModified, tuningparameters, valueModificationDone)

    @ classmethod
    def automate(cls, applicationContextPath, logger):
        valuesNeedToBeModifiedInApplicationContextXml = []


        def modifyApplicationContextFile(applicationContextPath, logger):

            # # Get Permissions on a File
            permissions = oct(os.stat(applicationContextPath).st_mode & 0777)

            # If the permissions donot allow to edit, make it editable
            if (permissions != 0755):
                subprocess.call(['chmod', '0755', applicationContextPath])

            file = open(applicationContextPath, 'r')
            parser = PCParser()
            xmlTreeFile = xml.etree.ElementTree.parse(file, parser)
            root = xmlTreeFile.getroot()
            ipaddressReference = subprocess.Popen("ifconfig| grep -e 'inet addr' | grep  'Bcast' | cut -d: -f2 | cut -d' ' -f1",
                                         shell=True, stdout=subprocess.PIPE).stdout.read().strip("\n")
            timeZoneReference = subprocess.Popen("date | cut -d' ' -f5",shell=True, stdout=subprocess.PIPE).stdout.read().strip("\n")

            hostName = subprocess.Popen(" cat /etc/hosts | grep " + ipaddressReference + " |  awk '{print $2}'", shell=True, stdout=subprocess.PIPE).stdout.read().strip("\n")

            # Check to see if ssl is secure from server.xml
            serverXmlFile = open(Configurations.serverXmlPath, 'r')
            parser = PCParser()
            serverXmlTreeFile = xml.etree.ElementTree.parse(serverXmlFile, parser)

            iter = serverXmlTreeFile.getiterator()

            for elem in iter:
                if elem.tag == "Connector":
                    if "secure" in elem.attrib:
                        secure = elem.attrib["secure"]
                        print secure


            constructedUrl = ""
            # Construct the url
            if secure == "true":
                constructedUrl = "https://" + hostName + ":8443/Profiler"
            elif secure == "false":
                constructedUrl = "http://" + hostName + ":8080/Profiler"

            Configurations.applicationContextTuningParameters['system'] = timeZoneReference
            Configurations.applicationContextTuningParameters['database'] = timeZoneReference

            root.set("url", constructedUrl)

            # Check for the attribute values in the root
            for value in Configurations.applicationContextMustHaveParameters:
                if not value in root.attrib or root.attrib[value] == "":
                    logger.warn("The " + value + " value is not set.")


            # Check if the url set in the url attribute
            if ipaddressReference not in root.attrib['url']:
                logger.warn("The URL is not set correctly (The IP address doesnot match)")

            ApplicationContextAutomator().recursiveIter(root,valuesNeedToBeModifiedInApplicationContextXml,
                                                        Configurations.applicationContextTuningParameters ,False)

            # print "valuesNotFoundInApplicationContextXml: ", valuesNotFoundInApplicationContextXml
            logger.info("values that need to be modified in ApplicationContextXml: ")
            print valuesNeedToBeModifiedInApplicationContextXml

            proceedAnswer = SyslogNgAutomator().proceedAnswer()

            if proceedAnswer == 'yes' or proceedAnswer == 'YES':
                # Take a backup of the file
                shutil.copy2(applicationContextPath, applicationContextPath + '_backup_' + str(datetime.now()))
                ApplicationContextAutomator().recursiveIter(root,valuesNeedToBeModifiedInApplicationContextXml,
                                                            Configurations.applicationContextTuningParameters ,True)
                xmlTreeFile.write(open(applicationContextPath, 'w'), "UTF-8")
                logger.info("application-context.xml got modified.")
            else:
                logger.info("application-context.xml was not modified.")

            # Reset the file permissions to the original value:
            if (permissions != 0755):
                subprocess.call(['chmod', permissions, applicationContextPath])

        try:
            modifyApplicationContextFile(applicationContextPath, logger)
        except Exception as e:
            logger.error(" Error occured while processing application-context.xml file: ")
            print e
            pass