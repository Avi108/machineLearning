
# coding: utf-8

# In[ ]:


# coding: utf-8

# In[ ]:


# coding: utf-8

# In[ ]:

"""
Created on Sun Jul  8 14:49:33 2018

@author: anandrathi
"""


import numpy as np
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.preprocessing import RobustScaler
from sklearn import preprocessing
from sklearn import feature_selection
from sklearn.model_selection import KFold, train_test_split, StratifiedKFold
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, roc_auc_score
from sklearn.decomposition import PCA, TruncatedSVD, FastICA, FactorAnalysis
from sklearn.random_projection import GaussianRandomProjection, SparseRandomProjection
from sklearn.grid_search import GridSearchCV
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, roc_auc_score
from sklearn.decomposition import PCA, TruncatedSVD, FastICA, FactorAnalysis
from sklearn.cross_decomposition import PLSCanonical


from sklearn import decomposition
import matplotlib.pyplot as plt

import lightgbm as lgb

np.random.seed(42)

import pandas as pd

filepath = "/home/ubuntu/testk/"
filepath = "/home/he159490/DS/Kaggle/SantanderValue//"

data_file = filepath + "train.csv"
test_file = filepath + "test.csv"

data = None
Y = None
xdata = pd.read_csv(data_file)
list(xdata.columns)
Y = xdata["target"]
data = xdata.drop(columns=['ID', 'target'])

print(list(data.columns)[0:10])
#print(list(Y.columns))
testdata = None
Ytest = None
testID = None
try:
  testdata = pd.read_csv(test_file)
  print("Test Data Loaded...")
  #list(testdata.columns)
  testID = testdata["ID"]

except Exception as e:
  print(e)

testdata = testdata.drop(columns=['ID'])


# In[]:
YBC = np.log1p(Y)
plt.figure(figsize=(8,8))
plt.plot(range(0,len(Y)),np.sort(YBC))
plt.show()

# In[6]:


# In[ ]:


print("Feature selection...")
colsToRemoveTest  = []
colsToRemoveTrain = []
for col in data.columns:
  if col != 'ID' and col != 'target':
    if data[col].std() ==0:
      colsToRemoveTrain.append(col)
    if testdata[col].std() ==0:
      colsToRemoveTest.append(col)

print("colsToRemoveTrain ==0 {} {}".format(len(colsToRemoveTrain), colsToRemoveTrain))
print("colsToRemoveTest ==0 {} {}".format(len(colsToRemoveTest), colsToRemoveTest))
# remove constant columns in the test set0


# In[ ]:


testdata=testdata.drop(colsToRemoveTest, axis=1, inplace=False)
data=data.drop(colsToRemoveTest, axis=1, inplace=False)

# In[6]:

train_without_duplicates = data.T.drop_duplicates().T
columns_not_to_be_dropped = train_without_duplicates.columns
columns_to_be_dropped = [col for col in testdata.columns if col not in columns_not_to_be_dropped]
print(columns_to_be_dropped )
print(len(columns_to_be_dropped ))
testdata = testdata.drop(columns_to_be_dropped, 1)
data = data.drop(columns_to_be_dropped, 1)

# In[87]:

print("Feature scaling...")
fulldata = data.append(testdata)
rscaler = preprocessing.MinMaxScaler()

dataLogScaled = (data)
testdataLogScaled  = (testdata)
fulldataLogScaled =  (fulldata)
dataLogScaled = np.log1p(data)
testdataLogScaled  = np.log1p(testdata)
fulldataLogScaled = np.log1p(fulldata)

rscaler.fit( fulldataLogScaled )
fulldataScaled = rscaler.transform( fulldataLogScaled )

#rscaler.fit( dataLogScaled )
dataScaled = rscaler.transform( dataLogScaled )

#rscaler.fit( testdataLogScaled )
testdataScaled = rscaler.transform( testdataLogScaled   )

dataScaledLog = (dataScaled)
testdataScaledLog = (testdataScaled)
fulldataScaledLog = (fulldataScaled)
print("Done...")

# In[8]:

print(fulldataScaledLog[0:10])

# In[8]:
def StratifiedSample(data, MY,  test_size, random_state):
  ylen = MY.shape[0]
  print("Ylen = {}".format(ylen))
  nbins = np.unique(MY).shape[0]
  print("bins = {}".format(nbins))
  bins = np.linspace(0, ylen, nbins)

  y_binned = np.digitize(MY, bins)
  MY=np.log1p(MY)
  X_data, X_test, Y_data, y_test = train_test_split(data, MY,
                                                    stratify=y_binned,
                                                    test_size=test_size, random_state=random_state)
  print("X_data = {}".format(X_data.shape))
  print("X_test = {}".format(X_test.shape))
  return  X_data, X_test, Y_data, y_test


