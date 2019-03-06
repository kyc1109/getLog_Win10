#!python3
# -*- coding: UTF-8 -*-
#!/usr/bin/python

import sys, os, time, datetime, ctypes, subprocess, socket

class UUT():
    """ UUT.reboot() ..."""
    def __doc__(self):
        print("""get system log""")
    def __init__(self):
        pass
        #self.name=name    
    def my_ping(self): #for test
        os.system('ping 127.0.0.1>ping.txt')
        print('function ping')
    def is_admin(self): #https://stackoverflow.com/questions/130763/request-uac-elevation-from-within-a-python-script
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, "", None, 1) #for py 3
            #ctypes.windll.shell32.ShellExecuteW(None, u"runas", unicode(sys.executable), unicode(__file__), None, 1) #for py2
            print("Not admin")
            return False
    def cmd(self,cmd_str):
        os.system(cmd_str)
    def getLog(self):
        pass
    def getzip(self): #OK
        import zipfile
        global logKP, logSW, logAPP, logzipfile, logShot, logBSOD, logOS_sys, logOS_app
        #del log.zip
        if os.path.exists(logzipfile):
            os.system("del /Q "+logzipfile)
            print("del ",logzipfile)
        try:
            #create log.zip
            with zipfile.ZipFile(logzipfile, 'w') as myzip:
                myzip.write(logKP)  #zip logKP
                myzip.write(logSW)
                myzip.write(logAPP)
                myzip.write(logOS_sys)  #zip OS event
                myzip.write(logOS_app)  #zip OS event
                for root, dirs, files in os.walk("."): #find device compare log in sub folder.
                    for file in files:
                        if file.endswith("_FAIL.TXT") or \
                        file.endswith("_PASS.TXT") or \
                        file.endswith("CHECKLIST.TXT") or \
                        file.endswith("CURRENTLIST.TXT"):
                            #print(os.path.join(root, file))
                            #print(root+"\\"+file)
                            myzip.write(root+"\\"+file)

                if os.path.exists(logShot): #add %userprofile%\Pictures\Screenshots\Screenshot (1).png
                    for root, dirs, files in os.walk(logShot): 
                        for file in files:
                            if file.endswith(".png") or file.endswith("Screenshot"):
                                myzip.write(root+"\\"+file)
                if os.path.exists(logBSOD):
                    print("find dump file")
                    myzip.write(logBSOD) #zip dump
            myzip.close()
            uut.logdel()
        except OSError: #沒辦法用if判斷檔案是否存在，所以只好這樣做了。
            print("Miss some files.")
            self.logdel()   #避免找不到檔案的時候，意外中斷，卻忘了刪掉之前的暫存檔。
      


    def logdel(self):
        import os
        global logKP, logSW, logAPP, logOS_app, logOS_sys, logShot, logBSOD
        dellists=[logKP,logSW, logAPP, logOS_app, logOS_sys, logShot, logBSOD]
        for dellist in dellists:
            if os.path.exists(dellist):
                os.system("del /Q "+dellist)
                print("del ",dellist)
          
    def getSW(self):
        import os
        global logKP, logSW, logAPP

        print("getSystem info")
        list_kp=["wmic computersystem get manufacturer, Model",
                "wmic BIOS get Manufacturer,Name,SMBIOSBIOSVersion,Version",
                "wmic OS get Caption,CSDVersion,OSArchitecture,Version",
                "wmic CPU get Name,NumberOfCores,NumberOfLogicalProcessors, CurrentClockspeed",
                "wmic MemoryChip get BankLabel,Manufacturer,Capacity,MemoryType,PartNumber,TypeDetail,Speed",
                "wmic diskdrive get Model, description,Size",
                "wmic path win32_portablebattery get deviceid,manufacturer,designcapacity,name",
                "wmic path win32_videocontroller get Description",
                "wmic path win32_videocontroller get CurrentHorizontalResolution,CurrentVerticalResolution,videomodedescription",
                "wmic desktopmonitor get pnpdeviceid",
                "wmic nic get ProductName"]
                
        #get key part list
        for lists in list_kp:
            os.system(lists+">>"+logKP)
        #get sw driver list, refer by Heysong_Chang@Compal.com
        os.system("wmic path win32_pnpsigneddriver get description,driverversion >"+logSW)
        os.system("wmic product get name,version >"+logAPP) #spend for long time
    def mytime(self):
        import time
        mytime=time.strftime("%Y_%m_%d_%H_%M")
        print(mytime)
        return mytime
    def getEvent(self):
        import os
        global mytime, logOS_sys, logOS_app
        print("getEvent")
        os.system("wevtutil cl System /bu:"+logOS_sys) #Application
        os.system("wevtutil cl Application /bu:"+logOS_app) #Application
    def ethan(self):
        print("""
        Collecting BIOS, Keypart, Dump and OS event logs...
        """)
    def auto_upload(self):
        global logzipfile
        server_log="\\\\192.168.0.1\\Logs" #your server path
        server_log2="\\\\192.168.0.1\\Logs"
        server_log3="\\\\192.168.0.11\\Logs"

        if os.path.exists(server_log):
            print("Logs Server found!!!")
            #print("copy /V /Y "+logzipfile+" "+server_log)
            os.system("copy /V /Y "+logzipfile+" "+server_log)
            print("Logs upload done!!!")
        else:
            print("Logs Server not found!!!")


