import pandas as pd
from mpl_toolkits import mplot3d
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
import plotly.offline as py
import plotly.graph_objs as go
import pyfpgrowth

affectingColumns={}
realMean={}
realMedian={}
realMad={}
meanArray=None
medianArray=None
madArray=None
threshold=0.8
real_columns=None
anomaly_index=None
indexToAffect={}
count=0
anomaly_idx=None
valueRange={} 

def DelNullCol(data):
    dataInfo=data.isna().sum().to_dict()
    colstobedeleted=[]
    for k,v in dataInfo.items():
        if v/data.shape[0]*100>50:
            colstobedeleted.append(k)
    return colstobedeleted

def ifDataAllUnique(data):
    colList=[]
    for i in data.columns:
        if len(data[i].unique())==data.shape[0]:
            colList.append(i)
    return colList

def imputeNumerical(data,type='mean'):
    for i in data.columns:
        if data[i].dtype!='object':
            if data[i].isna().sum()>0:
                if type == 'mean':
                    data[i]=data[i].fillna(data[i].mean())
                elif type== 'median':
                    data[i]=data[i].fillna(data[i].mean())
                elif  type == 'mode':
                    data[i]=data[i].fillna(data[i].mode())
    return data

def imputeCategorical(data,type='max'):
    for i in data.columns:
        if data[i].dtypes =='object':
            if data[i].isna().sum()>0:
                if type=='max':
                    count_dict=data[i].value_counts().to_dict()
                    filler=count_dict[list(count_dict.keys())[0]]
                    data[i]=data[i].fillna(filler)
    return data

def labelEncode(data):
    from sklearn.preprocessing import LabelEncoder
    le=LabelEncoder()
    labelEncode=[]
    for i in data.columns:
        #print(i)
        try:
            labelEncode.append(i)
            datal=le.fit_transform(data[i].astype('str'))
            data.drop(i,inplace=True,axis=1)
            data[i]=datal
        except:
            print(i)
    return data
def coordinatePCA(df,real_columns):
    pca=PCA(n_components=3)
    coordinates=pca.fit_transform(df[real_columns])
    coorDf=pd.DataFrame(coordinates,columns=['X','Y','Z'])
    finalDf=pd.concat([df,coorDf],axis=1)
    return finalDf

def plot3d(finalDf,path,columns=['X','Y','Z']):
    dataPlot = []
    print(finalDf['dbscan'].unique())
    trace1 = go.Scatter3d(
        x=finalDf.loc[finalDf['dbscan']==-1,[columns[0]]].values[:200].reshape(1,-1)[0],
        y=finalDf.loc[finalDf['dbscan']==-1,[columns[1]]].values[:200].reshape(1,-1)[0],
        z=finalDf.loc[finalDf['dbscan']==-1,[columns[2]]].values[:200].reshape(1,-1)[0],
        mode='markers',
        marker=dict(
            size=6 ,
            line=dict(
                color= 'rgba(217, 217, 217, 0.14)',
                width=0.5
            ),

        ),
        name= 'Anomaly'
    )
    trace2 = go.Scatter3d(
        x=finalDf.loc[finalDf['dbscan']!=-1,[columns[0]]].values.reshape(1,-1)[0],
        y=finalDf.loc[finalDf['dbscan']!=-1,[columns[1]]].values.reshape(1,-1)[0],
        z=finalDf.loc[finalDf['dbscan']!=-1,[columns[2]]].values.reshape(1,-1)[0],
        mode='markers',
        marker=dict(
            size= 3,
            line=dict(
                color= 'rgba(217, 217, 217, 0.14)',
                width=0.5
            ),

        ),
        name= 'NonAnomaly'
    )
    dataPlot=[trace1,trace2]
    py.plot(dataPlot, filename=path+'dbscan-scatter.html',auto_open=False)
               
def MinMax(finalDf,real_columns,difference,db,anomaly,nonana):
    global valueRange
    for i in difference:
        if abs(i)>=threshold and abs(i)<1:
            #print(real_columns[list(difference).index(i)])
            print(len(difference))
            colname=real_columns[list(difference).index(i)]
            print(colname)
            print(finalDf[colname].loc[anomaly])
            print(finalDf[colname].loc[nonana])
            print(finalDf[colname].quantile(.9),finalDf[colname].quantile(.1))
            valueRange[colname]=(finalDf[colname].quantile(.9),finalDf[colname].quantile(.1))
    
def calculateDiffFeatures(finalDf,real_columns,anomaly_idx,neighbour_idx):
    anomaly=finalDf.loc[anomaly_idx,real_columns]
    nonanomaly=finalDf.loc[neighbour_idx,real_columns]
    return anomaly-nonanomaly

