import numpy as np
import os
import csv
import operator
from keras.layers.merge import dot
from keras.models import Model
from keras.layers import Input, Dense, Masking, Dropout, LSTM, Bidirectional, Activation
from keras.layers import TimeDistributed
from keras.layers import AveragePooling1D
from keras.layers import Flatten
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import LSTM
from keras.layers import Bidirectional
from keras.models import load_model
from keras.optimizers import SGD, Adam, RMSprop
import matplotlib.pyplot as plt
from sklearn import svm, datasets
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from keras.utils import np_utils
import itertools
np.seterr(divide='ignore', invalid='ignore')


def plot_confusion_matrix(cm, classes, normalize=False, title='Confusion matrix', cmap=plt.cm):
    
    plt.figure(figsize=(4,7))
    
    #NOT NORMALIZED
    print('Confusion matrix, without normalization')
    print(cm)
    plt.subplot(2, 1, 1)
    plt.imshow(cm, interpolation='nearest', cmap=cmap.Blues)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    fmt = 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    
    #NORMALIZED
    cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    print("Normalized confusion matrix")
    print(cm)
    plt.subplot(2, 1, 2)
    plt.imshow(cm, interpolation='nearest', cmap=cmap.Blues)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    fmt = '.2f'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    
    return plt


def computeConfMatrix(allPredictionClasses, expected, dirRes, nameFileResult, flagPlotGraph):
    labelLimit = 170
    expected = np.argmax(expected, axis=1)
    cm = confusion_matrix(expected, allPredictionClasses)
    accurancy = (cm[0][0] + cm[1][1] + cm[2][2] + cm[3][3])/(labelLimit*4)
    print('Accurancy: ',accurancy)
    plt = plot_confusion_matrix(cm, ['joy','ang','sad','neu'], title=nameFileResult+'-CM')
    
    OutputImgPath = os.path.join(dirRes, nameFileResult+'-Acc_'+str(accurancy)+'-CM.png')
    plt.savefig(OutputImgPath)
    if flagPlotGraph:
        plt.show()
    
    
def statistics(Y, yhat, correctCounter, predEmoCounter):
    index, value = max(enumerate(Y[0]), key=operator.itemgetter(1))
    Pindex, Pvalue = max(enumerate(yhat[0]), key=operator.itemgetter(1))
    '''print('index: ', index, 'value: ', value)
    print('index: ', Pindex, 'value: ', Pvalue)'''
    
    #UPDATE CORRECT COUNTER
    if index == Pindex:
        correctCounter[index] += 1
    
    #UPDATE PREDICTED EMO COUNTER
    predEmoCounter[Pindex] += 1
    
    return correctCounter, predEmoCounter


