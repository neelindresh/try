import pandas as pd
from mpl_toolkits import mplot3d
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
import plotly.offline as py
import plotly.graph_objs as go
import pyfpgrowth
from sklearn.ensemble import IsolationForest
from sklearn.datasets import load_iris
import numpy as np
import random

from . import Unsupervised as un

featureList={}
featureList_1 = {}
def getFeatureList(id_anomaly,importance,real_col):
#     print('id_anom', id_anomaly)
    global featureList
    mean=np.median(importance)
    listoffeatures=[]
    listoffeatures_1 = []
    for idx,i in enumerate(importance):
        if i> mean:
            listoffeatures.append(real_col[idx])
            listoffeatures_1.append((real_col[idx], i))
    # list of imp features stored in feature[anomaly_index_in_actual_df] for each row indicated by anomaly_index_in_actual_df.
    featureList[id_anomaly]=listoffeatures
    listoffeatures_1.sort(key=lambda x: x[1], reverse=True)
    featureList_1[id_anomaly] = listoffeatures_1
    
    
def findImportantTree(anomaly,nonanomaly,iforest):
    importantTrees=[]
    count=0
    for trees in iforest.estimators_:
        #print('anomaly')
        distanceMatAnomaly=np.unique(trees.decision_path(anomaly.reshape(1,-1)).toarray(),return_counts=True)[1][1]
        #print('non anomaly')
        distanceMatnonAnomaly=np.unique(trees.decision_path(nonanomaly.values.reshape(1,-1)).toarray(),return_counts=True)[1][1]
        if distanceMatAnomaly<distanceMatnonAnomaly:
            importantTrees.append(trees)
            count+=1
    return importantTrees
def plot3d(finalDf,path,columns=['X','Y','Z']):
    dataPlot = []
    trace1 = go.Scatter3d(
        x=finalDf.loc[finalDf['predicted']==-1,[columns[0]]].values[:200].reshape(1,-1)[0],
        y=finalDf.loc[finalDf['predicted']==-1,[columns[1]]].values[:200].reshape(1,-1)[0],
        z=finalDf.loc[finalDf['predicted']==-1,[columns[2]]].values[:200].reshape(1,-1)[0],
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
        x=finalDf.loc[finalDf['predicted']!=-1,[columns[0]]].values.reshape(1,-1)[0],
        y=finalDf.loc[finalDf['predicted']!=-1,[columns[1]]].values.reshape(1,-1)[0],
        z=finalDf.loc[finalDf['predicted']!=-1,[columns[2]]].values.reshape(1,-1)[0],
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
    py.plot(dataPlot, filename=path+'isolation-scatter.html',auto_open=False)
def plotFimportance(sorted_x,path):
    data = [go.Bar(
            x=list(sorted_x.keys()),
            y=list(sorted_x.values()),
            
    )]
    layout = go.Layout(
        title=go.layout.Title(
            text='Features Affecting Anomalies',
            xref='paper',
        ))
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename=path+'FeatureImportance.html',auto_open=False)
def fit(data):
    col=un.DelNullCol(data)
    data=data.drop(col,axis=1)
    dcol=un.ifDataAllUnique(data)
    data=data.drop(dcol,axis=1)
    data=un.imputeNumerical(data)
    data=un.imputeCategorical(data)
    data=un.labelEncode(data)
    real_col=data.columns
    iforest=IsolationForest(contamination=0.05)
    iforest.fit(data)
    predicted=iforest.predict(data)
   
    #reasons
    dataFrame=data
    dataFrame['predicted']=predicted
    #plot Graph
    finalDf=un.coordinatePCA(dataFrame,real_col)
    plot3d(finalDf,'helloworld/static/image/')
    
    
    anomaly=dataFrame.loc[dataFrame['predicted']==-1,real_col]
    nonanomaly=dataFrame.loc[dataFrame['predicted']==1,real_col]
    for i,j in zip(dataFrame.loc[dataFrame['predicted']==-1,real_col].values,dataFrame.loc[dataFrame['predicted']==-1,real_col].index):
        ran=random.choice(dataFrame.loc[dataFrame['predicted']==1,real_col].index)
        # pass "one" anomalous row and one non-anomalous row to the findImportantTree() func
        important=findImportantTree(i,dataFrame.loc[ran,real_col],iforest)
        #print(i-dataFrame.loc[ran,real_col])
        importance=np.sum([trees.feature_importances_ for trees in important],axis=0)
        getFeatureList(j,importance,real_col)
    # compute the frequncy of occurrences of each feature
    feature_imp_anomalies_isolation = pd.DataFrame(featureList_1)
    feature_imp_anomalies_isolation = feature_imp_anomalies_isolation.head(10)
    feature_imp_anomalies_isolation_transpose = feature_imp_anomalies_isolation.transpose()
    feature_imp_anomalies_isolation_transpose.columns = [('Feature '+str(i)) for i in range(1, 11)]
#     print(list(feature_imp_anomalies_isolation.items())[0])
    path = 'flow/static/data/temporary/'
    feature_imp_anomalies_isolation_transpose.to_csv(path+'feature_imp_anomalies_isolation.csv')
    feature_imp_anomalies_isolation_transpose = pd.read_csv(path+'feature_imp_anomalies_isolation.csv')
    feature_imp_anomalies_isolation_transpose.columns = ['Row Index'] + [('Feature '+str(i)) for i in range(1, 11)]
    feature_imp_anomalies_isolation_transpose.to_csv(path+'feature_imp_anomalies_isolation.csv')
    
    frequency_dict={}
    for i  in featureList.values():
        for j in i:
            if j in frequency_dict:
                frequency_dict[j]+=1
            else:
                frequency_dict[j]=1
    sorted_x = sorted(frequency_dict.items(), key=lambda kv: kv[1],reverse=True)
    sorted_x={k:v for k,v in sorted_x}
    plotFimportance(sorted_x,'helloworld/static/image/')