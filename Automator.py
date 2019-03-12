import ConfigParser, re, logging, Configurations

from ApplicationContextAutomator import ApplicationContextAutomator
from HibernateAutomator import HibernateAutomator
from MyCnfAutomator import MyCnfAutomator
from sys import version_info

from ConfAutomator import ConfAutomator
from ProfilerXmlAutomator import ProfilerxmlAutomator
from ServerXmlAutomator import ServerXmlAutomator
from StartupShAutomator import StartupShAutomator
from SyslogNgAutomator import SyslogNgAutomator

class Automator(object):

    def __init__(self):
        print ""

    # Create a logger object
    @classmethod
    def createLogger(cls):
        # create logger
        logger = logging.getLogger('Automator_Logger')
        logger.setLevel(logging.DEBUG)
        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # add formatter to ch
        ch.setFormatter(formatter)
        # add ch to logger
        logger.addHandler(ch)

        return logger

    # To account for older version of python in ConfigParser
    def rawConfigParserAllowNoValue(self, config):
        OPTCRE_NV = re.compile(
            r'(?P<option>[^:=\s][^:=]*)'  # match "option" that doesn't start with white space
            r'\s*'  # match optional white space
            r'(?P<vi>(?:[:=]|\s*(?=$)))\s*'  # match separator ("vi") (or white space if followed by end of string)
            r'(?P<value>.*)$'  # match possibly empty "value" and end of string
        )
        config.OPTCRE = OPTCRE_NV
        config._optcre = OPTCRE_NV
        return config

    def myCnfAutomation(self, py3, pysub, logger):
        if not py3:
            if not pysub:
                config = ConfigParser.RawConfigParser()
                parser = self.rawConfigParserAllowNoValue(config)
        else:
            parser = ConfigParser.ConfigParser(allow_no_value=True)

        MyCnfAutomator().automate(Configurations.myCnfPath, parser, logger)

    def startUpShAutomation(self, logger):
        StartupShAutomator().automate(Configurations.startupPath, logger)

    def syslogNgAutomation(self, logger):
        # syslogNgPath = "C:\Users\AlokNath\Desktop\K&L_Gates\syslog-ng1.txt"
        SyslogNgAutomator().automate(Configurations.syslogNgPath, logger)

    def profilerXmlAutomation(self, logger):
        profilerXmlPath = "C:\Users\AlokNath\Desktop\K&L_Gates\Profiler1.xml"
        ProfilerxmlAutomator().automate(Configurations.profilerXmlPath, logger)

    def applicationContextAutomation(self, logger):
        applicationContextPath = "C:\Users\AlokNath\Desktop\K&L_Gates\Application-context1.xml"
        ApplicationContextAutomator().automate(Configurations.applicationContextPath, logger)

    def serverXmlAutomation(self, logger):
        serverXmlPath = "C:\Users\AlokNath\Desktop\K&L_Gates\server1.xml"
        ServerXmlAutomator().automate(Configurations.serverXmlPath, logger)

    def hibernateAutomation(self, logger):
        # hibernatePath = "C:\Users\AlokNath\Desktop\K&L_Gates\hibernate.cfg.default1.xml"
        HibernateAutomator.automate(Configurations.hibernatePath, logger)

    def ninentyNProcAutomation(self, logger):
        ninentynProcPath = "C:\Users\AlokNath\Desktop\K&L_Gates\90-nproc1.conf"
        ConfAutomator.automate(ninentynProcPath, logger,
                                       Configurations.ninentynProcTuningParameters, "\s+(.*?)$", "space")

    def limitsAutomation(self, logger):
        limitsConfPath = "C:\Users\AlokNath\Desktop\K&L_Gates\limits1.conf"
        ConfAutomator.automate(limitsConfPath, logger,
                                       Configurations.limitsTuningParameters, "\s+(.*?)$", "space")

    def sysctlAutomation(self, logger):
        sysctlPath = "C:\Users\AlokNath\Desktop\K&L_Gates\sysctl1.conf"
        ConfAutomator.automate(sysctlPath, logger,
                               Configurations.sysctlParameters, "\s+=\s+(.*?)$", "equal")


# The Main Program Starts Here
def main():
    py3 = version_info[0] > 2
    pysub = version_info[1] > 7
    logger = Automator().createLogger()
    logger.info("Starting Automation Script")
    # if py3:
    #     backupPath = input("Enter the path to the backup folder: ")
    # else:
    #     backupPath = raw_input("Enter the path to the backup folder: ")

    try:
        automator = Automator()
        logger.info("Initializing My.cnf Automation")
        # automator.myCnfAutomation(py3, pysub, logger)
        logger.info("Initializing Startup.sh Automation")
        # automator.startUpShAutomation(logger)
        logger.info("Initializing syslogNg Automation")
        # automator.syslogNgAutomation(logger)
        logger.info("Initializing Profiler.xml Automation")
        # automator.profilerXmlAutomation(logger)
        logger.info("Initializing application-context.xml Automation")
        # automator.applicationContextAutomation(logger)
        logger.info("Initializing server.xml Automation")
        # automator.serverXmlAutomation(logger)
        logger.info("Initializing hibernate.xml Automation")
        # automator.hibernateAutomation(logger)
        logger.info("Initializing 90-nproc.conf Automation")
        automator.ninentyNProcAutomation(logger)
        logger.info("Initializing limits.conf Automation")
        automator.limitsAutomation(logger)
        logger.info("Initializing sysctl.conf Automation")
        automator.sysctlAutomation(logger)


    except Exception as e:
        logger.error(" Error occured while processing")
        print e
        pass

if __name__ == "__main__":
    main()

