import os

securonixHome = os.environ['SECURONIX_HOME']

#Path to various files
syslogNgPath = "/etc/syslog-ng/syslog-ng.conf"
myCnfPath = "/usr/my.cnf"
startupPath = securonixHome + "/Tomcat/bin/startup.sh"
profilerXmlPath = securonixHome + "/Tomcat/conf/Catalina/localhost/Profiler.xml"
applicationContextPath = securonixHome + "/securonix_home/conf/application-context.xml"
serverXmlPath = securonixHome + "/Tomcat/conf/server.xml"
hibernatePath = securonixHome + "securonix_home/conf/hibernate/hibernate.cfg.default.xml"
ninentynProcPath = "/etc/security/limits.d/90-nproc.conf"
limitsConfPath = "/etc/security/limits.conf"
sysctlPath = "/etc/sysctl.conf"

mysqlVariableTuningValues = {'innodb_buffer_pool_size': {'32': '10G', '64': '20G', '128': '32G', '256': '64G', '512':'128G'}, 'innodb_log_file_size': {'32':'1G', '64':'2G', '128':'3G', '256':'6G', '512':'12G' },
'key_buffer_size': {'32':'2000M', '64':'4000M', '128':'8000M', '256':'16000M', '512':'32000M'},
'bulk_insert_buffer_size': '256M',
'myisam_sort_buffer_size': '256M',
'concurrent_insert': '2',
'connect_timeout': '600',
'long_query_time': '10',
'wait_timeout': '86400',
'interactive_timeout': '86400',
'sort_buffer_size': '1M',
'read_buffer_size': '1M',
'read_rnd_buffer_size': '32M',
'query_cache_type': '1',
'query_cache_size': '256M',
'innodb_flush_log_at_trx_commit': '2',
'innodb_lock_wait_timeout': '180',
'innodb_flush_method': 'O_DIRECT',
'Innodb_thread_concurrency': '0',
'tmp_table_size': '256M',
'max_allowed_packet': '1G',
'max_connections': '300',
'join_buffer_size': '256k',
'table_open_cache': '2000',
'innodb_file_per_table': '1',
'lower_case_table_names': '1',
'open_files_limit': '102400'}

drReplicationParameters = {'binlog_format': 'mixed',
'replicate-same-server-id':'0',
'binlog_cache_size':'64M' }

startupTuningParameters ={
'-Xms': {'32': '12g', '64':'24g', '128':'48g'},
'-Xmx': {'32':'16g', '64':'31g', '128':'52g'},
'-XX:PermSize': '=512m',
'-XX:MaxPermSize': '=512m',
'-XX:NewSize': '=1024m',
'-XX:MaxNewSize': '=1024m',
'-XX:ParallelGCThreads': '=10',
'-XX:InitiatingHeapOccupancyPercent': '=60',
'-verbose': ':gc',
'PrintGCDetails': '-XX:+PrintGCDetails',
'PrintGCTimeStamps': '-XX:+PrintGCTimeStamps',
'PrintGCDateStamps': '-XX:+PrintGCDateStamps',
'PrintTenuringDistribution': '-XX:+PrintTenuringDistribution',
'PrintGCApplicationConcurrentTime': '-XX:+PrintGCApplicationConcurrentTime',
'PrintGCApplicationStoppedTime': '-XX:+PrintGCApplicationStoppedTime',
'UseG1GC': '-XX:+UseG1GC',
'AggressiveOpts': '-XX:+AggressiveOpts',
'-server': ''
}

syslogNgTuningParameters ={
    'flush_lines':'0',
    'time_reopen':'10',
    'log_fifo_size':'1000',
    'long_hostnames':'off',
    'use_dns':'no',
    'use_fqdn':'no',
    'create_dirs':'yes',
    'keep_hostname':'yes',
    'chain_hostnames':'off',
    'log_msg_size':'1000',
    'dir_owner':'securonix',
    'dir_group':'securonix',
    'owner':'securonix',
    'group':'securonix',
    'dir_perm':'0775',
    'perm':'0775'
}

applicationContextMustHaveParameters = ['env', 'version', 'url', 'mode']

applicationContextTuningParameters = {
    'sessionTimeout': '3600',
    'activityImport': {'maxThreadCount': '35', 'recordsPerThread': '20000'},
    'userImport': {'maxThreadCount': '2', 'recordsPerThread': '10000'},
    'splitActivityImportFile': {'enabled': 'true'},
    'multiThreading': {'enabled': 'true'}
}

serverXmlTuningParameters = {
    'Server': {'port': '8080', 'shutdown': 'STARTUP'},
    'Resource': {'name': 'AlokeDataBase', 'type': 'org.apache.catalina.UserDatabase', 'auth': 'Drum'},
    'Connector': {'port': '8081', 'secure': 'true','SSLEnabled':'true', 'ciphers': 'SHA1'}
}

hibernateTuningParameters = {
    'property': {'name': ['hibernate.jdbc.batch_size', 'hibernate.cache.use_second_level_cache', 'hibernate.current_session_context_class']},
    'mapping': {'resource': ['Hello World','jbpm.identity.hbm.xml', 'jbpm.repository.hbm.xml']},
    'testValue': {'range': ['one', 'two']}
}


profilerXmlMustHaveParameters = ['username', 'url', 'encryptedPassword']

profilerXmlUrlParameters = {'autoReconnect': 'false',
                            'rewriteBatchedStatements': 'false',
                            'useUnicode': 'false',
                            'characterEncoding': 'UTF-8',
                            'maxReconnects': '10'}

profilerXmlTuningParameters = {
'auth':'Container',
'type':'javax.sql.DataSource',
'driverClassName':'com.mysql.jdbc.Driver',
'testWhileIdle':'true',
'testOnBorrow':'true',
'testOnReturn':'false',
'validationQuery':'SELECT 1',
'validationInterval':'30000',
'timeBetweenEvictionRunsMillis':'10000',
'maxActive':'377',
'minIdle':'10',
'maxIdle':'50',
'maxWait':'30000',
'initialSize':'10',
'removeAbandonedTimeout':'60',
'removeAbandoned':'true',
'logAbandoned':'true',
'minEvictableIdleTimeMillis':'300000',
'abandonWhenPercentageFull':'50',
'factory':'com.securonix.application.common.util.EncryptionFactor'
}

ninentynProcTuningParameters = {
    'soft nofile': '102400',
    'hard nofile': '102400',
    'soft nproc': '10240',
    'hard nproc': '10240'
}
softHardTuningParameters = ['soft nofile', 'hard nofile', 'soft nproc', 'hard nproc']

limitsTuningParameters =  {
    'soft nofile': '102400',
    'hard nofile': '102400',
    'soft nproc': '10240',
    'hard nproc': '10240',
    'hdfs - nofile': '32768',
    'kafka - nproc': '32768'
}

sysctlParameters = {
    'vm.swappiness': '2',
    'kernel.msgmnb': '72000',
    'kernel.core_uses_pid': '3',
    'vm.swampiness': 'insane'
}




