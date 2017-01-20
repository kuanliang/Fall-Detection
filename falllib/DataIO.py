import numpy as np
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures
import xlrd
import csv
import numpy as np

value_list = ['X(g)', 'Y(g)', 'Z(g)', 'Theta(deg)', 'Phi(deg)']


class Coordinate_axis:
    X_AXIS = 'X(g)'
    Y_AXIS = 'Y(g)'
    Z_AXIS = 'Z(g)'
    THETA = 'Theta(deg)'
    PHI = 'Phi(deg)'


class Fall:
    FRONT = 1
    BACK = 2
    LEFT = 3
    RIGHT = 4

    
def get_start_and_end_time(df, coordinate_axis, sec=0.6):
    '''
    '''
    condition = df[coordinate_axis] < 0

    if any(condition):
#         testDf[['X(g)', 'Y(g)', 'Z(g)']].plot()
        coordinate_less_than_zero = df[condition].iloc[0].name
        start_time = coordinate_less_than_zero - sec
        end_time = coordinate_less_than_zero + sec
    else:
        start_time = df.iloc[0].name
        end_time = df.iloc[-1].name
        exec_time = end_time - start_time
        middle = df.loc[df['Number'] == len(df)/2].index[0]
        
        # print start_time, end_time, exec_time, middle
        
        if exec_time > 10:
            start_time = middle - 4
            end_time = middle + 4
        elif exec_time > 6:
            start_time = middle - 2.5
            end_time = middle + 2.5
        else:
            start_time = middle - 1
            end_time = middle + 1

    return start_time, end_time


def get_record(currentDf, nextDf):
    '''
    '''
    
    value_list = ['X(g)', 'Y(g)', 'Z(g)', 'Theta(deg)', 'Phi(deg)']
    # mean, absolute value of the mean, standard deviation, skew, kurtosis
    # abss = np.abs(currentDf)
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
    

def xls_to_records(paths, use_step=False):
    '''read in xlsx file and parse worksheets to form matrix records
    
    Notes: columns are ['Number', 'X(g)', 'Y(g)', 'Z(g)', 'R(g)', 'Theta(deg)', 'Phi(deg)']
    
    Args: path
    
    Return: 
    
    '''
    # 
    record_all_list = []
    
    # 
    for path in paths: 
        print path
        workbook = xlrd.open_workbook(path)
        
        for index, sheet_name in enumerate(workbook.sheet_names()):
            try:
                # print 'processing workshet {}'.format(index)
                # print(sheet_name)
                worksheet = workbook.sheet_by_name(sheet_name)
                temp_file = 'temp.csv'

                with open(temp_file, 'w') as csvfile:
                    wr = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
                    for rownum in range(worksheet.nrows):
                        wr.writerow([x.encode('utf8', 'ignore') if type(x) == unicode else x for x in worksheet.row_values(rownum)])

                testDf = pd.read_csv(temp_file, skiprows=1, index_col='Time(s)')
                
                # 
                start_time, end_time = get_start_and_end_time(testDf, Coordinate_axis.Y_AXIS, sec=0.5)
                

                step_time = 0.25
                if use_step:
                    step_nb = int(round((end_time - start_time) / step_time))
                    # print 'step_nb: {}'.format(step_nb)
                else:
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

                    if len(currentDf) is 0:
                        break

                    # print currentDf.columns
                    currentDf.columns = ['Number', 'X(g)', 'Y(g)', 'Z(g)', 'R(g)', 'Theta(deg)', 'Phi(deg)']

                    # print currentDf.shape

    #                 nextDf = filteredDf[(filteredDf.index >= window_start + step_time) &
    #                                     (filteredDf.index < window_stop + step_time)].copy()

    #                 nextDf.columns = ['Number', 'X(g)', 'Y(g)', 'Z(g)', 'R(g)', 'Theta(deg)', 'Phi(deg)']
                    preDf = filteredDf[(filteredDf.index >= window_start - step_time) &
                                        (filteredDf.index < window_stop - step_time)].copy()
                    preDf.columns = ['Number', 'X(g)', 'Y(g)', 'Z(g)', 'R(g)', 'Theta(deg)', 'Phi(deg)']
                    # print nextDf.shape

                    # record_values = get_record(currentDf, nextDf)
                    record_values = get_record(currentDf, preDf)

                    record_list.append(record_values)

                # print len(record_list)

                record_all_list = record_all_list + record_list

                # print(currentDf.index)
                # print(nextDf.index)

                # print(filteredDf.shape)

                g_list = ['X(g)', 'Y(g)', 'Z(g)']

                # plt.plot(testDf[g_list])


                # print(testDf.shape)
            except Exception as e:
                print path
                print('Fail: {}'.format(sheet_name.encode('utf-8')))
                print e.message
                continue
    return np.array(record_all_list)