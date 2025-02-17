# Change Log

All notable changes to this project will be documented in this file.

## [0.7.0] - [dev]

**Added**

+ Class `ForecasterSarimax` and `model_selection_sarimax` (wrapper of pmdarima).

+ Method `predict_dist()` to `ForecasterAutoreg`, `ForecasterAutoregDirect` and `ForecasterAutoregCustom`. 

+ Method `predict_interval()` to `ForecasterAutoregDirect`.

+ Method `predict_bootstrapping()` to `ForecasterAutoreg`, `ForecasterAutoregDirect` and `ForecasterAutoregCustom`.

+ Function `plot_prediction_distribution` in module `plot`.

**Changed**

+ Deprecated python 3.7 compatibility

+ Added python 3.11 compatibility

+ `model_selection_statsmodels` is deprecated in favor of `ForecasterSarimax` and `model_selection_sarimax`.

+ Remove `levels_weights` argument in `grid_search_forecaster_multiseries` and `random_search_forecaster_multiseries`, deprecated since version 0.6.0. Use `series_weights` and `weights_func` when creating the forecaster instead.

**Fixed**




## [0.6.0] - [2022-11-30]

**Added**

+ Class `ForecasterAutoregMultivariate`.

+ Function `initialize_lags` in `utils` module  to create lags values in the initialization of forecasters (applies to all forecasters).

+ Function `initialize_weights` in `utils` module to check and initialize arguments `series_weights`and `weight_func` (applies to all forecasters).

+ Argument `weights_func` in all Forecasters to allow weighted time series forecasting. Individual time based weights can be assigned to each value of the series during the model training.

+ Argument `series_weights` in `ForecasterAutoregMultiSeries` to define individual weights each series.

+ Include argument `random_state` in all Forecasters `set_out_sample_residuals` methods for random sampling with reproducible output.

+ In `ForecasterAutoregMultiSeries`, `predict` and `predict_interval` methods allow the simultaneous prediction of multiple levels.

+ `backtesting_forecaster_multiseries` allows backtesting multiple levels simultaneously.

