import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime
import logging
import ast

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("../log/scheduler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('APScheduler')


# Define trading parameters
timeframe = mt5.TIMEFRAME_H1  # 15-minute timeframe
short_window = 50  # Short-term moving average window
long_window = 100  # Long-term moving average window

# login details
login = int(input("Pls type in your login code here: "))
password = input("Pls type in your password code here: ")
server = input("Pls type in your server here: ")


# currency list
def get_currency_list():
    """ get currency list  
       
        return: a list of currency  
           """
    
    logger.info('Getting currency list ... ')
    our_curr = ["EUR", "USD", "GBP", "JPY", "CHF", "NZD", "CAD", "BTC", "ETH", 'SOL', "BCH", "BNB", "LTC", "DOG"]
    # input_data = input("Pls type in the currency you would like to trade today eg. ['EUR', 'USD', 'GBP']: ")
    #
    # # Safely parse the input as a list
    # currencies = ast.literal_eval(input_data)
    return our_curr


def connect_MT5():
    """ Initialize connection to MT5 """
    # Initialize connection to MetaTrader 5
    if not mt5.initialize():
        logger.info("initialize() failed, error code =", mt5.last_error())
        quit()


def shutdown_MT5():
    """Shut down the MT5 connection."""
    mt5.shutdown()


# signin
def signin():
    """ sigin to MT5 with logins 

        return: signin response  
           """
    try:
        signin = mt5.login(login, password, server)
        logger.info(F"signin {signin}")
        return signin

    except mt5.last_error() as e:
        logger.info(e)


def get_acc_info():
    """ Retrieve account information
    
        return: account balance
        
        """
    # Retrieve account information
    account_info = mt5.account_info()

    # Check if successfully retrieved the account information
    if account_info is None:
        logger.info("Failed to retrieve account information. Error:", mt5.last_error())
    else:
        acc_balance = account_info.balance
        # logger.info account balance
        logger.info(f"Account Balance: {acc_balance}")
        return acc_balance


def get_symbols_data():
    """Get all symbols available for trading and save it to symbols_info.csv file  """
    # Get all symbols available for trading
    symbols = mt5.symbols_get()

    # Prepare a list to hold symbol information
    symbols_data = []

    # Check if any symbols were retrieved
    if symbols is not None:
        logger.info(f"Total symbols available: {len(symbols)}\n")

        # Loop through each symbol to get detailed information
        for symbol in symbols:
            # Get detailed information for each symbol
            symbol_info = mt5.symbol_info(symbol.name)

            if symbol_info is not None:
                # Append symbol information to the list as a dictionary
                symbols_data.append({
                    'Symbol': symbol_info.name,
                    'Description': symbol_info.description,
                    'Base Currency': symbol_info.currency_base,
                    'Profit Currency': symbol_info.currency_profit,
                    'Min Lot Size': symbol_info.volume_min,
                    'Max Lot Size': symbol_info.volume_max,
                    'Lot Step Size': symbol_info.volume_step,
                    'Trade Mode': symbol_info.trade_mode,
                    'Spread': symbol_info.spread,
                    'Digits': symbol_info.digits,
                    'Expiration Date': symbol_info.expiration_time
                })
            else:
                logger.info(f"Failed to get info for symbol: {symbol.name}")

    else:
        logger.info("No symbols found, error code:", mt5.last_error())

    # Convert the list of dictionaries into a pandas DataFrame
    df_symbols = pd.DataFrame(symbols_data)

    # Display the DataFrame
    logger.info('data frame gotten')

    # Optionally, save the DataFrame to a CSV file
    df_symbols.to_csv('symbols_info.csv', index=False)


# Fetch historical data
def fetch_data(symbol, num_bars):
    """ Fetch historical data
            Args:
                symbol : symbol of currency in MT5
                num_bars: this the degree on how much data to be gotten

            return: data of the symbol placed in it
            """
    rates = mt5.copy_rates_from(symbol, timeframe, datetime.now(), num_bars)
    data = pd.DataFrame(rates)
    data['time'] = pd.to_datetime(data['time'], unit='s')
    return data


# Calculate moving averages
def calculate_moving_averages(data, short_window, long_window):
    """ calculate moving average
            Args:
                data : data gotten form fetch_data() function
                short_window: short moving average
                long_window: long moving average

            return: data after calculating moving averages
            """
    data['short_ma'] = data['close'].rolling(window=short_window).mean()
    data['long_ma'] = data['close'].rolling(window=long_window).mean()
    return data


# Generate trading signals
def generate_signals(data):
    """ Generate trading signals
            Args:
                data : data gotten form calculate_moving_averages() function

            return: data signal
            """
    data['signal'] = 0  # Initialize signal column with 0
    # Detect where short_ma crosses above long_ma (Buy signal: 1) or below (Sell signal: -1)
    data.loc[short_window:, 'signal'] = np.where(
        data['short_ma'][short_window:] > data['long_ma'][short_window:], 1, 0
    )
    # Calculate position changes (diff of signals)
    data['position'] = data['signal'].diff()
    return data


def read_symbols_csv():
    """ read csv file """
    df = pd.read_csv("symbols_info.csv")
    return df


# place trade
def send_buy_order(ticker):
    """ sends buy order to the MT5 account
           Args:
               ticker : symbol of the pair to buy

           return: result of the buy order placed
           """

    symbol = ticker
    lot = 0.1
    point = mt5.symbol_info(symbol).point
    price = mt5.symbol_info_tick(symbol).ask # gives current price
    sl = price - 100 * point
    tp = price + 100 * point
    deviation = 20
    comment = "python script open"

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": deviation,
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    # send a trading request
    result = mt5.order_send(request)
    return result


def send_sell_order(ticker):
    """ sends sell order to the MT5 account
              Args:
                  ticker : symbol of the pair to sell

              return: result of the sell order placed
              """
    # place trade
    symbol = ticker
    lot = 0.1
    point = mt5.symbol_info(symbol).point
    price = mt5.symbol_info_tick(symbol).ask # gives current price
    sl = price + 100 * point
    tp = price - 100 * point
    deviation = 20
    comment = "python script open"

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": deviation,
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    # send a trading request
    result = mt5.order_send(request)
    return result


def check_order_status(result):
    """ check the order status """

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        logger.info("Failed to place sell order. Error:", result.comment)
    else:
        logger.info(f"Sell order placed successfully. Order ticket: {result.order}")

# print(f"login type{type(login)}, {login}")
# print(f"password type{type(password)}, {password}")
# print(f"server type{type(server)}, {server}")
#
# curry = get_currency_list()
# print(f"curry type{type(curry)}, {curry}")