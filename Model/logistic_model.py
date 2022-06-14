from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import LabelEncoder

import pandas as pd
import numpy as np

class Classifiers():

	def __init__(self, X, Y):
		labels = np.unique(Y)
		self.x_train, self.x_test, self.y_train, self.y_test = \
		train_test_split(X, Y, test_size=0.2, random_state=0)

	def do_logistic(self):
		LR = LogisticRegression()
		LR.fit(self.x_train, self.y_train)
		y_pred = LR.predict(self.x_test)

		return accuracy_score(self.y_test, y_pred)

	def do_all(self):
		rns = []
		rns.append(self.do_logistic())
		return rns
	
#pe.csv에서 pe_packer column특징을 사용하지 않음
def pe_predit(pe_all):
	NA_values = pe_all.isnull().values.sum()
	pe_all = pe_all.dropna()

	pe_all = pe_all.drop(['filename', 'MD5', 'packer_type'], 1)
	
	Y = pe_all['class']
	X = pe_all.drop('class',1)
	Y_bak = Y

	md_pe = Classifiers(X,Y)
	
	return md_pe.do_all()

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

#pe.csv에서 pe_packer column특징을 사용하기 위해 전처리 > one-hot encoding사용
def pe_packer(pe_all):	 
	pe_all = pe_all.drop(['filename', 'MD5'], 1)

	pe_all, classes_ = hot_encoding(pe_all)

	pe_all = pd.DataFrame(pe_all)
	pe_all.to_csv('pe_packer.csv', index=False)

	Y = pe_all['class'] 
	X = pe_all.drop('class', axis=1)

	md_pe_packer = Classifiers(X, Y)
	
	return md_pe_packer.do_all()	

def gram(ngram):	
	ngram = ngram.drop(['filename', 'MD5'], 1) 

	Y = ngram['class']
	X = ngram.drop('class', 1) 
	md_gram = Classifiers(X, Y)

	return md_gram.do_all()

def main():
	colum = ["logistic"]
	df = pd.DataFrame(columns=colum)

	pe_all = pd.read_csv('./DataSet/PE/pe_header_all.csv')
	ngram = pd.read_csv('./DataSet/ngram/ngram_all.csv')

	print(ngram.shape)

	df.loc['pe'] = pe_predit(pe_all)
	df.loc['pe_packer'] = pe_packer(pe_all)
	df.loc['ngram'] = gram(ngram)

	avg_pe = df.loc['pe'].mean(axis=0)
	avg_ngram = df.loc['ngram'].mean(axis=0)
	
	print(df)

if __name__ == '__main__':
	main()
