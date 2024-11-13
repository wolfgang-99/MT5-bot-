from server import *
import logging


# setting up logging
logger = logging.getLogger("algo.py")

max_drawdown_percentage = 0.07  # 8% max drawdown


def check_max_drawdown(account_balance, initial_balance):
    """Check if the max drawdown (7%) is reached."""
    if account_balance < initial_balance * (1 - max_drawdown_percentage):
        logger.info(" Almost reached Max drawdown at 7% of the account maximum drawdown. Stopping trading.")
        return False
    return True


def update_daily_loss_limit(current_balance):
    """ update daily loss limit
        Args:
            current_balance: current balance of the account

        return: daily_loss_limit
        """

    logger.info("updating daily loss limit ...")
    daily_loss_lim = 0.04 * current_balance
    return daily_loss_lim


def calculate_max_daily_loss(start_of_day_balance):
    """ calculate max daily loss
        Args:
            start_of_day_balance : current balance of the account at the start of the day

        return: max_daily_loss
        """
    logger.info("calculating max daily loss ...")
    max_daily_loss = 0.04 * start_of_day_balance
    return max_daily_loss


# Main function
def main():
    """ This the main functions that calls funtions from server.py to login, generate signal and place trade
        if all conditions are meet
     """

    logger.info('connecting to MT5 ...')
    connect_MT5()

    logger.info('signin to MT5 ...')
    if signin():
        start_of_day_balance = get_acc_info()  # initial acc balance
        get_symbols_data()
        df = read_symbols_csv()
        our_curr_list = get_currency_list()

        # calculate max daily loss limit
        max_daily_loss = calculate_max_daily_loss(start_of_day_balance)

        # check max account loss  before trade
        current_balance = get_acc_info()
        max_drawdown = check_max_drawdown(current_balance, start_of_day_balance)
        if max_drawdown:

            for p1 in our_curr_list:
                for p2 in our_curr_list:
                    ticker = f"{p1}{p2}"
                    if ticker in df.Symbol.unique():

                        # Fetch data for the symbol
                        data = fetch_data(ticker, long_window + 500)  # Get enough data for calculation
                        data = calculate_moving_averages(data, short_window, long_window)
                        data = generate_signals(data)

                        # logger data to check moving averages and signals
                        logger.info(" Debugging: Viewing the last few rows of the data")
                        logger.info(data.tail())  # Debugging: View the last few rows of the data

                        # Plot the moving averages
                        # plot_moving_averages(data)

                        # Check the latest signal
                        latest_signal = data.iloc[-1]['position']

                        # check daily loss before trade
                        current_balance = get_acc_info()
                        daily_lost_limit = update_daily_loss_limit(current_balance)

                        logger.info("checking if daily loss limit is reached ...")
                        if daily_lost_limit > max_daily_loss :
                            logger.info(f'daily lost limit reached at {daily_lost_limit}. shutting down MT5')
                            shutdown_MT5()
                            break

                        else:
                            logger.info("placing trade ...")
                            if latest_signal == 1:
                                logger.info(f"Buy signal for {ticker}")
                                # code to place a buy order
                                result = send_buy_order(ticker)

                                # check order status
                                check_order_status(result)

                            elif latest_signal == -1:
                                logger.info(f"Sell signal for {ticker}")
                                # code to place a sell order
                                result = send_sell_order(ticker)

                                # check order status
                                check_order_status(result)

                            elif latest_signal == 2:
                                logger.info(f"Strong buy signal for {ticker}")
                                # Place a buy order, or take other bullish actions
                                result = send_buy_order(ticker)

                                # check order status
                                check_order_status(result)

                            elif latest_signal == -2:
                                logger.info(f"Strong sell signal for {ticker}")
                                # Place a sell order, or take other bearish actions
                                result = send_sell_order(ticker)

                                # check order status
                                check_order_status(result)

                            else:
                                logger.info(f"No trade signal for {ticker}")


