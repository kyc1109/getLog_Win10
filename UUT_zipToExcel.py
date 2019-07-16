#!python3
# -*- coding: UTF-8 -*-
def findZips():
    zipfiles=[]
    for root, dirs, files in os.walk("."): #find device compare log in sub folder.
        for file in files:
            if file.endswith("zip"):
                zipfiles.append(file)
    return zipfiles
def zipLog(zFile): #parser Log_KP.txt
    config=""
    configs=[]
    kp_items=[]
    kp_infos=[]
    with zipfile.ZipFile(zFile, 'r') as zf:
        try:
            kps=zf.read('Log_KP.txt').decode("utf-8") #byte file need decode
            kps_buff=io.StringIO(kps) #str to buff, buff can using readline()    
            for kp in kps_buff: #filter below item 
                if kp.find("IP")==0 or \
                kp.find("MAC")==0 or \
                kp.find("OS_Version")==0 or \
                kp.find("CPU_Name")==0 or \
                kp.find("SMBIOSBIOSVersion")==0 or \
                kp.find("RAM_Manufacturer")==0 or \
                kp.find("PartNumber")==0 or \
                kp.find("Speed")==0 or \
                kp.find("Capacity")==0 or \
                kp.find("Disk_Model")==0 or \
                kp.find("Size")==0 or \
                kp.find("Description")==0 or \
                kp.find("Battery_manufacturer")==0 or \
                kp.find("designcapacity")==0 or \
                kp.find("name")==0:
                    config=config+kp
            config=config.split("\r\n")
            for con in config:
                configs=configs+con.split("=")
            for con in range (0,len(configs),2):    #get item title
                kp_items.append(configs[con])
            for con in range (1,len(configs),2):    #get item info
                #print("kp_info:",configs[con])
                kp_infos.append(configs[con])
        except:
            print("Log_KP.txt not found in "+zFile+" file")        
    return kp_items, kp_infos


def configToExcel(wlist):
    select_df = pd.DataFrame(wlist)
    select_df.to_excel("UUT_Config_Table.xlsx",sheet_name="Sheet1", header=False, index=False)
def find_diff_item(item_max_uut,item_uut):
    if set(item_uut) - set(item_max_uut): #find difference
        item_max_uut.extend(set(item_uut)-set(item_max_uut)-set(item_max_uut)) #要檢查的放前面，filter放後面。max減兩次避免累加
    return item_max_uut
def findDupItem(item_uuts): #find duplicated items and mark * icon
    uut_count=1
    for item_uut in item_uuts:
        for x in range(len(item_uut)): #x will iterate all items.
            if item_uut.count(item_uut[x])>1: #item over 2 or more
                for i in range(item_uut.count(item_uut[x])):
                    i=i+1   
                    item_uut[x]=item_uut[x]+"*"
        uut_count+=1
    return item_uuts
def replaceStar(iimms): #modify * to number
    count=0
    for iimm in range(len(iimms)): 
        if iimms[iimm] != None: #print("\"NoneType\" object has no attribute \"count\"")
            count = iimms[iimm].count("*")
            iimms[iimm] = str(iimms[iimm]).replace(" *","___*")
            iimms[iimm] = str(iimms[iimm]).replace("*","")
            iimms[iimm] = str(iimms[iimm]).replace("___","_"+str(count))
        else:
            pass
    return iimms

if __name__ == "__main__":  # Start from here
    import time, os, sys, re, zipfile, io, numpy
    import pandas as pd
    import itertools as it
    os.system("cls")
    kpTable=[]
    itemTable=[]
    infoTable=[]
    zFiles=findZips()
    Utables=[]
    item_uuts=[] #get all title
    info_uuts=[] #get all info
    item_max_uut=[]
    for zFile in zFiles: #get item and info from zip by each unit
        item_uut, info_uut=zipLog(zFile) #return title and info of KP
        item_uuts.append(item_uut)
        info_uuts.append(info_uut)
    #-----find the max item-------------------------------
    for item_uut in item_uuts: #find another items in all units to item_max
        if len(item_uut) > len(item_max_uut):
            item_max_uut = item_uut
    #-----add others item to max-------------------------------
    #print("\n\nbefore:",item_max_uut)
    for item_uut in item_uuts:  #get max mix
        item_max_uut=find_diff_item(item_max_uut,item_uut)
    #------mark dup item as *------------------------------
    #找重複item 並標上*號
    item_uuts = findDupItem(item_uuts)
    #--------filter out no need items part 2----------------------------
    import pandas as pd
    df=pd.DataFrame()
    item_uuts2=[]
    info_uuts2=[]
    item_info_uut=[]
    UUTi=0
    icount=0 #max_item_uut
    max_count=0 #max_item
    item_count=0 #item_uut
    #use dict to combine item and info
    for item_uut,info_uut in it.zip_longest(item_uuts,info_uuts):     
        while icount < len(item_max_uut): #loop by max
            if item_count <= len(item_uut): # fix list over len
                if item_max_uut[max_count]==item_uut[item_count]:
                    item_info_uut.append(item_uut[item_count])                    
                    if item_count == (len(item_uut)-1):
                        pass
                    else:
                        item_info_uut.append(info_uut[item_count])
                    icount=icount+1
                    max_count=max_count+1
                    item_count=item_count+1
                else:
                    item_info_uut.append(item_max_uut[max_count])
                    item_info_uut.append("--")
                    icount=icount+1
                    max_count=max_count+1    
        icount=0 #reset
        max_count=0 #reset
        item_count=0 #reset
        item_info_uut=replaceStar(item_info_uut)
        df["UUT"+str(UUTi)]=pd.Series(item_info_uut) #list to matrix table
        item_info_uut=[]  #UUT config, reset data
        UUTi=UUTi+1   #UUT count
    print(df)
    df.to_excel("UUT_Config_Table.xlsx",sheet_name="Sheet1", header=False, index=False)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