def saveCsv(currentFile, csvOutputFilePath):
    csvOutputFilePath = os.path.join(csvOutputFilePath + '.csv')
    try:
        os.remove(csvOutputFilePath)
    except OSError:
        pass
    
    with open(csvOutputFilePath, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(np.asarray(currentFile))
    f.close() 

    
def saveTxt(currentFile, txtOutputFilePath): 
    txtOutputFilePath = os.path.join(txtOutputFilePath + '.txt') 
    try:
        os.remove(txtOutputFilePath)
    except OSError:
        pass
    
    with open(txtOutputFilePath, 'w') as file:      
        for item in currentFile:
            file.write(str(item)+'\n')  
    file.close() 


def readFeatures(DirRoot, labelLimit):
    listA = [ item for item in os.listdir(DirRoot) if os.path.isfile(os.path.join(DirRoot, item)) ]
    allFileFeature = []
    allFileName = []
    
    i = 0
    #READ encoded audio Features
    for file in listA:
        allFileName.append(file)
        datareader = csv.reader(open(os.path.join(DirRoot, file), 'r'))
        data = []
        for row in datareader:
            data.append([float(val) for val in row])
        Y = np.array([np.array(xi) for xi in data])
        
        #Append all files feature in an unique array
        allFileFeature.append(Y)
        
        if i > labelLimit-1:
            break
        else:
            i += 1
        
    allFileFeature = np.asarray(allFileFeature)
    
    return allFileFeature, allFileName


def organizeFeatures(dirAudio, dirText, dirLabel, labelLimit):

    joyAudioFeature, joyFileName = readFeatures(os.path.join(dirAudio, 'joy'), labelLimit)
    angAudioFeature, angFileName = readFeatures(os.path.join(dirAudio, 'ang'), labelLimit)
    sadAudioFeature, sadFileName = readFeatures(os.path.join(dirAudio, 'sad'), labelLimit)
    neuAudioFeature, neuFileName = readFeatures(os.path.join(dirAudio, 'neu'), labelLimit)
    joyTextFeature, allFileName = readFeatures(os.path.join(dirText, 'joy'), labelLimit)
    angTextFeature, angFileName = readFeatures(os.path.join(dirText, 'ang'), labelLimit)
    sadTextFeature, sadFileName = readFeatures(os.path.join(dirText, 'sad'), labelLimit)
    neuTextFeature, neuFileName = readFeatures(os.path.join(dirText, 'neu'), labelLimit)
    joyLabels, joyFileName = readFeatures(os.path.join(dirLabel, 'joy'), labelLimit)
    angLabels, angFileName = readFeatures(os.path.join(dirLabel, 'ang'), labelLimit)
    sadLabels, sadFileName = readFeatures(os.path.join(dirLabel, 'sad'), labelLimit)
    neuLabels, neuFileName = readFeatures(os.path.join(dirLabel, 'neu'), labelLimit)
    '''print(allAudioFeature.shape)
    print(allTextFeature.shape)
    print(allLabels.shape)'''
    
    #BUILD SHUFFLED FEATURE FILES FOR TRAINING
    allAudioFeature = []
    allTextFeature = []
    allFileName = []
    allLabels = []
    i = 0
    while i < labelLimit:
        allAudioFeature.append(joyAudioFeature[i])
        allAudioFeature.append(angAudioFeature[i])
        allAudioFeature.append(sadAudioFeature[i])
        allAudioFeature.append(neuAudioFeature[i])
        
        allTextFeature.append(joyTextFeature[i])
        allTextFeature.append(angTextFeature[i])
        allTextFeature.append(sadTextFeature[i])
        allTextFeature.append(neuTextFeature[i])
        
        allFileName.append(joyFileName[i])
        allFileName.append(angFileName[i])
        allFileName.append(sadFileName[i])
        allFileName.append(neuFileName[i])
        
        allLabels.append(joyLabels[i])
        allLabels.append(angLabels[i])
        allLabels.append(sadLabels[i])
        allLabels.append(neuLabels[i])
        
        i +=1

    return allAudioFeature, allTextFeature, allFileName, allLabels


def buildBLTSM(maxTimestep, numFeatures):
    
    #MODEL WITH ATTENTION
    nb_lstm_cells = 128
    nb_classes = 4
    nb_hidden_units = 512
    # Logistic regression for learning the attention parameters with a standalone feature as input
    input_attention = Input(shape=(nb_lstm_cells * 2,))
    u = Dense(nb_lstm_cells * 2, activation='softmax')(input_attention)
    # Bi-directional Long Short-Term Memory for learning the temporal aggregation
    input_feature = Input(shape=(maxTimestep,numFeatures))
    x = Masking(mask_value=0.)(input_feature)
    x = Dense(nb_hidden_units, activation='relu')(x)
    x = Dropout(0.5)(x)
    x = Dense(nb_hidden_units, activation='relu')(x)
    x = Dropout(0.5)(x)
    y = Bidirectional(LSTM(nb_lstm_cells, return_sequences=True, dropout=0.5))(x)
    # To compute the final weights for the frames which sum to unity
    alpha = dot([u, y], axes=-1)  # inner prod.
    alpha = Activation('softmax')(alpha)
    # Weighted pooling to get the utterance-level representation
    z = dot([alpha, y], axes=1)
    # Get posterior probability for each emotional class
    output = Dense(nb_classes, activation='softmax')(z)
    model = Model(inputs=[input_attention, input_feature], outputs=output)
    #model.compile(loss='categorical_crossentropy', optimizer=RMSprop(lr=0.01, rho=0.9, epsilon=None, decay=0.0), metrics=['categorical_accuracy']) #mean_squared_error #categorical_crossentropy
    model.compile(loss='categorical_crossentropy', optimizer=Adam(), metrics=['categorical_accuracy']) #mean_squared_error #categorical_crossentropy
    
    #MODELLO BASE SEMPLICE
    '''model = Sequential()
    model.add(Bidirectional(LSTM(128, return_sequences=False), input_shape=(maxTimestep, numFeatures)))
    model.add(Dropout(0.5))
    model.add(Dense(512, activation='relu'))
    model.add(Dense(4, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer=RMSprop(lr=0.00001, rho=0.9, epsilon=None, decay=0.0), metrics=['categorical_accuracy']) #mean_squared_error #categorical_crossentropy
    '''
    
    return model


def reshapeLSTMInOut(audFeat, label, maxTimestep):
    X = []
    X = np.asarray(audFeat)
    X = pad_sequences(X, maxlen=maxTimestep, dtype='float32')
    Y = np.asarray(label)
    Y = Y.reshape(len(Y), 4)
    
    return X, Y

 
def predictFromModel(model, inputTest, Labels, fileName, fileLimit, labelLimit, maxTimestep):
    
    allPrediction = []
    allPredictionClasses = []
    expected = []
    emoCounter = np.array([[0],[0],[0],[0]]) #count label to block after labelLimit prediction
    correctCounter = np.array([[0],[0],[0],[0]]) #count correct prediction for each label, last place is for total number of each label
    predEmoCounter = np.array([[0],[0],[0],[0]]) #count how many prediction for each label
    
    #FORMAT X & Y
    X, Y = reshapeLSTMInOut(inputTest, Labels, maxTimestep)
    
    #PREPARE ATTENTION ARRAY INPUT:  training and test
    nb_attention_param = 256
    attention_init_value = 1.0 / 256
    u_train = np.full((X.shape[0], nb_attention_param), attention_init_value, dtype=np.float64)
    
    #PREDICT
    yhat = model.predict([u_train,X])
    for i in range(len(yhat)):
        print('Expected:', Y[i], 'Predicted', yhat[i])
        #print('Expected:', Y[i], 'Predicted', yhat2[i]) 
        Pindex, Pvalue = max(enumerate(yhat[i]), key=operator.itemgetter(1))
        allPredictionClasses.append(Pindex)
        expected.append(Y[i])
    
    #EVALUATE THE MODEL  
    scores = model.evaluate([u_train, X], Y, verbose=0)  
    print('NORMAL EVALUATION %s: %.2f%%' % (model.metrics_names[1], scores[1]*100))                
    
    #K-FOLD EVALUATION
    '''seed = 7
    np.random.seed(seed)
    dummy_y = np_utils.to_categorical(Y) # convert integers to dummy variables (i.e. one hot encoded)
    kfold = KFold(n_splits=10, shuffle=True, random_state=seed)
    results = cross_val_score(model, [u_train, X], dummy_y, cv=kfold)
    print("K-FOLD EVALUATION: %.2f%% (%.2f%%)" % (results.mean()*100, results.std()*100))'''
    
    return allPredictionClasses, expected
    
    
if __name__ == '__main__':
    
    #DEFINE MAIN ROOT
    #mainRootModelFile = os.path.normpath(r'D:\DATA\POLIMI\----TESI-----\Corpus_Training')
    #mainRoot = os.path.normpath(r'D:\DATA\POLIMI\----TESI-----\Corpus_Test')
    mainRootModelFile = os.path.normpath(r'C:\Users\JORIGGI00\Documents\MyDOCs\Corpus_Training')
    mainRoot = os.path.normpath(r'C:\Users\JORIGGI00\Documents\MyDOCs\Corpus_Test')
    
    #BUILD PATH FOR EACH FEATURE DIR
    dirAudio = os.path.join(mainRoot + '\FeaturesAudio')
    dirText = os.path.join(mainRoot + '\FeaturesText')
    dirLabel = os.path.join(mainRoot + '\LablesEmotion')
    #dirRes = os.path.normpath(r'D:\DATA\POLIMI\----TESI-----\Z_Results\Recent_Results')
    dirRes = os.path.normpath(r'C:\Users\JORIGGI00\Documents\MyDOCs\Z_Results\Recent_Results')
    
    #SET MODELS PATH
    mainRootModelAudio = os.path.normpath(mainRootModelFile + '\RNN_Model_AUDIO_saved.h5')
    mainRootModelText = os.path.normpath(mainRootModelFile + '\RNN_Model_TEXT_saved.h5')
    
    #DEFINE PARAMETERS
    modelType = 0 #0=OnlyAudio, 1=OnlyText, 2=Audio&Text
    labelLimit = 170 #Number of each emotion label file to process
    fileLimit = (labelLimit*4) #number of file trained: len(allAudioFeature) or a number
    nameFileResult = 'PredModel'+'-'+'Label_'+str(labelLimit)
    
    #EXTRACT FEATURES, NAMES, LABELS, AND ORGANIZE THEM IN AN ARRAY
    allAudioFeature, allTextFeature, allFileName, allLabels = organizeFeatures(dirAudio, dirText, dirLabel, labelLimit)
    
    #FIND MAX TIMESTEP FOR PADDING
    maxTimestep = 290 #setted with training because no test file is longer than 290
     
    #TRAIN & SAVE LSTM: considering one at time
    if modelType == 0 or modelType == 2:
        model_Audio = load_model(mainRootModelAudio) 
        #OutputWeightsPath = os.path.join(dirRes, 'weights.best.hdf5')  
        #model_Audio = buildBLTSM(maxTimestep, allAudioFeature[0].shape[1])
        #model_Audio.load_weights(OutputWeightsPath)
    if modelType == 1 or modelType == 2:
        modelPathAudio = os.path.normpath(mainRoot + '\RNN_Model_TEXT_saved.h5') 
    
    #MODEL SUMMARY
    model_Audio.summary()
    print('Predict of #file: ', fileLimit)
    print('Files with #features: ', allAudioFeature[0].shape[1])
    print('Max time step: ',maxTimestep)
    print('Predict number of each emotion: ', labelLimit)
    
    #PREDICT & SAVE
    allPredictionClasses, expected = predictFromModel(model_Audio, allAudioFeature, allLabels, allFileName, fileLimit, labelLimit, maxTimestep)
    computeConfMatrix(allPredictionClasses, expected, dirRes, nameFileResult, True)
    
    print('END')
    
    