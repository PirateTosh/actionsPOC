from flask import request, jsonify
from app.services.backtesting_service import (
    backtesting_report,
    storeTransaction,
    update_and_generate_summary,
)
from app.services.strategy_service import (
    fetch_closest_ltp,
    fetch_closest_ltp_for_reentry,
    find_current_ltp,
)
from app import app
from app.services.order_service import get_quote, place_order
from app.utils.exchange_util import indices_lot_quantity

strategy_executed = (
    False  # Initialize a flag to track if the strategy entry point has been executed
)
closest_ce_stock = None
closest_ce_last_price = None
closest_pe_stock = None
closest_pe_last_price = None
is_strategy_running = None
ce_entry_price = 0.0
pe_entry_price = 0.0
overall_profit_loss = 0.0
unrealised_pl = 0.0
active_orders = []


@app.route("/omegaTron_strategy", methods=["POST"])
def execute_omegaTron_strategy():
    global strategy_executed  # To modify the flag inside the function
    global closest_ce_stock
    global closest_ce_last_price
    global closest_pe_stock
    global closest_pe_last_price
    global ce_entry_price
    global pe_entry_price
    global overall_profit_loss
    global unrealised_pl
    global is_strategy_running
    global active_orders  # Added variable to track active orders

    ce_exit_logic_triggered = False
    pe_exit_logic_triggered = False

    if is_strategy_running is not None and is_strategy_running is True:
        return f"Found another instance of schedular running, skipping this schedule.\n"

    try:
        is_strategy_running = True
        data = request.get_json()

        try:
            entry_price = float(data.get("entry_price"))
            threshold = float(data.get("threshold"))
            userType = str(data.get("usertype"))
            user_guid = str(data.get("guid"))
            date = str(data.get("date"))
            isLastDate = bool(data.get("isLastDate"))
        except ValueError:
            # Handle case where not a valid number
            print("Passed value for entry_price is not a valid number")

        if userType == "Backtesting":
            ce_quotes, pe_quotes, symbol = get_quote(userType, date)
            if len(ce_quotes) == 0 or len(pe_quotes) == 0:
                # Data not found for the date
                is_strategy_running = False
                strategy_executed = False
                if isLastDate:
                    update_and_generate_summary()
                return "Data not found for date"
        else:
            date = None
            ce_quotes, pe_quotes, symbol = get_quote(userType, date)

        if date and date[-5:] == "15:17":
            # Check if there are any active orders
            if active_orders:
                for active_order in active_orders:
                    if active_order[-2:] == "CE":
                        last_price = ce_quotes[active_order]["ltp"]
                    elif active_order[-2:] == "PE":
                        last_price = pe_quotes[active_order]["ltp"]

                    place_order(userType, active_order, True)
                    storeTransaction(1, "bought", active_order, 1, last_price, date)
                active_orders = []
            strategy_executed = False
            is_strategy_running = False
            backtesting_report(date, isLastDate)
            return "All active orders bought back..Exiting"

        # Entry point for the strategy
        if (
            not strategy_executed
        ):  # Check if the strategy entry point has not been executed yet
            (
                closest_ce_stock,
                closest_ce_last_price,
                closest_pe_stock,
                closest_pe_last_price,
            ) = fetch_closest_ltp(ce_quotes, pe_quotes, entry_price)

            if (
                closest_ce_last_price >= threshold
                or closest_pe_last_price >= threshold
                or closest_ce_last_price / closest_pe_last_price >= 2
                or closest_pe_last_price / closest_ce_last_price >= 2
            ):
                is_strategy_running = False
                return f"No stocks availale for selling as per given config.\n\nProfit/Loss:\n  Unrealised: {unrealised_pl} INR\n  Booked: {overall_profit_loss} INR\n"

            place_order(userType, closest_ce_stock, False)
            place_order(userType, closest_pe_stock, False)
            # Store active orders
            active_orders.append(closest_ce_stock)
            active_orders.append(closest_pe_stock)
            storeTransaction(
                1, "sold", closest_ce_stock, 1, closest_ce_last_price, date
            )
            storeTransaction(
                1, "sold", closest_pe_stock, 1, closest_pe_last_price, date
            )
            ce_entry_price = closest_ce_last_price
            pe_entry_price = closest_pe_last_price
            strategy_executed = (
                True  # Set the flag to True after executing the entry point
            )
            is_strategy_running = False
            return f"Active Orders:\n  {closest_ce_stock} @ {closest_ce_last_price}\n  {closest_pe_stock} @ {closest_pe_last_price}\n\nProfit/Loss:\n  Unrealised: {unrealised_pl} INR\n  Booked: {overall_profit_loss} INR\n"

        # Find new closest_ce_last_price and closest_pe_last_price with respect to closest_ce_stock and closest_pe_stock
        closest_ce_last_price, closest_pe_last_price = find_current_ltp(
            ce_quotes, pe_quotes, closest_ce_stock, closest_pe_stock
        )

        # EXIT Logic for strategy - When threshold is reached
        if closest_ce_last_price is not None and threshold < float(
            closest_ce_last_price
        ):
            place_order(userType, closest_ce_stock, True)
            # Remove completed orders from the active orders list
            active_orders.remove(closest_ce_stock)
            storeTransaction(
                1, "bought", closest_ce_stock, 1, closest_ce_last_price, date
            )
            unrealised_pl = overall_profit_loss = overall_profit_loss + (
                float(ce_entry_price) - float(closest_ce_last_price)
            ) * indices_lot_quantity.get(symbol.lower())
            unrealised_pl = round(unrealised_pl, 2)
            overall_profit_loss = round(overall_profit_loss, 2)
            ce_exit_logic_triggered = True

        if closest_pe_last_price is not None and threshold < closest_pe_last_price:
            place_order(userType, closest_pe_stock, True)
            # Remove completed orders from the active orders list
            active_orders.remove(closest_pe_stock)
            storeTransaction(
                1, "bought", closest_pe_stock, 1, closest_pe_last_price, date
            )
            unrealised_pl = overall_profit_loss = overall_profit_loss + (
                float(pe_entry_price) - float(closest_pe_last_price)
            ) * indices_lot_quantity.get(symbol.lower())
            unrealised_pl = round(unrealised_pl, 2)
            overall_profit_loss = round(overall_profit_loss, 2)
            pe_exit_logic_triggered = True

        # EXIT Logic for strategy - When one of PE or CE gets half of the other
        if (
            closest_ce_last_price is not None
            and closest_pe_last_price is not None
            and float(closest_pe_last_price) / float(closest_ce_last_price) >= 2
        ):
            place_order(userType, closest_ce_stock, True)
            active_orders.remove(closest_ce_stock)

            storeTransaction(
                1, "bought", closest_ce_stock, 1, closest_ce_last_price, date
            )
            unrealised_pl = overall_profit_loss = overall_profit_loss + (
                float(ce_entry_price) - float(closest_ce_last_price)
            ) * indices_lot_quantity.get(symbol.lower())
            unrealised_pl = round(unrealised_pl, 2)
            overall_profit_loss = round(overall_profit_loss, 2)
            ce_exit_logic_triggered = True
        elif (
            closest_ce_last_price is not None
            and closest_pe_last_price is not None
            and float(closest_ce_last_price) / float(closest_pe_last_price) >= 2
        ):
            place_order(userType, closest_pe_stock, True)
            active_orders.remove(closest_pe_stock)

            storeTransaction(
                1, "bought", closest_pe_stock, 1, closest_pe_last_price, date
            )
            unrealised_pl = overall_profit_loss = overall_profit_loss + (
                float(pe_entry_price) - float(closest_pe_last_price)
            ) * indices_lot_quantity.get(symbol.lower())
            unrealised_pl = round(unrealised_pl, 2)
            overall_profit_loss = round(overall_profit_loss, 2)
            pe_exit_logic_triggered = True

        # RE-Entry Logic for strategy
        if ce_exit_logic_triggered:
            (
                closest_ce_stock_new,
                closest_ce_last_price_new,
            ) = fetch_closest_ltp_for_reentry(
                ce_quotes, pe_quotes, None, closest_pe_last_price
            )

            if (
                closest_ce_stock == closest_ce_stock_new
                or closest_ce_last_price_new >= threshold
            ):
                place_order(userType, closest_pe_stock, True)
                active_orders.remove(closest_pe_stock)

                storeTransaction(
                    1, "bought", closest_pe_stock, 1, closest_pe_last_price, date
                )
                unrealised_pl = overall_profit_loss = overall_profit_loss + (
                    float(pe_entry_price) - float(closest_pe_last_price)
                ) * indices_lot_quantity.get(symbol.lower())
                unrealised_pl = round(unrealised_pl, 2)
                overall_profit_loss = round(overall_profit_loss, 2)
                strategy_executed = False
                is_strategy_running = False
                return f"No Active Orders.\n\nProfit/Loss:\n  Unrealised: {unrealised_pl} INR\n  Booked: {overall_profit_loss} INR\n"
            else:
                closest_ce_stock = closest_ce_stock_new
                closest_ce_last_price = closest_ce_last_price_new
                ce_entry_price = closest_ce_last_price_new
                place_order(userType, closest_ce_stock, False)
                active_orders.append(closest_ce_stock)

                storeTransaction(
                    1, "sold", closest_ce_stock, 1, closest_ce_last_price, date
                )
        if pe_exit_logic_triggered:
            (
                closest_pe_stock_new,
                closest_pe_last_price_new,
            ) = fetch_closest_ltp_for_reentry(
                ce_quotes, pe_quotes, closest_ce_last_price, None
            )
            if (
                closest_pe_stock == closest_pe_stock_new
                or closest_pe_last_price_new >= threshold
            ):
                place_order(userType, closest_ce_stock, True)
                active_orders.remove(closest_ce_stock)
                storeTransaction(
                    1, "bought", closest_ce_stock, 1, closest_ce_last_price, date
                )
                unrealised_pl = overall_profit_loss = overall_profit_loss + (
                    float(ce_entry_price) - float(closest_ce_last_price)
                ) * indices_lot_quantity.get(symbol.lower())
                unrealised_pl = round(unrealised_pl, 2)
                overall_profit_loss = round(overall_profit_loss, 2)
                strategy_executed = False
                is_strategy_running = False
                return f"No Active Orders.\n\nProfit/Loss:\n  Unrealised: {unrealised_pl} INR\n  Booked: {overall_profit_loss} INR\n"
            else:
                closest_pe_stock = closest_pe_stock_new
                closest_pe_last_price = closest_pe_last_price_new
                pe_entry_price = closest_pe_last_price_new
                place_order(userType, closest_pe_stock, False)
                active_orders.append(closest_pe_stock)
                storeTransaction(
                    1, "sold", closest_pe_stock, 1, closest_pe_last_price, date
                )
        is_strategy_running = False

        closest_ce_last_price_float = (
            float(closest_ce_last_price) if closest_ce_last_price is not None else 0.0
        )
        ce_entry_price_float = float(ce_entry_price)
        pe_entry_price_float = float(pe_entry_price)

        unrealised_pl = (
            overall_profit_loss
            + (
                (ce_entry_price_float - closest_ce_last_price_float)
                * indices_lot_quantity.get(symbol.lower(), 0)
            )
            + (
                (pe_entry_price_float - closest_ce_last_price_float)
                * indices_lot_quantity.get(symbol.lower(), 0)
            )
        )
        unrealised_pl = round(unrealised_pl, 2)
        overall_profit_loss = round(overall_profit_loss, 2)
        return f"Active Orders:\n  {closest_ce_stock}:\n    Entry: {ce_entry_price}\n    LTP: {closest_ce_last_price}\n    SL: {threshold}\n  {closest_pe_stock}:\n    Entry: {pe_entry_price}\n    LTP: {closest_pe_last_price}\n    SL: {threshold}\n\nProfit/Loss:\n  Unrealised: {unrealised_pl} INR\n  Booked: {overall_profit_loss} INR\n"

    except Exception as e:
        is_strategy_running = False
        print({"error": format(str(e))})
        return jsonify({"error": format(str(e))}), 500