if __name__ == "__main__":  # Start from here
    import time
    #全域
    logKP = "Log_KP.txt"
    logSW = "Log_SW.txt"
    logAPP = "Log_APP.txt"
    logShot = os.getenv("userprofile")+"\\Pictures\\Screenshots" #add %userprofile%\Pictures\Screenshots\Screenshot (1).png
    logBSOD = os.getenv("SystemRoot")+"\\MEMORY.DMP" 
    mytime = time.strftime("%Y_%m_%d_%H_%M")
    #SKU = os.environ['USERNAME']
    SKU = socket.gethostbyname(socket.getfqdn()).replace(".","-")
    logOS_sys = "Logs_sys_"+mytime+".evtx"
    logOS_app = "Logs_app_"+mytime+".evtx"
    
    os.system('mode con: cols=80 lines=10')

    #if sys.argv[1] is not None and sys.argv[2] is not None and sys.argv[3] is not None:
    if len(sys.argv)>1: #To fix list index out of range
        sku_no=sys.argv[1]
        test_item= sys.argv[2]
        accept_upload= sys.argv[3]
    else:
        sku_no=input("\ninput SKU NO. (ex:1-1): ") #1
        test_item=input("\ninput test item and symptom (ex:WB_BSNBLNCL): ") #2
        accept_upload=str(input("\nAccept to upload log to server?(Y/n)") or "Y") #3
    logzipfile= SKU+"_"+sku_no+"_"+"Logs_"+test_item+"_"+mytime+".zip"

    #print("cwd: ",os.getcwd())
    os.chdir(os.environ['USERPROFILE']+"\\Desktop") #Change the current working directory to Desktop
    #print("cwd: ",os.getcwd())

    uut=UUT() #create menu from Class UUT
    if uut.is_admin(): #check admin or not
        # Code of your program here
        #uut.ethan()
        uut.getSW() #ok
        uut.getEvent() #ok
        uut.getzip()  #ok
        uut.logdel() #del all of logs
        print("accept_upload: ",accept_upload)
        if accept_upload.lower()=="Y".lower() or accept_upload=="Yes".lower() or accept_upload=="":
            uut.auto_upload()
        else:
            print("Log no upload to server")
        #print(os.getenv("SystemRoot"))
        #uut.mytime()
        

    else:
        # Re-run the program with admin rights
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, "", None, 1) #for py 3
        #ctypes.windll.shell32.ShellExecuteW(None, u"runas", unicode(sys.executable), unicode(__file__), None, 1) #for py2
        print ("Not admin")
        uut.cmd("timeout /t 10")
    



#add %userprofile%\Pictures\Screenshots\Screenshot (1).png
#IP instead of UUT






    