+ `metric` argument can be a list in `grid_search_forecaster_multiseries`, `random_search_forecaster_multiseries`. If `metric` is a `list`, multiple metrics will be calculated. (suggested by Pablo Dávila Herrero https://github.com/Pablo-Davila)

+ Function `multivariate_time_series_corr` in module `utils`.

+ Function `plot_multivariate_time_series_corr` in module `plot`.
  
**Changed**

+ `ForecasterAutoregDirect` allows to predict specific steps.

+ Remove `ForecasterAutoregMultiOutput` in favor of `ForecasterAutoregDirect`, (deprecated since 0.5.0).

+ Rename function `exog_to_multi_output` to `exog_to_direct` in `utils` module.

+ In `ForecasterAutoregMultiSeries`, rename parameter `series_levels` to `series_col_names`.

+ In `ForecasterAutoregMultiSeries` change type of `out_sample_residuals` to a `dict` of numpy ndarrays.

+ In `ForecasterAutoregMultiSeries`, delete argument `level` from method `set_out_sample_residuals`.

+ In `ForecasterAutoregMultiSeries`, `level` argument of `predict` and `predict_interval` renamed to `levels`.

+ In `backtesting_forecaster_multiseries`, `level` argument of `predict` and `predict_interval` renamed to `levels`.

+ In `check_predict_input` function, argument `level` renamed to `levels` and `series_levels` renamed to `series_col_names`.

+ In `backtesting_forecaster_multiseries`, `metrics_levels` output is now a pandas DataFrame.

+ In `grid_search_forecaster_multiseries` and `random_search_forecaster_multiseries`, argument `levels_weights` is deprecated since version 0.6.0, and will be removed in version 0.7.0. Use `series_weights` and `weights_func` when creating the forecaster instead.

+ Refactor `_create_lags_` in `ForecasterAutoreg`, `ForecasterAutoregDirect` and `ForecasterAutoregMultiSeries`. (suggested by Bennett https://github.com/Bennett561)

+ Refactor `backtesting_forecaster` and `backtesting_forecaster_multiseries`.

+ In `ForecasterAutoregDirect`, `filter_train_X_y_for_step` now starts at 1 (before 0).

+ In `ForecasterAutoregDirect`, DataFrame `y_train` now start with 1, `y_step_1` (before `y_step_0`).

+ Remove `cv_forecaster` from module `model_selection`.

**Fixed**

+ In `ForecasterAutoregMultiSeries`, argument `last_window` predict method now works when it is a pandas DataFrame.

+ In `ForecasterAutoregMultiSeries`, fix bug transformers initialization.


## [0.5.1] - [2022-10-05]

**Added**

+ Check that `exog` and `y` have the same length in `_evaluate_grid_hyperparameters` and `bayesian_search_forecaster` to avoid fit exception when `return_best`.

+ Check that `exog` and `series` have the same length in `_evaluate_grid_hyperparameters_multiseries` to avoid fit exception when `return_best`.

**Changed**

+ Argument `levels_list` in `grid_search_forecaster_multiseries`, `random_search_forecaster_multiseries` and `_evaluate_grid_hyperparameters_multiseries` renamed to `levels`.

**Fixed**

+ `ForecasterAutoregMultiOutput` updated to match `ForecasterAutoregDirect`.

+ Fix Exception to raise when `level_weights` does not add up to a number close to 1.0 (before was exactly 1.0) in `grid_search_forecaster_multiseries`, `random_search_forecaster_multiseries` and `_evaluate_grid_hyperparameters_multiseries`.

+ `Create_train_X_y` in `ForecasterAutoregMultiSeries` now works when the forecaster is not fitted.


## [0.5.0] - [2022-09-23]

**Added**

+ New arguments `transformer_y` (`transformer_series` for multiseries) and `transformer_exog` in all forecaster classes. It is for transforming (scaling, max-min, ...) the modeled time series and exogenous variables inside the forecaster.

+ Functions in utils `transform_series` and `transform_dataframe` to carry out the transformation of the modeled time series and exogenous variables.

+ Functions `_backtesting_forecaster_verbose`, `random_search_forecaster`, `_evaluate_grid_hyperparameters`, `bayesian_search_forecaster`, `_bayesian_search_optuna` and `_bayesian_search_skopt` in model_selection.

+ Created `ForecasterAutoregMultiSeries` class for modeling multiple time series simultaneously.

+ Created module `model_selection_multiseries`. Functions: `_backtesting_forecaster_multiseries_refit`, `_backtesting_forecaster_multiseries_no_refit`, `backtesting_forecaster_multiseries`, `grid_search_forecaster_multiseries`, `random_search_forecaster_multiseries` and `_evaluate_grid_hyperparameters_multiseries`.

+ Function `_check_interval` in utils. (suggested by Thomas Karaouzene https://github.com/tkaraouzene)

+ `metric` can be a list in `backtesting_forecaster`, `grid_search_forecaster`, `random_search_forecaster`, `backtesting_forecaster_multiseries`. If `metric` is a `list`, multiple metrics will be calculated. (suggested by Pablo Dávila Herrero https://github.com/Pablo-Davila)

+ Skforecast works with python 3.10.

+ Functions `save_forecaster` and `load_forecaster` to module utils.

+ `get_feature_importance()` method checks if the forecast is fitted.

**Changed**

+ `backtesting_forecaster` change default value of argument `fixed_train_size: bool=True`.

+ Remove argument `set_out_sample_residuals` in function `backtesting_forecaster` (deprecated since 0.4.2).

+ `backtesting_forecaster` verbose now includes fold size.

+ `grid_search_forecaster` results include the name of the used metric as column name.

+ Remove `get_coef` method from `ForecasterAutoreg`, `ForecasterAutoregCustom` and `ForecasterAutoregMultiOutput` (deprecated since 0.4.3).

+ `_get_metric` now allows `mean_squared_log_error`.

+ `ForecasterAutoregMultiOutput` has been renamed to `ForecasterAutoregDirect`. `ForecasterAutoregMultiOutput` will be removed in version 0.6.0.

+ `check_predict_input` updated to check `ForecasterAutoregMultiSeries` inputs.

+ `set_out_sample_residuals` has a new argument `transform` to transform the residuals before being stored.

**Fixed**

+ `fit` now stores `last_window` values with len = forecaster.max_lag in ForecasterAutoreg and ForecasterAutoregCustom.

+ `in_sample_residuals` stored as a `pd.Series` when `len(residuals) > 1000`.


## [0.4.3] - [2022-03-18]

**Added**

+ Checks if all elements in lags are `int` when creating ForecasterAutoreg and ForecasterAutoregMultiOutput.

+ Add `fixed_train_size: bool=False` argument to `backtesting_forecaster` and `backtesting_sarimax`

**Changed**

+ Rename `get_metric` to `_get_metric`.

+ Functions in model_selection module allow custom metrics.

+ Functions in model_selection_statsmodels module allow custom metrics.

+ Change function `set_out_sample_residuals` (ForecasterAutoreg and ForecasterAutoregCustom), `residuals` argument must be a `pandas Series` (was `numpy ndarray`).

+ Returned value of backtesting functions (model_selection and model_selection_statsmodels) is now a `float` (was `numpy ndarray`).

+ `get_coef` and `get_feature_importance` methods unified in `get_feature_importance`.

**Fixed**

+ Requirements versions.

+ Method `fit` doesn't remove `out_sample_residuals` each time the forecaster is fitted.

+ Added random seed to residuals downsampling (ForecasterAutoreg and ForecasterAutoregCustom)


## [0.4.2] - [2022-01-08]

**Added**

+ Increased verbosity of function `backtesting_forecaster()`.

+ Random state argument in `backtesting_forecaster()`.

**Changed**

+ Function `backtesting_forecaster()` do not modify the original forecaster.

+ Deprecated argument `set_out_sample_residuals` in function `backtesting_forecaster()`.

+ Function `model_selection.time_series_spliter` renamed to `model_selection.time_series_splitter`

**Fixed**

+ Methods `get_coef` and `get_feature_importance` of `ForecasterAutoregMultiOutput` class return proper feature names.


## [0.4.1] - [2021-12-13]

**Added**

**Changed**

**Fixed**

+ `fit` and `predict` transform pandas series and dataframes to numpy arrays if regressor is XGBoost.

## [0.4.0] - [2021-12-10]

Version 0.4 has undergone a huge code refactoring. Main changes are related to input-output formats (only pandas series and dataframes are allowed although internally numpy arrays are used for performance) and model validation methods (unified into backtesting with and without refit).

**Added**

+ `ForecasterBase` as parent class

**Changed**

+ Argument `y` must be pandas Series. Numpy ndarrays are not allowed anymore.

+ Argument `exog` must be pandas Series or pandas DataFrame. Numpy ndarrays are not allowed anymore.

+ Output of `predict` is a pandas Series with index according to the steps predicted.

+ Scikitlearn pipelines are allowed as regressors.

+ `backtesting_forecaster` and `backtesting_forecaster_intervals` have been combined in a single function.

    + It is possible to backtest forecasters already trained.
    + `ForecasterAutoregMultiOutput` allows incomplete folds.
    + It is possible to update `out_sample_residuals` with backtesting residuals.
    
+ `cv_forecaster` has the option to update `out_sample_residuals` with backtesting residuals.

+ `backtesting_sarimax_statsmodels` and `cv_sarimax_statsmodels` have been combined in a single function.

+ `gridsearch_forecaster` use backtesting as validation strategy with the option of refit.

+ Extended information when printing `Forecaster` object.

+ All static methods for checking and preprocessing inputs moved to module utils.

+ Remove deprecated class `ForecasterCustom`.

**Fixed**

## [0.3.0] - [2021-09-01]

**Added**

+ New module model_selection_statsmodels to cross-validate, backtesting and grid search AutoReg and SARIMAX models from statsmodels library:
    + `backtesting_autoreg_statsmodels`
    + `cv_autoreg_statsmodels`
    + `backtesting_sarimax_statsmodels`
    + `cv_sarimax_statsmodels`
    + `grid_search_sarimax_statsmodels`
    
+ Added attribute window_size to `ForecasterAutoreg` and `ForecasterAutoregCustom`. It is equal to `max_lag`.

**Changed**

+ `cv_forecaster` returns cross-validation metrics and cross-validation predictions.
+ Added an extra column for each parameter in the dataframe returned by `grid_search_forecaster`.
+ statsmodels 0.12.2 added to requirements

**Fixed**


## [0.2.0] - [2021-08-26]

**Added**


+ Multiple exogenous variables can be passed as pandas DataFrame.

+ Documentation at https://joaquinamatrodrigo.github.io/skforecast/

+ New unit test

+ Increased typing

**Changed**

+ New implementation of `ForecasterAutoregMultiOutput`. The training process in the new version creates a different X_train for each step. See [Direct multi-step forecasting](https://github.com/JoaquinAmatRodrigo/skforecast#introduction) for more details. Old versión can be acces with `skforecast.deprecated.ForecasterAutoregMultiOutput`.

**Fixed**



## [0.1.9] - [2021-07-27]

**Added**

+ Logging total number of models to fit in `grid_search_forecaster`.

+ Class `ForecasterAutoregCustom`.

+ Method `create_train_X_y` to facilitate access to the training data matrix created from `y` and `exog`.

**Changed**


+ New implementation of `ForecasterAutoregMultiOutput`. The training process in the new version creates a different X_train for each step. See [Direct multi-step forecasting](https://github.com/JoaquinAmatRodrigo/skforecast#introduction) for more details. Old versión can be acces with `skforecast.deprecated.ForecasterAutoregMultiOutput`.

+ Class `ForecasterCustom` has been renamed to `ForecasterAutoregCustom`. However, `ForecasterCustom` will still remain to keep backward compatibility.

+ Argument `metric` in `cv_forecaster`, `backtesting_forecaster`, `grid_search_forecaster` and `backtesting_forecaster_intervals` changed from 'neg_mean_squared_error', 'neg_mean_absolute_error', 'neg_mean_absolute_percentage_error' to 'mean_squared_error', 'mean_absolute_error', 'mean_absolute_percentage_error'.

+ Check if argument `metric` in `cv_forecaster`, `backtesting_forecaster`, `grid_search_forecaster` and `backtesting_forecaster_intervals` is one of 'mean_squared_error', 'mean_absolute_error', 'mean_absolute_percentage_error'.

+ `time_series_spliter` doesn't include the remaining observations in the last complete fold but in a new one when `allow_incomplete_fold=True`. Take in consideration that incomplete folds with few observations could overestimate or underestimate the validation metric.

**Fixed**

+ Update lags of  `ForecasterAutoregMultiOutput` after `grid_search_forecaster`.


## [0.1.8.1] - [2021-05-17]

**Added**

+ `set_out_sample_residuals` method to store or update out of sample residuals used by `predict_interval`.

**Changed**

+ `backtesting_forecaster_intervals` and `backtesting_forecaster` print number of steps per fold.

+ Only stored up to 1000 residuals.

+ Improved verbose in `backtesting_forecaster_intervals`.

**Fixed**

+ Warning of inclompleted folds when using `backtesting_forecast` with a  `ForecasterAutoregMultiOutput`.

+ `ForecasterAutoregMultiOutput.predict` allow exog data longer than needed (steps).

+ `backtesting_forecast` prints correctly the number of folds when remainder observations are cero.

+ Removed named argument X in `self.regressor.predict(X)` to allow using XGBoost regressor.

+ Values stored in `self.last_window` when training `ForecasterAutoregMultiOutput`. 


## [0.1.8] - [2021-04-02]

**Added**

- Class `ForecasterAutoregMultiOutput.py`: forecaster with direct multi-step predictions.
- Method `ForecasterCustom.predict_interval` and  `ForecasterAutoreg.predict_interval`: estimate prediction interval using bootstrapping.
- `skforecast.model_selection.backtesting_forecaster_intervals` perform backtesting and return prediction intervals.
 
**Changed**

 
**Fixed**


## [0.1.7] - [2021-03-19]

**Added**

- Class `ForecasterCustom`: same functionalities as `ForecasterAutoreg` but allows custom definition of predictors.
 
**Changed**

- `grid_search forecaster` adapted to work with objects `ForecasterCustom` in addition to `ForecasterAutoreg`.
 
**Fixed**
 
 
## [0.1.6] - [2021-03-14]

**Added**

- Method `get_feature_importances` to `skforecast.ForecasterAutoreg`.
- Added backtesting strategy in `grid_search_forecaster`.
- Added `backtesting_forecast` to `skforecast.model_selection`.
 
**Changed**

- Method `create_lags` return a matrix where the order of columns match the ascending order of lags. For example, column 0 contains the values of the minimum lag used as predictor.
- Renamed argument `X` to `last_window` in method `predict`.
- Renamed `ts_cv_forecaster` to `cv_forecaster`.
 
**Fixed**
 
## [0.1.4] - [2021-02-15]
  
**Added**

- Method `get_coef` to `skforecast.ForecasterAutoreg`.
 
**Changed**

 
**Fixed**