# In[ ]:


from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier

def remove_features_using_importance(x_train, y_train, x_test, num_of_features):
    def rmsle(actual, predicted):
        return np.sqrt(np.mean(np.power(np.log1p(actual)-np.log1p(predicted), 2)))

    print("Split train and test")
    #x1, x2, y1, y2 = StratifiedSample(data=x_train, MY=y_train, test_size = 0.25, random_state = 42)
    print("Train RF")
    model = RandomForestRegressor(n_estimators = 211, n_jobs = -2, random_state = 7)
    model.fit(x_train, y_train)
    print(rmsle(np.expm1(y_train), np.expm1(model.predict(x_train))))

    print("Get columns by feature importances")
    col_df = pd.DataFrame({'importance': model.feature_importances_, 'feature': x_train.columns})
    col_df_sorted = col_df.sort_values(by = ['importance'], ascending = [False])
    columns = col_df_sorted[:num_of_features]['feature'].values

    x_train = x_train[columns]
    x_test = x_test[columns]

    return x_train, x_test

num_of_features = int(data.shape[1] * 0.85)+1
x_trainTOPRF, x_testTOPRF = remove_features_using_importance(x_train=data, y_train=YBC, x_test=testdata , num_of_features = num_of_features )

print("x_trainTOPRF {}".format(x_trainTOPRF.shape) )
print("x_testTOPRF {}".format(x_testTOPRF.shape) )


# In[ ]:



from sklearn.random_projection import GaussianRandomProjection, SparseRandomProjection
from sklearn.grid_search import GridSearchCV
def DecomposedFeatures(train,  test,
                                total,
                                addtrain,
                                addtest,
                                n_components,
                                use_pca = 0.0,
                                use_tsvd = 0.0,
                                use_ica = 0.0,
                                use_fa = 0.0,
                                use_grp = 0.0,
                                use_srp = 0.0,
                                use_pls = 0.0 ):
    N_COMP = int(n_components  * train.shape[1]) + 1
    print("\nStart decomposition process...")
    train_decomposed = np.concatenate([addtrain], axis=1)
    test_decomposed = np.concatenate([addtest], axis=1)
    if use_pca>0.0:
        print("PCA")
        N_COMP = int(use_pca  * train.shape[1]) +1
        pca = PCA(n_components = N_COMP, whiten=True, svd_solver="full", random_state = 42)
        pca_results = pca.fit(total)
        pca_results_train = pca.transform(train)
        pca_results_test = pca.transform(test)
        train_decomposed = np.concatenate([pca_results_train,train_decomposed], axis=1)
        test_decomposed = np.concatenate([pca_results_test, test_decomposed], axis=1)

    if use_tsvd>0.0:
        print("tSVD")
        N_COMP = int(use_tsvd  * train.shape[1]) +1
        tsvd = TruncatedSVD(n_components = N_COMP, random_state=42)
        tsvd_results = tsvd.fit(total)
        tsvd_results_train = tsvd.transform(train)
        tsvd_results_test = tsvd.transform(test)
        train_decomposed = np.concatenate([tsvd_results_train,train_decomposed], axis=1)
        test_decomposed = np.concatenate([tsvd_results_test, test_decomposed], axis=1)

    if use_ica>0.0:
        print("ICA")
        N_COMP = int(use_ica  * train.shape[1]) +1
        ica = FastICA(n_components = N_COMP, random_state=42)
        ica_results = ica.fit(total)
        ica_results_train = ica.transform(train)
        ica_results_test = ica.transform(test)
        train_decomposed = np.concatenate([ica_results_train,train_decomposed], axis=1)
        test_decomposed = np.concatenate([ica_results_test, test_decomposed], axis=1)

    if use_fa>0.0:
        print("FA")
        N_COMP = int(use_fa  * train.shape[1]) +1
        fa = FactorAnalysis(n_components = N_COMP, random_state=42)
        fa_results = fa.fit(total)
        fa_results_train = fa.transform(train)
        fa_results_test = fa.transform(test)
        train_decomposed = np.concatenate([fa_results_train,train_decomposed], axis=1)
        test_decomposed = np.concatenate([fa_results_test, test_decomposed], axis=1)

    if use_grp>0.0:
        print("GRP")
        N_COMP = int(use_grp  * train.shape[1]) +1
        grp = GaussianRandomProjection(n_components = N_COMP, eps=0.1, random_state=42)
        grp_results = grp.fit(total)
        grp_results_train = grp.transform(train)
        grp_results_test = grp.transform(test)
        train_decomposed = np.concatenate([grp_results_train,train_decomposed], axis=1)
        test_decomposed = np.concatenate([grp_results_test, test_decomposed], axis=1)

    if use_srp>0.0:
        print("SRP")
        N_COMP = int(use_srp  * train.shape[1]) +1
        srp = SparseRandomProjection(n_components = N_COMP, dense_output=True, random_state=42)
        srp_results = srp.fit(total)
        srp_results_train = srp.transform(train)
        srp_results_test = srp.transform(test)
        train_decomposed = np.concatenate([srp_results_train,train_decomposed], axis=1)
        test_decomposed = np.concatenate([srp_results_test, test_decomposed], axis=1)

    if use_pls>0.0:
        print("PLS")
        #N_COMP = int(use_pls  * train.shape[1]) +1
        #pls = PLSCanonical(n_components = N_COMP)
        #pls_results = pls.fit(total)
        #pls_results_train = pls.transform(train)
        #pls_results_test = pls.transform(test)
        #train_decomposed = np.concatenate([pls_results_train,train_decomposed], axis=1)
        #test_decomposed = np.concatenate([pls_results_test, test_decomposed], axis=1)

        
    print("Append decomposition components together...")

    train_with_only_decomposed_features = pd.DataFrame(train_decomposed)
    test_with_only_decomposed_features = pd.DataFrame(test_decomposed)

    #for agg_col in ['sum', 'var', 'mean', 'median', 'std', 'weight_count', 'count_non_0', 'num_different', 'max', 'min']:
    #    train_with_only_decomposed_features[col] = train[col]
    #    test_with_only_decomposed_features[col] = test[col]

    # Remove any NA
    train_with_only_decomposed_features = train_with_only_decomposed_features.fillna(0)
    test_with_only_decomposed_features = test_with_only_decomposed_features.fillna(0)

    return train_with_only_decomposed_features, test_with_only_decomposed_features

