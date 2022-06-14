from sklearn.datasets import load_iris 
from sklearn.model_selection import train_test_split 
from sklearn.metrics import accuracy_score 

from sklearn.ensemble import ExtraTreesClassifier 
from sklearn.ensemble import RandomForestClassifier 
from xgboost import XGBClassifier 
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier

from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import LabelEncoder

from vecstack import stacking 

import numpy as np
import pandas as pd

def hot_encoding(df):
    enc = OneHotEncoder(handle_unknown='ignore', sparse=False)
    lab = LabelEncoder()    

    dat = df['packer_type']
    lab.fit(dat)
    lab_dat = lab.transform(dat)

    df = df.drop('packer_type', 1)
    lab_dat = lab_dat.reshape(len(lab_dat), 1)
    enc_dat = enc.fit_transform(lab_dat)
    enc_dat = pd.DataFrame(enc_dat, columns=lab.classes_)

    df = df.reset_index(drop=True)
    enc_dat = enc_dat.reset_index(drop=True)
    
    df = pd.concat([df, enc_dat], axis=1)

    return df, lab.classes_

pe_all = pd.read_csv('./DataSet/PE/pe_header_all.csv')
pe_all = pe_all.drop(['filename', 'MD5'], 1)
#gram_all = pd.read_csv('./DataSet/ngram/4gram_all.csv')
#gram_all = gram_all.drop(['filename', 'MD5'], 1) 

#y = gram_all['class']
#X = gram_all.drop('class', 1) 
pe_all, classes_ = hot_encoding(pe_all)

pe_all = pd.DataFrame(pe_all)
pe_all.to_csv('pe_packer.csv', index=False)

y = pe_all['class']
X = pe_all.drop('class',1)


# Load demo data 
#iris = load_iris() 

#	X, y = , iris.target 
	# Make train/test split 
	# As usual in machine learning task we have X_train, y_train, and X_test 
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 0) 
	# Caution! All models and parameter values are just 
	# demonstrational and shouldn't be considered as recommended. 
	# Initialize 1-st level models. 

models = [ 
	#learning_rate=학습률, n_estimators = 반복하려는 트리의 개수, max_depth =트리의 최대 깊이

	ExtraTreesClassifier(random_state = 42, n_estimators = 1000), 
	RandomForestClassifier(n_estimators = 1000), 	
	#CatBoostClassifier(learning_rate=0.1),
	LGBMClassifier(seed = 0, num_leaves=123, learning_rate = 0.05, n_estimators = 1500, max_depth = -1),	
	XGBClassifier(colsample_bytree=0.8, seed = 27, n_jobs = 4, learning_rate = 0.1, n_estimators = 1500, max_depth =5)]

	# Compute stacking features 
S_train, S_test = stacking(models, X_train, y_train, X_test, regression = False, metric = accuracy_score, n_folds = 7, stratified = True, shuffle = True, random_state = 42, verbose = 2) 
	# Initialize 2-nd level model 
model = XGBClassifier(colsample_bytree=0.8, seed = 27, n_jobs = -1, learning_rate = 0.1, n_estimators = 1500, max_depth =3) 
	# Fit 2-nd level model 
model = model.fit(S_train, y_train) 
	# Predict 
y_pred = model.predict(S_test) 

	# Final prediction score 
print('Final prediction score: [%.8f]' % accuracy_score(y_test, y_pred))