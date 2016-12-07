import pandas as pd
import numpy as np
import xlrd
import matplotlib.pyplot as plt
import csv
import itertools

def plot_worksheet(path, sheetNo):
    '''
    '''
    g_list = ['X(g)', 'Y(g)', 'Z(g)']
    workbook = xlrd.open_workbook(path)
    worksheet_names = workbook.sheet_names()
    # print worksheet_names
    worksheet = workbook.sheet_by_name(worksheet_names[sheetNo])
    temp_file = 'temp.csv'
    csvfile = open(temp_file, 'w')
    wr = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
    for rownum in range(worksheet.nrows):
        # rownum = rownum if type(rownum) is int else rownum.encode('ascii', 'ignore')
        # print worksheet.row_values(rownum)
        wr.writerow([x.encode('utf8', 'ignore') if type(x) == unicode else x for x in worksheet.row_values(rownum)])
    csvfile.close()
    
    df = pd.read_csv(temp_file, skiprows=1, index_col='Time(s)')
    
    plt.plot(df[g_list])
    
def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, cm[i, j],
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')