print("train pca... ")
trainDecomp, testDecomp = DecomposedFeatures(train=data, test=testdata, total=fulldata, 
                                      addtrain=x_trainTOPRF, addtest=x_testTOPRF, n_components=0.97,
                                      use_pca = 0.975,
                                      use_tsvd = 0.00,
                                      use_ica = 0.00,
                                      use_fa = 0.00,
                                      use_grp=0.01,
                                      use_srp=0.00,
                                       use_pls=0.00)
print("trainDecomp {}".format(trainDecomp.shape) )
print("testDecomp {}".format(testDecomp.shape) )

# In[24]:


# In[ ]:


# In[ ]:

def get_training_set_with_test_set_similarity_predictions(X_train, Y_train, X_test):
    from catboost import CatBoostClassifier
    xclf=CatBoostClassifier(iterations=111,
                           depth=5,
                           border_count=121,
                           learning_rate=0.057, loss_function='Logloss',
                           thread_count=8)
    print("Add target column")
    X_train['target'] = Y_train
    X_test['target'] = 0

    X_train["is_test"] = 0
    X_test["is_test"] = 1
    assert(np.all(data.columns == testdata.columns))
    print("Concat train and test data")
    total = pd.concat([X_train,X_train,X_train,X_train,X_train,X_train, X_test])
    total = total.fillna(0)

    x = total.drop(["is_test", "target"], axis = 1)
    y = total.is_test
    print("Start cross-validating")
    rfcls = RandomForestClassifier(n_estimators = 115, n_jobs = -2)
 
    x_train, x_test, y_train, y_test = train_test_split(x, y, stratify = y, test_size = 0.25, random_state = 42)    
    print("fit RF - " )
    rfcls.fit(x, y)
    predicted_probabilities = rfcls.predict_proba(x_test)[:, 1]
    auc = roc_auc_score(y_test, predicted_probabilities)
    print("AUC Score - " + str(auc) + "%")

    print("adversal training set ...")
    df_Prob = pd.DataFrame(rfcls.predict_proba(X_test.drop(["is_test", "target"], axis = 1)), columns=rfcls.classes_)
    print(df_Prob.head(5))
    X_test = X_test.assign( prob_test = df_Prob[[1]])

    print("adversal test set ...")

    df_Prob = pd.DataFrame(rfcls.predict_proba(X_train.drop(["is_test", "target"], axis = 1)), columns=rfcls.classes_)
    print(df_Prob.head(5))
    X_train = X_train.assign( prob_test = df_Prob[[1]])

    print("fit catboost - " )
    xclf.fit(x, y)
    xpredicted_probabilities = xclf.predict_proba(x_test)[:, 1]
    xauc = roc_auc_score(y_test, xpredicted_probabilities)
    print("xAUC Score - " + str(xauc) + "%")

    print("Boost adversal training set ...")
    xdf_Prob = pd.DataFrame(xclf.predict_proba(X_train.drop(["is_test", "target"], axis = 1)), columns=xclf.classes_)
    print(xdf_Prob.head(5))
    X_train = X_train.assign( prob_test = (df_Prob[[1]]+ xdf_Prob[[1]])/2)

    print("Boost adversal test set ...")
    xdf_Prob = pd.DataFrame(xclf.predict_proba(X_test.drop(["is_test", "target"], axis = 1)), columns=xclf.classes_)
    print(xdf_Prob.head(5))
    X_test = X_test.assign( prob_test = (df_Prob[[1]]+ xdf_Prob[[1]])/2)
    
    return X_train, X_test


