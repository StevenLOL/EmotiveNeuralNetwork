import os
import csv
import shutil
import numpy as np


def readDataFile(main_root):
    index_file_path =  os.path.join(main_root+'\AllData.txt')
    #Audio File Names
    with open(index_file_path, 'r') as AllDatafile:
        X = [line.strip() for line in AllDatafile] 
        arrayFileName = [line.split(';')[0] for line in X] 
    AllDatafile.close()
    #Emotion Labels
    with open(index_file_path, 'r') as AllDatafile:
        Y = [line.strip() for line in AllDatafile] 
        arrayEmoLabel = [line.split(';')[1] for line in Y]
    AllDatafile.close()  
    #Transcriptions   
    with open(index_file_path, 'r') as AllDatafile:
        Z = [line.strip() for line in AllDatafile] 
        arrayText = [line.split(';')[2] for line in Z]
    AllDatafile.close()
    
    return arrayFileName, arrayEmoLabel


def encodeLabels(arrayEmoLabel,arrayFileName):
    i = 0
    joyEncoded = []
    sadEncoded = []
    angEncoded = []
    neuEncoded = []
    joyFileName = []
    sadFileName = []
    angFileName = []
    neuFileName = []
    
    while i < len(arrayEmoLabel):
        emoLabel = arrayEmoLabel[i]
        
        if  emoLabel == 'exc': 
            code = [1,0,0,0] #JOY
            joyEncoded.append(code)
            joyFileName.append(arrayFileName[i])
        if  emoLabel == 'ang' :    
            code = [0,1,0,0] #ANG
            angEncoded.append(code)
            angFileName.append(arrayFileName[i])
        if  emoLabel == 'sad': 
            code = [0,0,1,0] 
            sadEncoded.append(code)
            sadFileName.append(arrayFileName[i])  
        if  emoLabel == 'neu': 
            code = [0,0,0,1]
            neuEncoded.append(code)
            neuFileName.append(arrayFileName[i])
        if  emoLabel == 'dis' or emoLabel == 'sur' or emoLabel == 'fea' or emoLabel == 'oth' or emoLabel == 'xxx' or emoLabel == 'fru' or emoLabel == 'hap': 
            code = [0,0,0,2]  #NOT CLASSIFIED
                        
        i += 1
        
    return joyEncoded, angEncoded, sadEncoded, neuEncoded, joyFileName, angFileName, sadFileName, neuFileName


def saveEncLabelcsv(emoEncoded, arrayFileName, main_root, emoFolder):
    out_csv_labels_path = os.path.join(main_root, emoFolder)
    i = 0
    
    while i < len(emoEncoded):
        #CREATE OUTPUTS DATA FILE: remove if it already exist and recreate it new
        out_current_file = arrayFileName[i] + '.csv'
        out_current_file = os.path.join(out_csv_labels_path, out_current_file)
        try:
            os.remove(out_current_file)
        except OSError:
            pass
        
        #WRITE ON IT
        print(arrayFileName[i])
        print(emoEncoded[i])
        with open(out_current_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(emoEncoded[i])
        csvfile.close()
        i += 1


if __name__ == '__main__':
    
    #SET MAIN ROOT
    #main_root = os.path.normpath(r'D:\DATA\POLIMI\----TESI-----\Corpus_Training')
    main_root = os.path.normpath(r'D:\DATA\POLIMI\----TESI-----\Corpus_Test')
    #main_root = os.path.normpath(r'C:\Users\JORIGGI00\Documents\MyDOCs\Corpus_Test_Training')
    #main_root = os.path.normpath(r'C:\Users\JORIGGI00\Documents\MyDOCs\Corpus_Usefull') 
     
    #READ DATAFILE AND BUILD ARRAYS
    arrayFileName, arrayEmoLabel = readDataFile(main_root)
    
    #ENCODE EMOTIONS LABELS
    joyEncoded, angEncoded, sadEncoded, neuEncoded, joyFileName, angFileName, sadFileName, neuFileName = encodeLabels(arrayEmoLabel, arrayFileName)
    
    #WRITE CSV FILE
    dir_root = os.path.normpath(main_root+'\LablesEmotion')
    saveEncLabelcsv(joyEncoded, joyFileName, dir_root, 'joy')
    saveEncLabelcsv(angEncoded, angFileName, dir_root, 'ang')
    saveEncLabelcsv(sadEncoded, sadFileName, dir_root, 'sad')
    saveEncLabelcsv(neuEncoded, neuFileName, dir_root, 'neu')
    
    print('END')
    
    