def getFeatureList(difference,real_columns):
    global affectingColumns,realMean,meanArray,realMedian,realMad,indexToAffect
    for i in difference:
        if abs(i)>=threshold and abs(i)<1:
            #print(difference)
            #print(real_columns[list(difference).index(i)])
            realMean[real_columns[list(difference).index(i)]]=meanArray[real_columns[list(difference).index(i)]]
            realMedian[real_columns[list(difference).index(i)]]=medianArray[real_columns[list(difference).index(i)]]
            realMad[real_columns[list(difference).index(i)]]=madArray[real_columns[list(difference).index(i)]]
            if real_columns[list(difference).index(i)] not in affectingColumns:
                affectingColumns[real_columns[list(difference).index(i)]]=[i]
            else:
                affectingColumns[real_columns[list(difference).index(i)]].append(i)
            if anomaly_idx[count] not in indexToAffect:
                indexToAffect[anomaly_idx[count]]=[real_columns[list(difference).index(i)]]
            else:
                indexToAffect[anomaly_idx[count]].append(real_columns[list(difference).index(i)])
def clean(data):
    col=DelNullCol(data)
    data=data.drop(col,axis=1)
    dcol=ifDataAllUnique(data)
    data=data.drop(dcol,axis=1)
    data=imputeNumerical(data)
    data=imputeCategorical(data)
    data=labelEncode(data)
    return data
def detect_anomaly(data,path):
    global meanArray,medianArray,madArray,anomaly_index,real_columns
    col=DelNullCol(data)
    data=data.drop(col,axis=1)
    dcol=ifDataAllUnique(data)
    data=data.drop(dcol,axis=1)
    data=imputeNumerical(data)
    data=imputeCategorical(data)
    data=labelEncode(data)
    real_columns=data.columns
    #print(real_columns)
    mns=MinMaxScaler()
    data=mns.fit_transform(data)
    db=DBSCAN(eps=1,min_samples=10)
    db.fit(data)
    label=list(db.labels_)
    df=pd.DataFrame(data,columns=real_columns)
    df['dbscan']=db.labels_
    print(label.count(-1))
    finalDf=coordinatePCA(df,real_columns)
    plot3d(finalDf,path)
    import matplotlib.pyplot as plt
    


    from sklearn.neighbors import NearestNeighbors
    neigh = NearestNeighbors(n_neighbors=5)
    neigh.fit(data)


    
    index_list=[]
    x1=None
    y1=None
    global count,anomaly_idx
    anomaly=finalDf.loc[finalDf['dbscan']==-1,real_columns].values
    anomaly_idx=finalDf.loc[finalDf['dbscan']==-1,real_columns].index
    
    count=0
    for j in anomaly[:200]:
        distance,indexes=neigh.kneighbors([j])
        for i in indexes[0]:
            index_list.append(i)
            if i == indexes[0][0]:
                X=finalDf.loc[i]['X']
                Y=finalDf.loc[i]['Y']
                x1=X
                y1=Y
                #db=finalDf.loc[i]['dbscan']
                #plt.scatter(X,Y,c='green')
            else:
                X=finalDf.loc[i]['X']
                Y=finalDf.loc[i]['Y']
                db=finalDf.loc[i]['dbscan']
                if db==-1:

                    #plt.scatter(X,Y,c='red')
                    pass

                else:
                    meanArray=finalDf.loc[finalDf['dbscan']==db,real_columns].mean()
                    medianArray=finalDf.loc[finalDf['dbscan']==db,real_columns].median()
                    madArray=finalDf.loc[finalDf['dbscan']==db,real_columns].mad()
                    diffArray=calculateDiffFeatures(finalDf,real_columns,indexes[0][0],i).values
                    
                    getFeatureList(diffArray,real_columns)
                    MinMax(finalDf,real_columns,diffArray,db,indexes[0][0],i)
        count+=1
    return finalDf
def plotFeature(finalDf,featureName,path):
    trace0 = go.Box(
        y=finalDf[finalDf['dbscan']!=-1][featureName].values,
        boxmean='sd'
    )
    py.plot([trace0],filename=path+'featureplot.html',auto_open=False)
def getReason():
    return affectingColumns,anomaly_idx
def getMinMax():
    return valueRange
def Difference():
    return realMean,realMedian,realMad
def rulesGet():
    featureList=[set(i) for i in indexToAffect.values()]
    patterns=pyfpgrowth.find_frequent_patterns(featureList,support_threshold=1)
    rules=pyfpgrowth.generate_association_rules(patterns,0.5)
    return rules