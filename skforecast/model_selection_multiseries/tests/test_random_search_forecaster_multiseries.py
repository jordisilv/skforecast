# Unit test random_search_forecaster_multiseries
# ==============================================================================
import pytest
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from skforecast.ForecasterAutoregMultiSeries import ForecasterAutoregMultiSeries
from skforecast.ForecasterAutoregMultiVariate import ForecasterAutoregMultiVariate
from skforecast.model_selection_multiseries import random_search_forecaster_multiseries

from tqdm import tqdm
from functools import partialmethod
tqdm.__init__ = partialmethod(tqdm.__init__, disable=True) # hide progress bar

# Fixtures
# np.random.seed(123)
# l1 = np.random.rand(50)
# l2 = np.random.rand(50)
series = pd.DataFrame({'l1': pd.Series(np.array(
                                [0.69646919, 0.28613933, 0.22685145, 0.55131477, 0.71946897,
                                 0.42310646, 0.9807642 , 0.68482974, 0.4809319 , 0.39211752,
                                 0.34317802, 0.72904971, 0.43857224, 0.0596779 , 0.39804426,
                                 0.73799541, 0.18249173, 0.17545176, 0.53155137, 0.53182759,
                                 0.63440096, 0.84943179, 0.72445532, 0.61102351, 0.72244338,
                                 0.32295891, 0.36178866, 0.22826323, 0.29371405, 0.63097612,
                                 0.09210494, 0.43370117, 0.43086276, 0.4936851 , 0.42583029,
                                 0.31226122, 0.42635131, 0.89338916, 0.94416002, 0.50183668,
                                 0.62395295, 0.1156184 , 0.31728548, 0.41482621, 0.86630916,
                                 0.25045537, 0.48303426, 0.98555979, 0.51948512, 0.61289453]
                                      )
                            ), 
                       'l2': pd.Series(np.array(
                                [0.12062867, 0.8263408 , 0.60306013, 0.54506801, 0.34276383,
                                 0.30412079, 0.41702221, 0.68130077, 0.87545684, 0.51042234,
                                 0.66931378, 0.58593655, 0.6249035 , 0.67468905, 0.84234244,
                                 0.08319499, 0.76368284, 0.24366637, 0.19422296, 0.57245696,
                                 0.09571252, 0.88532683, 0.62724897, 0.72341636, 0.01612921,
                                 0.59443188, 0.55678519, 0.15895964, 0.15307052, 0.69552953,
                                 0.31876643, 0.6919703 , 0.55438325, 0.38895057, 0.92513249,
                                 0.84167   , 0.35739757, 0.04359146, 0.30476807, 0.39818568,
                                 0.70495883, 0.99535848, 0.35591487, 0.76254781, 0.59317692,
                                 0.6917018 , 0.15112745, 0.39887629, 0.2408559 , 0.34345601]
                                      )
                            )
                      }
         )


def test_output_random_search_forecaster_multiseries_ForecasterAutoregMultiSeries_with_mocked():
    """
    Test output of random_search_forecaster_multiseries in ForecasterAutoregMultiSeries with mocked
    (mocked done in Skforecast v0.5.0)
    """
    forecaster = ForecasterAutoregMultiSeries(
                    regressor = Ridge(random_state=123),
                    lags      = 2 # Placeholder, the value will be overwritten
                 )

    steps = 3
    n_validation = 12
    lags_grid = [2, 4]
    param_distributions = {'alpha':np.logspace(-5, 3, 10)}
    n_iter = 3

    results = random_search_forecaster_multiseries(
                    forecaster          = forecaster,
                    series              = series,
                    param_distributions = param_distributions,
                    steps               = steps,
                    metric              = 'mean_absolute_error',
                    initial_train_size  = len(series) - n_validation,
                    fixed_train_size    = False,
                    levels              = None,
                    exog                = None,
                    lags_grid           = lags_grid,
                    refit               = False,
                    n_iter              = n_iter,
                    return_best         = False,
                    verbose             = False
              )
    
    expected_results = pd.DataFrame({
            'levels':[['l1', 'l2'], ['l1', 'l2'], ['l1', 'l2'], ['l1', 'l2'], ['l1', 'l2'], ['l1', 'l2']],
            'lags'  :[[1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2], [1, 2], [1, 2]],
            'params':[{'alpha': 1e-05}, {'alpha': 0.03593813663804626}, {'alpha': 16.681005372000556}, 
                      {'alpha': 16.681005372000556}, {'alpha': 0.03593813663804626}, {'alpha': 1e-05}],
            'mean_absolute_error':np.array([0.20967967565103562, 0.20968441516920436, 0.20988932397621246,
                                            0.2104645379335131, 0.2107874324738886, 0.2107879393001434]),                                                               
            'alpha' :np.array([1e-05, 0.03593813663804626, 16.681005372000556, 
                               16.681005372000556, 0.03593813663804626, 1e-05])
                                     },
            index=[4, 3, 5, 2, 0, 1]
                                   )

    pd.testing.assert_frame_equal(results, expected_results)


def test_output_random_search_forecaster_multiseries_ForecasterAutoregMultiVariate_with_mocked():
    """
    Test output of random_search_forecaster_multiseries in ForecasterAutoregMultiVariate with mocked
    (mocked done in Skforecast v0.6.0)
    """
    forecaster = ForecasterAutoregMultiVariate(
                     regressor = Ridge(random_state=123),
                     level     = 'l1',
                     lags      = 2,
                     steps     = 3
                 )

    steps = 3
    n_validation = 12
    lags_grid = [2, 4]
    param_distributions = {'alpha':np.logspace(-5, 3, 10)}
    n_iter = 3

    results = random_search_forecaster_multiseries(
                    forecaster          = forecaster,
                    series              = series,
                    param_distributions = param_distributions,
                    steps               = steps,
                    metric              = 'mean_absolute_error',
                    initial_train_size  = len(series) - n_validation,
                    fixed_train_size    = False,
                    levels              = None,
                    exog                = None,
                    lags_grid           = lags_grid,
                    refit               = False,
                    n_iter              = n_iter,
                    return_best         = False,
                    verbose             = True
              )
    
    expected_results = pd.DataFrame({
            'levels': [['l1'], ['l1'], ['l1'], ['l1'], ['l1'], ['l1']],
            'lags'  : [[1, 2], [1, 2], [1, 2], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4]],
            'params': [{'alpha': 1e-05}, {'alpha': 0.03593813663804626}, {'alpha': 16.681005372000556},
                       {'alpha': 16.681005372000556}, {'alpha': 0.03593813663804626}, {'alpha': 1e-05}],
            'mean_absolute_error': np.array([0.20107097, 0.20135665, 0.20991177, 0.21121154, 0.22640335, 0.22645387]),                                                               
            'alpha' : np.array([1.00000000e-05, 3.59381366e-02, 1.66810054e+01, 1.66810054e+01, 3.59381366e-02, 1.00000000e-05])
                                     },
            index=[1, 0, 2, 5, 3, 4]
                                   )

    pd.testing.assert_frame_equal(results, expected_results)