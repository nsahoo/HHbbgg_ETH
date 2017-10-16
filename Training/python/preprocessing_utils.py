import training_utils as utils
import os
import numpy as np
import pandas as pd
import root_pandas as rpd


def define_process_weight(df,proc,name,cleanSignal=True):
    df['proc'] = ( np.ones_like(df.index)*proc ).astype(np.int8)
    df['weight'] = ( np.ones_like(df.index)).astype(np.float32)
    input_df=rpd.read_root(name,"bbggSelectionTree", columns = ['genTotalWeight', 'lumiFactor','isSignal','puweight'])
    w = np.multiply(input_df[['lumiFactor']],input_df[['genTotalWeight']])
    w = np.multiply(w,input_df[['puweight']])
    df['lumiFactor'] = input_df[['lumiFactor']]
    df['genTotalWeight'] = input_df[['genTotalWeight']]
    df['isS`ignal'] = input_df[['isSignal']]
    if cleanSignal:#some trees include also the control region,select only good events
        df['weight']= np.multiply(w,input_df[['isSignal']])
    else:
        df['weight']=w



def define_process_weight_CR(df,proc,name):
    df['proc'] = ( np.ones_like(df.index)*proc ).astype(np.int8)
    df['weight'] = ( np.ones_like(df.index)).astype(np.float32)
    input_df=rpd.read_root(name,"bbggSelectionTree", columns = ['isPhotonCR'])
    w = input_df[['isPhotonCR']]
    df['weight']=w

 
def clean_signal_events(x_b, y_b, w_b,x_s,y_s,w_s):#some trees include also the control region,select only good events
    return x_b[np.where(w_b!=0),:][0],y_b[np.where(w_b!=0)],w_b[np.where(w_b!=0)], x_s[np.where(w_s!=0),:][0], np.asarray(y_s)[np.where(w_s!=0)],np.asarray(w_s)[np.where(w_s!=0)]

 
def clean_signal_events_single_dataset(x_b, y_b, w_b):#some trees include also the control region,select only good events
    return x_b[np.where(w_b!=0),:][0],np.asarray(y_b)[np.where(w_b!=0)],np.asarray(w_b)[np.where(w_b!=0)]

    
                       
def normalize_process_weights(w_b,y_b,w_s,y_s):
    proc=999
    sum_weights = 1
    w_bkg = []
    for i in range(utils.IO.nBkg):
        if utils.IO.bkgProc[i] != proc:
            w_proc = np.asarray(np.absolute(w_b[np.asarray(y_b) == utils.IO.bkgProc[i]]))#absolute is important to normalize in case of negative weights
            sum_weights = float(np.sum(w_proc))
            proc = utils.IO.bkgProc[i]
        if i==0:
            w_bkg = np.divide(w_proc,sum_weights)
        else:
            w_bkg = np.concatenate((w_bkg, np.divide(w_proc,sum_weights)))
        utils.IO.background_df[i][['weight']] = np.divide(utils.IO.background_df[i][['weight']],sum_weights)

    proc=999
    sum_weights = 1
    w_sig = []
    for i in range(utils.IO.nSig):
        if utils.IO.sigProc[i] != proc:
            w_proc = np.asarray(w_s[np.asarray(y_s) == utils.IO.sigProc[i]])
            sum_weights = np.sum(w_proc)
            proc = utils.IO.sigProc[i]
        if i==0:
            w_sig = np.divide(w_proc,sum_weights)
        else:
            w_sig = np.concatenate((w_sig, np.divide(w_proc,sum_weights)))
        utils.IO.signal_df[i][['weight']] = np.divide(utils.IO.signal_df[i][['weight']],sum_weights)



    return w_bkg,w_sig
        

def weight_signal_with_resolution(w_s,y_s):
    proc=999
    for i in range(utils.IO.nSig):
         w_sig = np.asarray(w_s[np.asarray(y_s) == utils.IO.sigProc[i]])
	 proc = utils.IO.sigProc[i]
	 utils.IO.signal_df[i][['weight']] = np.divide(utils.IO.signal_df[i][['weight']],utils.IO.signal_df[i][['sigmaMOverMDecorr']])

    return utils.IO.signal_df[i][['weight']]

