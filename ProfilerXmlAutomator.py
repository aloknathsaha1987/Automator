import os, shutil, subprocess
import xml, re
from datetime import datetime
import Configurations
from PCParser import PCParser
from SyslogNgAutomator import SyslogNgAutomator


class ProfilerxmlAutomator(object):

    def __init__(self):
        print ""

    @classmethod
    def indent(cls, elem, level=0):
        i = "\n" + level * "  "
        if len(elem):
            print elem.text
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                cls.indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            elem.text = re.sub(r"([a-z]\")", r"\1\n", elem.text)
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
    @classmethod
    def automate(cls,profilerXmlPath, logger):

        def representsInt(s):
            try:
                int(s)
                return True
            except ValueError:
                return False

        def modifyProfilerXmlFile(profilerXmlPath, logger):
            valuesFoundInProfilerXml = []
            valuesNotFoundInProfilerXml = []
            valuesNeedToBeModifiedInProfilerXml = []

            # # Get Permissions on a File
            permissions = oct(os.stat(profilerXmlPath).st_mode & 0777)


            # If the permissions donot allow to edit, make it editable
            if (permissions != 0755):
                subprocess.call(['chmod', '0755', profilerXmlPath])

            file = open(profilerXmlPath, 'r')
            parser = PCParser()
            xmlTreeFile = xml.etree.ElementTree.parse(file, parser)
            root = xmlTreeFile.getroot()
            resource = root.find('Resource')

            for neighbor in root.getiterator('Resource'):
                # Search for the values from the Configuration File
                for key in Configurations.profilerXmlTuningParameters:
                    if key in neighbor.attrib:
                        valuesFoundInProfilerXml.append(key)
                        if neighbor.attrib[key] != Configurations.profilerXmlTuningParameters[key]:
                            # Update the parameter value and add it to the valuesNeedToBeModifiedInProfilerXml
                            valuesNeedToBeModifiedInProfilerXml.append(key)
                            neighbor.set(key, Configurations.profilerXmlTuningParameters[key])


            # Check for Profiler xml must haves:
            username = ""
            url = ""
            for mustHaveValue in Configurations.profilerXmlMustHaveParameters:
                if not mustHaveValue in resource.attrib or resource.attrib[mustHaveValue] == "":
                    logger.warn(" The "+ mustHaveValue + " value is not set.")
                elif mustHaveValue == "username":
                    username = resource.attrib["username"]
                elif mustHaveValue == "url":
                    url = resource.attrib["url"]


            # Check if the username is set to root, give a warning if set
            if username == "root":
                logger.warn("The username should not be root, it should be changed to be specific"
                            "to Securonix application.")

            # Check the url parameters that need to be added/ modified

            urlValues = re.search("\/securonix(.*?)\?(.*)", url)

            if urlValues:
                if representsInt(urlValues.group(1)):
                    logger.warn("The database name should not have a number in it.")

                words = urlValues.group(2).split('&')
                wordsDict = {}
                parametersToBeUpdated = {}

                for word in words:
                    tempSplit = word.split('=')
                    if len(tempSplit) >= 2:
                        wordsDict[tempSplit[0]] = tempSplit[1]

                for parameter in Configurations.profilerXmlUrlParameters:
                    if parameter in wordsDict:
                        if wordsDict[parameter] != Configurations.profilerXmlUrlParameters[parameter]:
                            parametersToBeUpdated[parameter] = Configurations.profilerXmlUrlParameters[parameter]

                    else:
                        parametersToBeUpdated[parameter] = Configurations.profilerXmlUrlParameters[parameter]

                # Construct the string
                for parameter in parametersToBeUpdated:
                    if parameter in url:
                        url = url.replace(parameter + "=" + wordsDict[parameter], parameter + "=" + parametersToBeUpdated[parameter])
                    else:
                        url+= "&" + parameter + "=" + parametersToBeUpdated[parameter] + "&"

                resource.set("url", url)

            # Get the values that were not found in the Profiler Xml and append it to the xml file:
            for value in Configurations.profilerXmlTuningParameters:
                if not valuesFoundInProfilerXml.__contains__(value):
                    valuesNotFoundInProfilerXml.append(value)

            logger.info("Values found: ")
            print valuesFoundInProfilerXml
            logger.info("Values to be modified: ")
            print valuesNeedToBeModifiedInProfilerXml
            logger.info("Values not found and to be added: ")
            print valuesNotFoundInProfilerXml

            for value in valuesNotFoundInProfilerXml:
                resource.attrib[value] = Configurations.profilerXmlTuningParameters[value]

            file.close()

            proceedAnswer = SyslogNgAutomator().proceedAnswer()

            if proceedAnswer == 'yes' or proceedAnswer == 'YES':
                # Take a backup of the file
                shutil.copy2(profilerXmlPath, profilerXmlPath + '_backup_' + str(datetime.now()))

                xmlTreeFile.write(open(profilerXmlPath, 'w'), "UTF-8")
                logger.info("Profiler xml got modified.")
            else:
                logger.info("Profiler xml was not modified.")

            # Reset the file permissions to the original value:
            if (permissions != 0755):
                subprocess.call(['chmod', permissions, profilerXmlPath])

        try:
            modifyProfilerXmlFile(profilerXmlPath, logger)
        except Exception as e:
            logger.error(" Error occured while processing Profiler.xml file: ")
            print e
            pass


