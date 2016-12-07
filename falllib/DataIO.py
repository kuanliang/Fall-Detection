import numpy as np
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures
import xlrd
import csv
import numpy as np

value_list = ['X(g)', 'Y(g)', 'Z(g)', 'Theta(deg)', 'Phi(deg)']


class Coordinate_axis():
    X_AXIS = 'X(g)'
    Y_AXIS = 'Y(g)'
    Z_AXIS = 'Z(g)'
    THETA = 'Theta(deg)'
    PHI = 'Phi(deg)'

    
def get_start_and_end_time(df, coordinate_axis, sec=0.5):
    coordinate_less_than_zero = df[df[coordinate_axis] < 0].iloc[0].name
    start_time = coordinate_less_than_zero - sec
    end_time = coordinate_less_than_zero + sec
    return start_time, end_time
    
    
def get_record(currentDf, nextDf):
    '''
    '''
    
    value_list = ['X(g)', 'Y(g)', 'Z(g)', 'Theta(deg)', 'Phi(deg)']
    # mean, absolute value of the mean, standard deviation, skew, kurtosis
    means = currentDf.mean()[value_list].values
    abs_means = np.abs(currentDf.mean())[value_list].values
    stds = currentDf.std()[value_list].values
    skews = currentDf.skew()[value_list].values
    kurtosiss = currentDf.kurtosis()[value_list].values
    # mean, standard deviation, skew, kurtosis differences between successive samples
    diff_means = means - nextDf.mean()[value_list].values
    diff_stds = stds - nextDf.std()[value_list].values
    diff_skews = skews - nextDf.skew()[value_list].values
    diff_kurtosiss = kurtosiss - nextDf.skew()[value_list].values
    
    # min, max, absolute value of the min and max
    mins = currentDf.min()[value_list].values
    maxs = currentDf.max()[value_list].values
    abs_mins = np.abs(mins)
    abs_maxs = np.abs(maxs)
    
    # mean of the cross product
    poly = PolynomialFeatures(interaction_only=True, include_bias=False)
    cross_products = poly.fit_transform(currentDf[value_list])[:, 5:].mean(axis=0)
    abs_cross_products = np.abs(cross_products)
    
    final_record = np.concatenate((means, abs_means, stds, skews, kurtosiss,
                                  diff_means, diff_stds, diff_skews, diff_kurtosiss,
                                  mins, maxs, abs_mins, abs_maxs,
                                  cross_products, abs_cross_products))
    
    return final_record
    




def xls_to_records(path):
    '''read in xlsx file and parse worksheets to form matrix records
    
    Notes: columns are ['Number', 'X(g)', 'Y(g)', 'Z(g)', 'R(g)', 'Theta(deg)', 'Phi(deg)']
    
    Args: path
    
    Return: 
    
    '''
    record_all_list = []
    workbook = xlrd.open_workbook(path)
    for index, sheet_name in enumerate(workbook.sheet_names()):
        # print 'processing workshet {}'.format(index)
        # print(sheet_name)
        worksheet = workbook.sheet_by_name(sheet_name)
        temp_file = 'temp.csv'
        csvfile = open(temp_file, 'w')
        wr = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        for rownum in range(worksheet.nrows):
            wr.writerow([x.encode('utf8', 'ignore') if type(x) == unicode else x for x in worksheet.row_values(rownum)])
        
        csvfile.close()
        
        testDf = pd.read_csv(temp_file, skiprows=1, index_col='Time(s)')
        start_time, stop_time = get_target_rows(testDf, Coordinate_axis.Y_AXIS, sec=step_time * 2)

        #start_time = start_stop_dict[index]['start_time']
        #end_time = start_stop_dict[index]['end_time']
        step_time = 0.25
        step_nb = int(round(end_time - start_time))
        
        filteredDf = testDf[(testDf.index >= start_time) & (testDf.index < end_time)].copy()
        
        record_list = []
        # return filteredDf
        for i in range(step_nb):
            window_start = start_time + i * step_time
            window_stop = start_time + 1 + i * step_time
            # print(window_start)
            # print(window_stop)
            currentDf = filteredDf[(filteredDf.index >= window_start) & 
                                   (filteredDf.index < window_stop)].copy()
            
            # print currentDf.columns
            currentDf.columns = ['Number', 'X(g)', 'Y(g)', 'Z(g)', 'R(g)', 'Theta(deg)', 'Phi(deg)']
            
            # print currentDf.shape
        
            nextDf = filteredDf[(filteredDf.index >= window_start + step_time) &
                                (filteredDf.index < window_stop + step_time)].copy()
            
            nextDf.columns = ['Number', 'X(g)', 'Y(g)', 'Z(g)', 'R(g)', 'Theta(deg)', 'Phi(deg)']
            
            # print nextDf.shape
        
            record_values = get_record(currentDf, nextDf)
        
            record_list.append(record_values)
            
        # print len(record_list)
        
        record_all_list = record_all_list + record_list
        # print(currentDf.index)
        # print(nextDf.index)
        
        # print(filteredDf.shape)
        
        g_list = ['X(g)', 'Y(g)', 'Z(g)']
        
        # plt.plot(testDf[g_list])
        
        
        # print(testDf.shape)
        
    return np.array(record_all_list)