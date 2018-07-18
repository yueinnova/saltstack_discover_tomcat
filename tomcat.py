#!/bin/python
# encoding=utf-8

import commands
import xml.etree.ElementTree as ET

def ciData():

    grains = {}
    datas = {}

    ## Step 1. find tomcat's home directory
    keyword = "server.xml"

    locateSvr = "locate " + keyword + " | grep tomcat"
    dirSvr = commands.getoutput(locateSvr).strip()
    #print dirSvr

    locateConf = "dirname " + dirSvr
    dirConf = commands.getoutput(locateConf).strip()
    #print dirConf

    locateHome = "dirname " + dirConf
    dirHome = commands.getoutput(locateHome).strip()
    #print dirHome

    ## Step 2. locate server.xml and version.sh
    conFile = dirHome + "/conf/server.xml"
    verSh = dirHome + "/bin/version.sh"
    
    ## Step 3. fetch info from server.xml

    root = ET.parse(conFile).getroot()

    ## initial 
    port = "port"
    connectionTimeout = "connectiontimeout"
    redirectPort = "redirectport"
    shutDownPort = "sdport"
    maxThreads = "maxthreads"
    minSpareThreads = "minsparethreads"
    runningState = "state"

   # root = ET.parse(conFile).getroot()

    if "SHUTDOWN" in root.get("shutdown"):
        shutDownPort = root.get("port", port)

    for connector in root.find("Service").findall("Connector"):
        if "HTTP" in connector.get("protocol"):
            port = connector.get("port", port)
            connectionTimeout = connector.get("connectionTimeout", connectionTimeout) + " ms"
            redirectPort = connector.get("redirectPort", redirectPort)

    for executor in root.find("Service").findall("Executor"):
        if "ThreadPool" in executor.get("name"):
            maxThreads = executor.get("maxThreads", maxThreads)
            minSpareThreads = executor.get("minSpareThreads", minSpareThreads)
    
    # Step 4. get version info by version.sh
    getVersion = verSh + " | grep -i 'Server version' | awk -F\: '{print $2}'"
    version = commands.getoutput(getVersion).strip()

    # Step 5. chk tomcat whether is running or not 
    chkPort = "netstat -lnp | grep " + port
    if commands.getoutput(chkPort) == "":
        runningState = "stopped"
    else:
        runningState = "running"

    # Step 6. general cmd to get java version/ipv4

   # getJavaVersion = "java -version 2>&1 | awk 'NR==1 {gsub(/"/,""); print $3}'"
    getJavaVersion = "java -version 2>&1 | awk 'NR==1 {print $3}' | sed 's/\"//g'"
    javaVersion = commands.getoutput(getJavaVersion).strip()
    
    getIpAddr = "grep IPADDR /etc/sysconfig/network-scripts/ifcfg-enp0s8 | cut -d = -f 2"
    ipAddr = commands.getoutput(getIpAddr).strip()

    getHostName = "hostname"
    hostName = commands.getoutput(getHostName).strip()

    datas['connectionTimeout'] = connectionTimeout
    datas['home'] = dirHome
    datas['hostName'] = hostName
    datas['redirectPort'] = redirectPort       
    datas['jdkVersion'] = javaVersion   
    datas['maxThreads'] = maxThreads      
    datas['minSpareThreads'] = minSpareThreads
    datas['port'] = port   
    datas['serIP'] = ipAddr
    datas['shutPort'] = shutDownPort
    datas['version'] = version
    datas['state'] = runningState

    # print "Install Directory: " + dirHome
    # print "port: " + port
    # print "redirect port: " + redirectPort
    # print "connection timeout: " + connectionTimeout 
    # print "max threads: " + maxThreads
    # print "min spare threads: " + minSpareThreads
    # print "shutdown port: " + shutDownPort
    # print "version: " + version
    # print "java version: " + javaVersion  
    # print "host ip: " + ipAddr
    # print "hostname: " + hostName

    key = 'Tomcat_' + str(port)
    grains[key] = datas
    return grains
    
if __name__=="__main__":
    datas = ciData()
    print datas    
