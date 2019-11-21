import pandas as pd
import numpy as np
import scipy
from scipy import special
from PyAstronomy import pyasl
import os, shutil

median=None
MAD=None
sampleStd=None
sampleMean=None
PopulationMean=None
def MadValues(data):
    median_=np.median(data,axis=0)
    MAD_=np.median(np.abs(data-median_))
    return MAD_

def ModifiedZScore(data):
    #0.6745*(X-median)/MAD
    return 0.6745*(data-median)/MAD


def getOutliersMad(data,column):
    global median,MAD
    UniColumn=data[column]
    UniColumn=UniColumn.fillna(value=UniColumn.mean())
    UniColumn=pd.DataFrame(UniColumn,columns=[UniColumn.name])
    MAD=MadValues(UniColumn)
    median=np.median(UniColumn,axis=0)
    ModifiedZ=UniColumn.apply(ModifiedZScore)
    UniColumn['ModifiedZ']=list(ModifiedZ.values)
    indexList=list(UniColumn[UniColumn['ModifiedZ']>3].index)
    indexList.extend(list(UniColumn[UniColumn['ModifiedZ']<-3].index))
    modz=list(UniColumn['ModifiedZ'].iloc[indexList].values)
    return indexList, modz


def getZScore(data):
    zscore=(data-data.mean())/data.std()
    return zscore

def getPValues(zscore):
    pvalues=1-special.ndtr(zscore)
    return pvalues
def getMaxPopulationMean(data):
    #print(abs(data-sampleMean))
    return abs(data-sampleMean)

def PeirceEstimate(data):
    global sampleStd
    if sampleStd==0:
        sampleStd=0.1
    if abs(data-sampleMean)>PopulationMean/sampleStd:
        return True
    else:
        return False 

def getOutliersPtest(data,column,alpha=0.025):
    UniColumn=data[column]
    UniColumn=UniColumn.fillna(value=UniColumn.mean())
    UniColumn=pd.DataFrame(UniColumn,columns=[UniColumn.name])
    zscore=getZScore(UniColumn[column])
    UniColumn['ZScore']=zscore
    UniColumn['PValues']=getPValues(UniColumn['ZScore'])
    indexList=list(UniColumn[UniColumn['PValues']>alpha].index)
    pval=list(UniColumn['PValues'].iloc[indexList].values)
    return indexList, pval

def getOutliersChauvenet(data,column):
    alpha=1/(2*len(data))
    idlist, m=getOutliersPtest(data,column,alpha)
    chauv=list(data[column].iloc[idlist].values)
    return idlist, chauv

def getOutliersESD(data,column):
    UniColumn=data[column]
    UniColumn=UniColumn.fillna(value=UniColumn.mean())
    UniColumn=pd.DataFrame(UniColumn,columns=[UniColumn.name])
    r=pyasl.generalizedESD(UniColumn[column],100,fullOutput=True)
    return r[1]

def getPeirce(data,column):
    global sampleMean,sampleStd,PopulationMean
    UniColumn=data[column]
    UniColumn=UniColumn.fillna(value=UniColumn.mean())
    UniColumn=pd.DataFrame(UniColumn,columns=[UniColumn.name])
    sampleMean=UniColumn[column].mean()
    sampleStd=UniColumn[column].std()
    PopulationMean=UniColumn[column].apply(getMaxPopulationMean).mean()
    UniColumn['PCiter']=UniColumn[column].apply(PeirceEstimate)
    return UniColumn[UniColumn['PCiter']==True].index

def remove(pathcol):
    for the_file in os.listdir(pathcol):
        file_path = os.path.join(pathcol, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            #elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)