#================================================================================
#================================================================================
#================================================================================



# In[ ]:

train_set_with_predictions_for_test_set_similarity, X_test =  get_training_set_with_test_set_similarity_predictions(X_train=x_trainTOPRF,
                                                                                                                    Y_train=YBC,
                                                                                                                    X_test=x_testTOPRF)

print("train_set_with_predictions_for_test_set_similarity {}".format(train_set_with_predictions_for_test_set_similarity.shape))
# In[ ]:


# In[29]:


# In[27]:
def AdversarialTrainVal(train, test ):
    x_test = test.drop(["is_test", "target"], 1)
    train = train.sort_values(by=['prob_test'], ascending=False)
    Xtrain = train.nlargest(int(train.shape[0]*0.86), 'prob_test')
    Xtrain = Xtrain.append(train.nlargest(int(train.shape[0]*0.54), 'prob_test'))
    Xtrain = Xtrain.append(train.nlargest(int(train.shape[0]*0.44), 'prob_test'))
    Xtrain = Xtrain.append(train.nlargest(int(train.shape[0]*0.51), 'prob_test'))
    Xtrain = Xtrain.append(train.nlargest(int(train.shape[0]*0.31), 'prob_test'))
    for i in range(200):
        Xtrain = Xtrain.append(train[ train["prob_test"] > 0.80 ])
        Xtrain = Xtrain.append(train[ train["prob_test"] > 0.70 ])
    for i in range(110):
        Xtrain = Xtrain.append(train[ train["prob_test"] > 0.60 ])
    for i in range(50):
        Xtrain = Xtrain.append(train[ train["prob_test"] >= 0.5 ])
    for i in range(5):
        Xtrain = Xtrain.append(train[ train["prob_test"] > 0.49 ])
    for i in range(1):
        Xtrain = Xtrain.append(train[ train["prob_test"] > 0.35 ])

    Xtrain = Xtrain.drop(["is_test"], 1)

    #Xtrain = Xtrain.append(train)
    
    val = train.nsmallest(int(train.shape[0]*0.86), 'prob_test')
    val = val.append(train.nsmallest(int(train.shape[0]*0.9), 'prob_test'))
    val = val.append(train.nlargest(int(train.shape[0]*0.86), 'prob_test'))
    val = val.drop(["is_test"], 1)
    
    x_train, y_train = Xtrain.drop("target", 1), Xtrain.target
    x_val, y_val = val.drop("target", 1), val.target
    return x_train, y_train, x_val, y_val, x_test

x_train, y_train, x_val, y_val, x_test = AdversarialTrainVal(train=train_set_with_predictions_for_test_set_similarity, test=X_test )

[ print("  {}".format(x.shape)) for x in [x_train, y_train, x_val, y_val, x_test] ] 


# In[30]:


# In[ ]:

import matplotlib.pyplot as plt
from numpy import genfromtxt
from sklearn.metrics import mean_squared_error
from math import sqrt


"""
kernel = C(1.0, (1e-3, 1e3)) * RBF(10, (1e-2, 1e2))
gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=9)
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
# Fit to data using Maximum Likelihood Estimation of the parameters
gp.fit(x_train, y_train)
# Make the prediction on the meshed x-axis (ask for MSE as well)
y_gppred, sigma = gp.predict(x_val, return_std=True)
trainrms = sqrt(mean_squared_error( np.expm1(y_val ), np.expm1(y_gppred) ))
print("y_lgbmx1  trainrms {}".format(  trainrms ) )
"""


