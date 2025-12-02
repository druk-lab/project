import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

def forecast_sales(daily_sales: pd.Series, steps: int = 30) -> pd.Series:
    """
    daily_sales: индекс — даты, значения — сумма продаж.
    Возвращает прогноз на steps дней.
    """
    # Очень простой вариант, без подбора p,d,q:
    model = ARIMA(daily_sales, order=(1,1,1))
    fitted = model.fit()
    forecast = fitted.forecast(steps=steps)
    return forecast
