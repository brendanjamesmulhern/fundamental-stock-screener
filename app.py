import simfin as sf
from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
from datetime import datetime
from datetime import timedelta
from config import api_key
import os

app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
    sf.set_api_key(api_key)
    sf.set_data_dir('~/simfin_data/')
    hub = sf.StockHub(market='us',
                      refresh_days=30,
                      refresh_days_shareprices=1)
    df_fin_signals = hub.fin_signals(variant='latest')
    df_fin_signals.dropna()
    df_fin_signals_2y = hub.fin_signals(variant='latest',
                                        func=sf.avg_ttm_2y)
    df_fin_signals_2y.dropna()
    df_growth_signals = hub.growth_signals(variant='latest')
    df_growth_signals.dropna()
    df_growth_signals_2y = hub.growth_signals(variant='latest',
                                              func=sf.avg_ttm_2y)
    df_growth_signals_2y.dropna()
    df_val_signals = hub.val_signals(variant='latest')
    df_val_signals.dropna()
    df_val_signals_2y = hub.val_signals(variant='latest',
                                        func=sf.avg_ttm_2y)
    df_val_signals_2y.dropna()
    dfs = [df_fin_signals, df_growth_signals, df_val_signals]
    df_signals = pd.concat(dfs, axis=1)
    dfs = [df_fin_signals_2y, df_growth_signals_2y, df_val_signals_2y]
    df_signals_2y = pd.concat(dfs, axis=1)
    mask = (df_signals[P_NETNET] > 0) & (df_signals[P_NETNET] < 1)
    date_limit = datetime.now() - timedelta(days=30)
    df_prices_latest = hub.load_shareprices(variant='latest')
    mask_date_limit = (df_prices_latest.reset_index(DATE)[DATE] > date_limit)
    mask &= mask_date_limit
    out = {
      "netToNetStocks": df_signals.loc[mask, P_NETNET],
      "1yrSignals": df_fin_signals,
      "2yrSignals": df_fin_signals_2y,
      "df_growth_signals": df_growth_signals,
      "df_growth_signals_2y": df_growth_signals_2y,
      "df_val_signals": df_val_signals,
      "df_val_signals_2y": df_val_signals_2y
    };
    return jsonify(out.to_json())

if __name__ == "__main__":
  app.run()
