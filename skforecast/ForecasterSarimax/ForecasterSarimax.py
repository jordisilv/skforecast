################################################################################
#                            ForecasterSarimax                                 #
#                                                                              #
# This work by Joaquin Amat Rodrigo and Javier Escobar Ortiz is licensed       #
# under a Creative Commons Attribution 4.0 International License.              #
################################################################################
# coding=utf-8

from typing import Union, Dict, List, Tuple, Any, Optional
import warnings
import logging
import sys
import numpy as np
import pandas as pd
import pmdarima
from pmdarima.arima import ARIMA
from sklearn.base import clone
from sklearn.exceptions import NotFittedError

import skforecast
from ..utils import check_y
from ..utils import check_exog
from ..utils import check_predict_input
from ..utils import expand_index
from ..utils import transform_series
from ..utils import transform_dataframe

logging.basicConfig(
    format = '%(name)-10s %(levelname)-5s %(message)s', 
    level  = logging.INFO,
)


class ForecasterSarimax():
    """
    This class turns ARIMA model from pmdarima library into a Forecaster compatible with 
    the skforecast API.
    
    Parameters
    ----------
    regressor : pmdarima.arima.ARIMA
        An instance of an ARIMA from pmdarima library. This model internally wraps the
        statsmodels SARIMAX class.

    transformer_y : object transformer (preprocessor), default `None`
        An instance of a transformer (preprocessor) compatible with the scikit-learn
        preprocessing API with methods: fit, transform, fit_transform and inverse_transform.
        ColumnTransformers are not allowed since they do not have inverse_transform method.
        The transformation is applied to `y` before training the forecaster. 

    transformer_exog : object transformer (preprocessor), default `None`
        An instance of a transformer (preprocessor) compatible with the scikit-learn
        preprocessing API. The transformation is applied to `exog` before training the
        forecaster. `inverse_transform` is not available when using ColumnTransformers.
    
    Attributes
    ----------
    regressor : pmdarima.arima.ARIMA
        An instance of an ARIMA from pmdarima library. The model internally wraps the
        statsmodels SARIMAX class

    params: dict
        Parameters of the sarimax model.
        
    transformer_y : object transformer (preprocessor), default `None`
        An instance of a transformer (preprocessor) compatible with the scikit-learn
        preprocessing API with methods: fit, transform, fit_transform and inverse_transform.
        ColumnTransformers are not allowed since they do not have inverse_transform method.
        The transformation is applied to `y` before training the forecaster.

    transformer_exog : object transformer (preprocessor), default `None`
        An instance of a transformer (preprocessor) compatible with the scikit-learn
        preprocessing API. The transformation is applied to `exog` before training the
        forecaster. `inverse_transform` is not available when using ColumnTransformers.
   
    window_size : int, `1` 
        Not used, present here for API consistency by convention.

    last_window : pandas Series
        Last window the forecaster has seen during trained. It stores the
        values needed to predict the next `step` right after the training data.

    extended_index : pandas Index
        When predicting using `last_window` and `last_window_exog`, the internal
        statsmodels SARIMAX will be updated using its append method. To do this,
        `last_window` data must start at the end of the index seen by the 
        forecaster, this is stored in forecaster.extended_index.

        Check https://www.statsmodels.org/dev/generated/statsmodels.tsa.arima.model.ARIMAResults.append.html
        to know more about statsmodels append method.
        
    fitted : Bool
        Tag to identify if the regressor has been fitted (trained).
        
    index_type : type
        Type of index of the input used in training.
        
    index_freq : str
        Frequency of Index of the input used in training.
        
    training_range : pandas Index
        First and last values of index of the data used during training.
        
    included_exog : bool
        If the forecaster has been trained using exogenous variable/s.
        
    exog_type : type
        Type of exogenous variable/s used in training.
        
    exog_col_names : list
        Names of columns of `exog` if `exog` used in training was a pandas
        DataFrame.

    creation_date : str
        Date of creation.

    fit_date : str
        Date of last fit.

    skforcast_version : str
        Version of skforecast library used to create the forecaster.

    python_version : str
        Version of python used to create the forecaster.
     
    """
    
    def __init__(
        self,
        regressor: ARIMA,
        transformer_y: Optional[object]=None,
        transformer_exog: Optional[object]=None,
    ) -> None:
        
        self.regressor         = regressor
        self.transformer_y     = transformer_y
        self.transformer_exog  = transformer_exog
        self.window_size       = 1
        self.last_window       = None
        self.extended_index    = None
        self.fitted            = False
        self.index_type        = None
        self.index_freq        = None
        self.training_range    = None
        self.included_exog     = False
        self.exog_type         = None
        self.exog_col_names    = None
        self.creation_date     = pd.Timestamp.today().strftime('%Y-%m-%d %H:%M:%S')
        self.fit_date          = None
        self.skforcast_version = skforecast.__version__
        self.python_version    = sys.version.split(" ")[0]
        
        if not isinstance(self.regressor, pmdarima.arima.ARIMA):
            raise TypeError(
                (f"`regressor` must be an instance of type pmdarima.arima.ARIMA. "
                 f"Got {type(regressor)}.")
            )

        self.params = self.regressor.get_params(deep=True)


    def __repr__(
        self
    ) -> str:
        """
        Information displayed when a ForecasterSarimax object is printed.
        """

        info = (
            f"{'=' * len(str(type(self)).split('.')[1])} \n"
            f"{str(type(self)).split('.')[1]} \n"
            f"{'=' * len(str(type(self)).split('.')[1])} \n"
            f"Regressor: {self.regressor} \n"
            f"Regressor parameters: {self.params} \n"
            f"Window size: {self.window_size} \n"
            f"Transformer for y: {self.transformer_y} \n"
            f"Transformer for exog: {self.transformer_exog} \n"
            f"Exogenous included: {self.included_exog} \n"
            f"Type of exogenous variable: {self.exog_type} \n"
            f"Exogenous variables names: {self.exog_col_names} \n"
            f"Training range: {self.training_range.to_list() if self.fitted else None} \n"
            f"Training index type: {str(self.index_type).split('.')[-1][:-2] if self.fitted else None} \n"
            f"Training index frequency: {self.index_freq if self.fitted else None} \n"
            f"Creation date: {self.creation_date} \n"
            f"Last fit date: {self.fit_date} \n"
            f"Index seen by the forecaster: {self.extended_index} \n"
            f"Skforecast version: {self.skforcast_version} \n"
            f"Python version: {self.python_version} \n"
        )

        return info


    def fit(
        self,
        y: pd.Series,
        exog: Optional[Union[pd.Series, pd.DataFrame]]=None
    ) -> None:
        """
        Training Forecaster.
        
        Parameters
        ----------        
        y : pandas Series
            Training time series.
            
        exog : pandas Series, pandas DataFrame, default `None`
            Exogenous variable/s included as predictor/s. Must have the same
            number of observations as `y` and their indexes must be aligned so
            that y[i] is regressed on exog[i].

        Returns 
        -------
        None
        
        """

        check_y(y=y)
        if exog is not None:
            if len(exog) != len(y):
                raise ValueError(
                    (f'`exog` must have same number of samples as `y`. '
                     f'length `exog`: ({len(exog)}), length `y`: ({len(y)})')
                )
            check_exog(exog=exog)

        # Reset values in case the forecaster has already been fitted.
        self.index_type          = None
        self.index_freq          = None
        self.last_window         = None
        self.extended_index      = None
        self.included_exog       = False
        self.exog_type           = None
        self.exog_col_names      = None
        self.X_train_col_names   = None
        self.in_sample_residuals = None
        self.fitted              = False
        self.training_range      = None
        
        if exog is not None:
            self.included_exog = True
            self.exog_type = type(exog)
            self.exog_col_names = \
                 exog.columns.to_list() if isinstance(exog, pd.DataFrame) else exog.name

        y = transform_series(
                series            = y,
                transformer       = self.transformer_y,
                fit               = True,
                inverse_transform = False
            )

        if exog is not None:
            if isinstance(exog, pd.Series):
                # pmdarima.arima.ARIMA only accepts DataFrames or 2d-arrays as exog   
                exog = exog.to_frame()
            
            exog = transform_dataframe(
                       df                = exog,
                       transformer       = self.transformer_exog,
                       fit               = True,
                       inverse_transform = False
                   )
        
        self.regressor.fit(y=y, X=exog)
        self.fitted = True
        self.fit_date = pd.Timestamp.today().strftime('%Y-%m-%d %H:%M:%S')
        self.training_range = y.index[[0, -1]]
        self.index_type = type(y.index)
        if isinstance(y.index, pd.DatetimeIndex):
            self.index_freq = y.index.freqstr
        else: 
            self.index_freq = y.index.step

        self.last_window = y.copy()
        self.extended_index = self.regressor.arima_res_.fittedvalues.index.copy()
        self.params = self.regressor.get_params(deep=True)


    def predict(
        self,
        steps: int,
        last_window: Optional[pd.Series]=None,
        last_window_exog: Optional[Union[pd.Series, pd.DataFrame]]=None,
        exog: Optional[Union[pd.Series, pd.DataFrame]]=None
    ) -> pd.Series:
        """
        Forecast future values

        Generate predictions (forecasts) n steps in the future. Note that if 
        exogenous variables were used in the model fit, they will be expected 
        for the predict procedure and will fail otherwise.
        
        When predicting using `last_window` and `last_window_exog`, the internal
        statsmodels SARIMAX will be updated using its append method. To do this,
        `last_window` data must start at the end of the index seen by the 
        forecaster, this is stored in forecaster.extended_index.

        Check https://www.statsmodels.org/dev/generated/statsmodels.tsa.arima.model.ARIMAResults.append.html
        to know more about statsmodels append method.
        
        Parameters
        ----------
        steps : int
            Number of future steps predicted.
            
        last_window : pandas Series, default `None`
            Values of the series used to create the predictors needed in the 
            predictions. Used to make predictions unrelated to the original data. 
            Values have to start at the end of the training data.

        last_window_exog : pandas Series, pandas DataFrame, default `None`
            Values of the exogenous variables aligned with `last_window`. Only
            needed when `last_window` is not None and the forecaster has been
            trained including exogenous variables. Used to make predictions 
            unrelated to the original data. Values have to start at the end 
            of the training data.
            
        exog : pandas Series, pandas DataFrame, default `None`
            Value of the exogenous variable/s for the next steps.

        Returns 
        -------
        predictions : pandas Series
            Predicted values.
            
        """

        # Needs to be a new variable to avoid arima_res_.append if not needed
        last_window_check = last_window.copy() if last_window is not None else self.last_window.copy()

        check_predict_input(
            forecaster_type  = type(self).__name__,
            steps            = steps,
            fitted           = self.fitted,
            included_exog    = self.included_exog,
            index_type       = self.index_type,
            index_freq       = self.index_freq,
            window_size      = self.window_size,
            last_window      = last_window_check,
            last_window_exog = last_window_exog,
            exog             = exog,
            exog_type        = self.exog_type,
            exog_col_names   = self.exog_col_names,
            interval         = None,
            alpha            = None,
            max_steps        = None,
            levels           = None,
            series_col_names = None
        )

        # If last_window_exog is provided but no last_window
        if last_window is None and last_window_exog is not None:
            raise ValueError(
                ('To make predictions unrelated to the original data, both '
                 '`last_window` and `last_window_exog` must be provided.')
            )

        # Check if forecaster needs exog
        if last_window is not None and last_window_exog is None and self.included_exog:
            raise ValueError(
                ('Forecaster trained with exogenous variable/s. To make predictions '
                 'unrelated to the original data, same variable/s must be provided '
                 'using `last_window_exog`.')
            )

        if last_window is not None:
            # If predictions do not follow directly from the end of the training 
            # data. The internal statsmodels SARIMAX model needs to be updated 
            # using its append method. The data needs to start at the end of the 
            # training series.

            # check index append values
            expected_index = expand_index(index=self.extended_index, steps=1)[0]
            if expected_index != last_window.index[0]:
                raise ValueError(
                    (f'To make predictions unrelated to the original data, `last_window` '
                     f'has to start at the end of the index seen by the forecaster.\n'
                     f'    Series last index         : {self.extended_index[-1]}.\n'
                     f'    Expected index            : {expected_index}.\n'
                     f'    `last_window` index start : {last_window.index[0]}.')
                )
            
            last_window = transform_series(
                              series            = last_window.copy(),
                              transformer       = self.transformer_y,
                              fit               = False,
                              inverse_transform = False
                          )
            
            # TODO -----------------------------------------------------------------------------------------------------
            # This is done because pmdarima deletes the series name
            # Check issue: https://github.com/alkaline-ml/pmdarima/issues/535
            last_window.name = None
            # ----------------------------------------------------------------------------------------------------------

            # last_window_exog
            if last_window_exog is not None:
                # check index last_window_exog
                if expected_index != last_window_exog.index[0]:
                    raise ValueError(
                        (f'To make predictions unrelated to the original data, `last_window_exog` '
                         f'has to start at the end of the index seen by the forecaster.\n'
                         f'    Series last index              : {self.extended_index[-1]}.\n'
                         f'    Expected index                 : {expected_index}.\n'
                         f'    `last_window_exog` index start : {last_window_exog.index[0]}.')
                    )

                if isinstance(last_window_exog, pd.Series):
                    # pmdarima.arima.ARIMA only accepts DataFrames or 2d-arrays as exog 
                    last_window_exog = last_window_exog.to_frame()
            
                last_window_exog = transform_dataframe(
                                       df                = last_window_exog,
                                       transformer       = self.transformer_exog,
                                       fit               = False,
                                       inverse_transform = False
                                   )

            self.regressor.arima_res_ = self.regressor.arima_res_.append(
                                            endog = last_window,
                                            exog  = last_window_exog,
                                            refit = False
                                        )
            self.extended_index = self.regressor.arima_res_.fittedvalues.index
                        
        # Exog
        if exog is not None:
            if isinstance(exog, pd.Series):
                # pmdarima.arima.ARIMA only accepts DataFrames or 2d-arrays as exog
                exog = exog.to_frame()

            exog = transform_dataframe(
                       df                = exog,
                       transformer       = self.transformer_exog,
                       fit               = False,
                       inverse_transform = False
                   )  
            exog = exog.iloc[:steps, ]

        # Get following n steps predictions
        predictions = self.regressor.predict(
                          n_periods = steps,
                          X         = exog
                      )

        # Reverse the transformation if needed
        predictions = transform_series(
                          series            = predictions,
                          transformer       = self.transformer_y,
                          fit               = False,
                          inverse_transform = True
                      )
        predictions.name = 'pred'
        
        return predictions
    
        
    def predict_interval(
        self,
        steps: int,
        last_window: Optional[pd.Series]=None,
        last_window_exog: Optional[Union[pd.Series, pd.DataFrame]]=None,
        exog: Optional[Union[pd.Series, pd.DataFrame]]=None,
        alpha: float=0.05,
        interval: list=None,
    ) -> pd.DataFrame:
        """
        Forecast future values and their confidence intervals

        Generate predictions (forecasts) n steps in the future with confidence
        intervals. Note that if exogenous variables were used in the model fit, 
        they will be expected for the predict procedure and will fail otherwise.
        
        When predicting using `last_window` and `last_window_exog`, the internal
        statsmodels SARIMAX will be updated using its append method. To do this,
        `last_window` data must start at the end of the index seen by the 
        forecaster, this is stored in forecaster.extended_index.

        Check https://www.statsmodels.org/dev/generated/statsmodels.tsa.arima.model.ARIMAResults.append.html
        to know more about statsmodels append method.

        Parameters
        ---------- 
        steps : int
            Number of future steps predicted.
            
        last_window : pandas Series, default `None`
            Values of the series used to create the predictors needed in the 
            first iteration of prediction (t + 1).

        last_window_exog : pandas Series, pandas DataFrame, default `None`
            Values of the exogenous variables aligned with `last_window`. Only
            need when `last_window` is not None and the forecaster has been
            trained including exogenous variables.
            
        exog : pandas Series, pandas DataFrame, default `None`
            Exogenous variable/s included as predictor/s.
            
        alpha : float, default `0.05`
            The confidence intervals for the forecasts are (1 - alpha) %.
            If both, `alpha` and `interval` are provided, `alpha` will be used.
            
        interval : list, default `None`
            Confidence of the prediction interval estimated. The values must be
            symmetric. Sequence of percentiles to compute, which must be between 
            0 and 100 inclusive. For example, interval of 95% should be as 
            `interval = [2.5, 97.5]`. If both, `alpha` and `interval` are 
            provided, `alpha` will be used.

        Returns 
        -------
        predictions : pandas DataFrame
            Values predicted by the forecaster and their estimated interval:

            - pred: predictions.
            - lower_bound: lower bound of the interval.
            - upper_bound: upper bound interval of the interval.

        """

        # Needs to be a new variable to avoid arima_res_.append if not needed
        last_window_check = last_window.copy() if last_window is not None else self.last_window.copy()

        check_predict_input(
            forecaster_type  = type(self).__name__,
            steps            = steps,
            fitted           = self.fitted,
            included_exog    = self.included_exog,
            index_type       = self.index_type,
            index_freq       = self.index_freq,
            window_size      = self.window_size,
            last_window      = last_window_check,
            last_window_exog = last_window_exog,
            exog             = exog,
            exog_type        = self.exog_type,
            exog_col_names   = self.exog_col_names,
            interval         = interval,
            alpha            = alpha,
            max_steps        = None,
            levels           = None,
            series_col_names = None
        )

        # If last_window_exog is provided but no last_window
        if last_window is None and last_window_exog is not None:
            raise ValueError(
                ('To make predictions unrelated to the original data, both '
                 '`last_window` and `last_window_exog` must be provided.')
            )

        # Check if forecaster needs exog
        if last_window is not None and last_window_exog is None and self.included_exog:
            raise ValueError(
                ('Forecaster trained with exogenous variable/s. To make predictions '
                 'unrelated to the original data, same variable/s must be provided '
                 'using `last_window_exog`.')
            )  

        # If interval and alpha take alpha, if interval transform to alpha
        if alpha is None:
            if 100 - interval[1] != interval[0]:
                raise ValueError(
                    (f'When using `interval` in ForecasterSarimax, it must be symmetrical. '
                     f'For example, interval of 95% should be as `interval = [2.5, 97.5]`. '
                     f'Got {interval}.')
                )
            alpha = 2*(100 - interval[1])/100

        if last_window is not None:
            # If predictions do not follow directly from the end of the training 
            # data. The internal statsmodels SARIMAX model needs to be updated 
            # using its append method. The data needs to start at the end of the 
            # training series.

            # check index append values
            expected_index = expand_index(index=self.extended_index, steps=1)[0]
            if expected_index != last_window.index[0]:
                raise ValueError(
                    (f'To make predictions unrelated to the original data, `last_window` '
                     f'has to start at the end of the index seen by the forecaster.\n'
                     f'    Series last index         : {self.extended_index[-1]}.\n'
                     f'    Expected index            : {expected_index}.\n'
                     f'    `last_window` index start : {last_window.index[0]}.')
                )

            last_window = transform_series(
                              series            = last_window,
                              transformer       = self.transformer_y,
                              fit               = False,
                              inverse_transform = False
                          )

            # TODO -----------------------------------------------------------------------------------------------------
            # This is done because pmdarima deletes the series name
            # Check issue: https://github.com/alkaline-ml/pmdarima/issues/535
            last_window.name = None
            # ----------------------------------------------------------------------------------------------------------

            # Transform last_window_exog    
            if last_window_exog is not None:
                # check index last_window_exog
                if expected_index != last_window_exog.index[0]:
                    raise ValueError(
                        (f'To make predictions unrelated to the original data, `last_window_exog` '
                         f'has to start at the end of the index seen by the forecaster.\n'
                         f'    Series last index              : {self.extended_index[-1]}.\n'
                         f'    Expected index                 : {expected_index}.\n'
                         f'    `last_window_exog` index start : {last_window_exog.index[0]}.')
                    )

                if isinstance(last_window_exog, pd.Series):
                    # pmdarima.arima.ARIMA only accepts DataFrames or 2d-arrays as exog 
                    last_window_exog = last_window_exog.to_frame()
            
                last_window_exog = transform_dataframe(
                                       df                = last_window_exog,
                                       transformer       = self.transformer_exog,
                                       fit               = False,
                                       inverse_transform = False
                                   )

            self.regressor.arima_res_ = self.regressor.arima_res_.append(
                                            endog = last_window,
                                            exog  = last_window_exog,
                                            refit = False
                                        )
            self.extended_index = self.regressor.arima_res_.fittedvalues.index

        # Exog
        if exog is not None:
            if isinstance(exog, pd.Series):
                # pmdarima.arima.ARIMA only accepts DataFrames or 2d-arrays as exog
                exog = exog.to_frame()

            exog = transform_dataframe(
                       df                = exog,
                       transformer       = self.transformer_exog,
                       fit               = False,
                       inverse_transform = False
                   )  
            exog = exog.iloc[:steps, ]

        # Get following n steps predictions with intervals
        predicted_mean, conf_int = self.regressor.predict(
                                       n_periods       = steps,
                                       X               = exog,
                                       alpha           = alpha,
                                       return_conf_int = True
                                   )
                                    
        predictions = predicted_mean.to_frame(name="pred")
        predictions['lower_bound'] = conf_int[:, 0]
        predictions['upper_bound'] = conf_int[:, 1]

        # Reverse the transformation if needed
        if self.transformer_y:
            for col in predictions.columns:
                predictions[col] = transform_series(
                                    series            = predictions[col],
                                    transformer       = self.transformer_y,
                                    fit               = False,
                                    inverse_transform = True
                               )

        return predictions

    
    def set_params(
        self, 
        **params: dict
    ) -> None:
        """
        Set new values to the parameters of the model stored in the forecaster.
        
        Parameters
        ----------
        params : dict
            Parameters values.

        Returns 
        -------
        self
        
        """

        self.regressor = clone(self.regressor)
        self.regressor.set_params(**params)
        self.params = self.regressor.get_params(deep=True)
        
    
    def get_feature_importance(
        self
    ) -> pd.DataFrame:
        """      
        Return feature importance of the regressor stored in the
        forecaster.

        Parameters
        ----------
        self

        Returns
        -------
        feature_importance : pandas DataFrame
            Feature importance associated with each predictor.

        """

        if self.fitted == False:
            raise NotFittedError(
                ("This forecaster is not fitted yet. Call `fit` with appropriate "
                 "arguments before using `get_feature_importance()`.")
            )

        feature_importance = self.regressor.params().to_frame().reset_index()
        feature_importance.columns = ['feature', 'importance']

        return feature_importance