def weight_background_with_resolution(w_b,y_b,proc):
    w_bkg = []
    process=999
    for i in range(utils.IO.nBkg):
        if utils.IO.bkgProc[i] == proc:
            utils.IO.background_df[i][['weight']] = np.divide(utils.IO.background_df[i][['weight']],utils.IO.background_df[i][['sigmaMOverMDecorr']])
            w_proc = np.asarray(utils.IO.background_df[i][['weight']])
            np.reshape(w_proc,(len(utils.IO.background_df[i][['weight']]),))
        else:
            if process == utils.IO.bkgProc[i]: #don't do twice multiple samples of same process, like GJet
                continue
            process =  utils.IO.bkgProc[i]
        
            w_proc = np.asarray(w_b[np.asarray(y_b) == utils.IO.bkgProc[i]])

        if i == 0:
            w_bkg = w_proc
        else:
            w_bkg =  np.concatenate((w_bkg,np.asarray(w_proc.ravel())))
        
            
    return w_bkg.reshape(len(w_bkg),1)




def get_training_sample(x,splitting=0.5):
    halfSample = int((x.size/len(x.columns))*splitting)
    return np.split(x,[halfSample])[0]


def get_test_sample(x,splitting=0.5):
    halfSample = int((x.size/len(x.columns))*splitting)
    return np.split(x,[halfSample])[1]

    
def get_total_training_sample(x_sig,x_bkg,splitting=0.5):
    x_s=pd.DataFrame(x_sig)
    x_b=pd.DataFrame(x_bkg)
    halfSample_s = int((x_s.size/len(x_s.columns))*splitting)
    halfSample_b = int((x_b.size/len(x_b.columns))*splitting)
    return np.concatenate([np.split(x_s,[halfSample_s])[0],np.split(x_b,[halfSample_b])[0]])

    
def get_total_test_sample(x_sig,x_bkg,splitting=0.5):
    x_s=pd.DataFrame(x_sig)
    x_b=pd.DataFrame(x_bkg)
    halfSample_s = int((x_s.size/len(x_s.columns))*splitting)
    halfSample_b = int((x_b.size/len(x_b.columns))*splitting)
    return np.concatenate([np.split(x_s,[halfSample_s])[1],np.split(x_b,[halfSample_b])[1]])


def set_signals(treeName,branch_names,shuffle):
    for i in range(utils.IO.nSig):
        utils.IO.signal_df.append(rpd.read_root(utils.IO.signalName[i],"bbggSelectionTree", columns = branch_names))
        define_process_weight(utils.IO.signal_df[i],utils.IO.sigProc[i],utils.IO.signalName[i])
        if shuffle:
            utils.IO.signal_df[i]['random_index'] = np.random.permutation(range(utils.IO.signal_df[i].index.size))
            utils.IO.signal_df[i].sort_values(by='random_index',inplace=True)
            
#         adjust_and_compress(utils.IO.signal_df[i]).to_hdf('/tmp/micheli/signal.hd5','sig',compression=9,complib='bzip2',mode='a')

    

def set_backgrounds(treeName,branch_names,shuffle):
    for i in range(utils.IO.nBkg):
        utils.IO.background_df.append(rpd.read_root(utils.IO.backgroundName[i],"bbggSelectionTree", columns = branch_names))
        define_process_weight(utils.IO.background_df[i],utils.IO.bkgProc[i],utils.IO.backgroundName[i])
        if shuffle:
            utils.IO.background_df[i]['random_index'] = np.random.permutation(range(utils.IO.background_df[i].index.size))
            utils.IO.background_df[i].sort_values(by='random_index',inplace=True)

#         adjust_and_compress(utils.IO.background_df[i]).to_hdf('/tmp/micheli/background.hd5','bkg',compression=9,complib='bzip2',mode='a')



