from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler
from sklearn import linear_model
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import Imputer

def logisticModeling(X_train, y_train, random_state=0):
    '''perform logistic regression
    
    Notes: 
    
    Args:
        dfTrain: training dataframe split according to SN split
        dfTest: testing dataframe split according to SN split

    Return: trained logistic model
    
    '''
    pipe = Pipeline(
        [
            ('imputer', Imputer(missing_values='NaN', strategy='median', axis=1)),
            ('scaler', RobustScaler()),
            ('clf', linear_model.LogisticRegression(class_weight='balanced', max_iter=1000))
        ]
    )
    param_grid = {
        'clf__penalty': ('l1','l2'),
        'clf__tol': (1, 1e-1, 1e-2, 1e-3, 1e-4),
        'clf__C': (10, 5, 1, 0.1, 0.01, 0.001, 0.0001)
    }
    
    gs_cv = grid_search.GridSearchCV(pipe, param_grid, scoring='f1_weighted')
    
    gs_cv.fit(X_train, y_train)
    
    
    return gs_cv