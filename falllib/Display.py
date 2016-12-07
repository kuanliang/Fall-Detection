import pandas as pd
import numpy as np
import xlrd
import matplotlib.pyplot as plt
import csv

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