def set_data(treeName,branch_names):
    utils.IO.data_df.append(rpd.read_root(utils.IO.dataName[0],"bbggSelectionTree", columns = branch_names))
    utils.IO.data_df[0]['proc'] =  ( np.ones_like(utils.IO.data_df[0].index)*utils.IO.dataProc[0] ).astype(np.int8)
    input_df=rpd.read_root(utils.IO.dataName[0],"bbggSelectionTree", columns = ['isSignal'])
    w = (np.ones_like(utils.IO.data_df[0].index)).astype(np.int8)
    utils.IO.data_df[0]['weight'] = np.multiply(w,input_df['isSignal'])

    y_data = utils.IO.data_df[0][['proc']]
    w_data = utils.IO.data_df[0][['weight']]

    for j in range(len(branch_names)):
        if j == 0:
            X_data = utils.IO.data_df[0][[branch_names[j].replace('noexpand:','')]]
        else:
            X_data = np.concatenate([X_data,utils.IO.data_df[0][[branch_names[j].replace('noexpand:','')]]],axis=1)
    
    return np.round(X_data,5),y_data,w_data
    
    

def set_signals_and_backgrounds(treeName,branch_names,shuffle=True):
    #signals will have positive process number while bkg negative ones
    set_signals(treeName,branch_names,shuffle)
    set_backgrounds(treeName,branch_names,shuffle)


def randomize(X,y,w):
    randomize=np.arange(len(X))
    np.random.shuffle(randomize)
    X = X[randomize]
    y = np.asarray(y)[randomize]
    w = np.asarray(w)[randomize]

    return X,y,w


 
def set_variables(branch_names):
    for i in range(utils.IO.nSig):
        if i ==0:
            y_sig = utils.IO.signal_df[i][['proc']]
            w_sig = utils.IO.signal_df[i][['weight']]
            for j in range(len(branch_names)):
                if j == 0:
                    X_sig = utils.IO.signal_df[i][[branch_names[j].replace('noexpand:','')]]
                else:
                    X_sig = np.concatenate([X_sig,utils.IO.signal_df[i][[branch_names[j].replace('noexpand:','')]]],axis=1)
        else:
            y_sig = np.concatenate((y_sig,utils.IO.signal_df[i][['proc']]))
            w_sig = np.concatenate((w_sig,utils.IO.signal_df[i][['weight']]))
            for j in range(len(branch_names)):
                if j == 0:
                    X_sig_2 = utils.IO.signal_df[i][[branch_names[j].replace('noexpand:','')]]
                else:
                    X_sig_2 = np.concatenate([X_sig_2,utils.IO.signal_df[i][[branch_names[j].replace('noexpand:','')]]],axis=1)
            X_sig=np.concatenate((X_sig,X_sig_2))

    for i in range(utils.IO.nBkg):
        if i ==0:
            y_bkg = utils.IO.background_df[i][['proc']]
            w_bkg = utils.IO.background_df[i][['weight']]
            for j in range(len(branch_names)):
                if j == 0:
                    X_bkg = utils.IO.background_df[i][[branch_names[j].replace('noexpand:','')]]
                else:
                    X_bkg = np.concatenate([X_bkg,utils.IO.background_df[i][[branch_names[j].replace('noexpand:','')]]],axis=1)
        else:
            y_bkg = np.concatenate((y_bkg,utils.IO.background_df[i][['proc']]))
            w_bkg = np.concatenate((w_bkg,utils.IO.background_df[i][['weight']]))
            for j in range(len(branch_names)):
                if j == 0:
                    X_bkg_2 = utils.IO.background_df[i][[branch_names[j].replace('noexpand:','')]]
                else:
                    X_bkg_2 = np.concatenate([X_bkg_2,utils.IO.background_df[i][[branch_names[j].replace('noexpand:','')]]],axis=1)
            X_bkg=np.concatenate((X_bkg,X_bkg_2))

    return np.round(X_bkg,5),y_bkg,w_bkg,np.round(X_sig,5),y_sig,w_sig