# In[ ]:

from catboost import CatBoostRegressor
lgbm2 = lgb.LGBMRegressor(objective='regression',
                        num_leaves=21,
                        min_data_in_leaf=2,
                        learning_rate= 0.021,
                        feature_fraction= 0.9,
                        bagging_fraction= 0.8,
                        bagging_freq= 4,
                        verbose= -1,
                        num_threads=4,
                        n_estimators=2111)

catgbmx1=CatBoostRegressor(iterations=1110,
                           depth=8,
                           border_count=126,
                           learning_rate=0.026, loss_function='RMSE',
                           thread_count=6)
#catgbmx1.fit(x_train, y_train, eval_set=(x_val, y_val),plot=False, use_best_model=True)
lgbm2.fit(x_train, y_train, eval_set=[(x_val, y_val)], eval_metric='l2',  early_stopping_rounds=111)

# In[ ]:


# In[ ]:


y_lgbm2 = lgbm2.predict(x_val)
trainrms = sqrt(mean_squared_error( np.expm1(y_val), np.expm1(y_lgbm2)))
print("lgbm2 trainrms {}".format(  trainrms ) )


# In[ ]:


# In[ ]:


# In[82]:
lgbm1 = lgb.LGBMRegressor(objective='regression',
                        num_leaves=31,
                        min_data_in_leaf=2,
                        learning_rate= 0.021,
                        feature_fraction= 0.9,
                        bagging_fraction= 0.8,
                        bagging_freq= 4,
                        verbose= -1,
                        num_threads=4,
                        n_estimators=3111)

lgbm1.fit(x_train, y_train, eval_set=[(x_val, y_val)], eval_metric='l1',  early_stopping_rounds=511)


# In[ ]:


# In[ ]:


# In[ ]:

y_lgbmx1 = lgbm1.predict(x_val)
trainrms = sqrt(mean_squared_error( np.expm1(y_val ), np.expm1(y_lgbmx1 ) ))
print("y_lgbmx1  trainrms {}".format(  trainrms ) )


# In[6]:


# In[ ]:


# In[31]:


# In[89]:
print("Predict  lgbm1...")
ytest_lgbm1= np.expm1(lgbm1.predict(x_test ))

# In[89]:
print("Predict  catgbmx1...")
ytest_catgbmx1= np.expm1(lgbm2.predict(x_test ))


# In[ ]:

plt.figure(figsize=(11,11))
plt.scatter(range(0,len(ytest_lgbm1)), ytest_lgbm1, s=100,  marker="s", label='ytest_lgbm1')
plt.xlabel('index', fontsize=12)
plt.ylabel('ytest_lgbm1 ', fontsize=12)
plt.title("ytest_lgbm1 Distribution", fontsize=14)
plt.show()
plt.figure(figsize=(11,11))
plt.scatter(range(0,len(ytest_catgbmx1)), ytest_catgbmx1, s=100,  marker="s", label='ytest_lgbmClass1')
plt.xlabel('index', fontsize=12)
plt.ylabel('ytest_catgbmx1 ', fontsize=12)
plt.title("ytest_catgbmx1 Distribution", fontsize=14)
plt.show()


plt.figure(figsize=(11,11))
plt.scatter( ytest_lgbm1 , ytest_catgbmx1, s=100,  marker="s", label='lgbm1_RFT ' )
plt.xlabel('ytest_lgbm1', fontsize=12)
plt.ylabel('ytest_catgbmx1 ', fontsize=12)
plt.title("ytest_lgytest_catgbmx1 bmClass1 lgbm1 Distribution", fontsize=14)
plt.show()


# In[34]:


# In[ ]:


ypredavg = pd.DataFrame(dict(
    XCATGB1=ytest_catgbmx1,
    LGB1=ytest_lgbm1,
    AVG= (ytest_lgbm1 + ytest_catgbmx1 )/2  ) )

print(ypredavg.columns)
ypredavg.to_csv(filepath + "/tmp/FinalFinal.csv", index=False)
print(ypredavg.mean())
print(ypredavg.std())


# In[ ]:


# In[35]:


# In[93]:
ySubmit = pd.DataFrame(dict( ID=testID,target=(ypredavg["AVG"] )))
ySubmit.to_csv(filepath + "/tmp/submit.csv", index=False)
print(ySubmit.shape)

