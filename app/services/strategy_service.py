def fetch_closest_ltp(ce_option_data, pe_option_data, entry_price):
    # Initialize variables to store the closest CE and PE last prices
    closest_ce_last_price = None
    closest_pe_last_price = None
    closest_ce_stock = None
    closest_pe_stock = None
    min_ce_difference = float("inf")
    min_pe_difference = float("inf")

    # Iterate through the option_data
    for key, item in ce_option_data.items():
        try:
            ce_last_price = float(item["ltp"])
            ce_difference = abs(entry_price - ce_last_price)
            # Update the closest CE last price if a closer one is found
            if ce_difference < min_ce_difference or (
                ce_difference == min_ce_difference
                and ce_last_price > closest_ce_last_price
            ):
                min_ce_difference = ce_difference
                closest_ce_last_price = ce_last_price
                closest_ce_stock = key
        except ValueError:
            # Handle the case where ce_last_price is not a valid number
            print("Invalid CE last price, not a valid number")

    for key, item in pe_option_data.items():
        try:
            pe_last_price = float(item["ltp"])
            pe_difference = abs(entry_price - pe_last_price)
            # Update the closest PE last price if a closer one is found
            if pe_difference < min_pe_difference or (
                pe_difference == min_pe_difference
                and pe_last_price > closest_pe_last_price
            ):
                min_pe_difference = pe_difference
                closest_pe_last_price = pe_last_price
                closest_pe_stock = key
        except ValueError:
            # Handle the case where ce_last_price is not a valid number
            print("Invalid PE last price, not a valid number")

    # Return the closest CE and PE stock identifiers
    return (
        closest_ce_stock,
        closest_ce_last_price,
        closest_pe_stock,
        closest_pe_last_price,
    )


def find_current_ltp(ce_quotes, pe_quotes, closest_ce_stock, closest_pe_stock):
    new_ce_last_price = None
    new_pe_last_price = None
    try:
        new_ce_last_price = ce_quotes[closest_ce_stock]["ltp"]
        new_pe_last_price = pe_quotes[closest_pe_stock]["ltp"]

    except Exception as e:
        # Handle exceptions
        print(f"Error occurred: {e}")
        # You might want to log the error or handle it in a different way based on your requirements

    return new_ce_last_price, new_pe_last_price


def fetch_closest_ltp_for_reentry(
    ce_quotes, pe_quotes, closest_ce_last_price=None, closest_pe_last_price=None
):
    # Initialize variables to store the closest CE and PE last prices
    closest_stock = None
    closest_last_price = None
    applicable_quotes = None
    min_difference = float("inf")

    # Determine which type of option (CE or PE) we are evaluating based on provided value
    if closest_ce_last_price is not None:
        entry_price = float(closest_ce_last_price)
        opposite_option_type = "PE"
        applicable_quotes = pe_quotes
    elif closest_pe_last_price is not None:
        entry_price = closest_pe_last_price
        opposite_option_type = "CE"
        applicable_quotes = ce_quotes
    else:
        return None, None  # Return None if neither CE_LTP nor PE_LTP is provided

    # Iterate through the option_data to find the closest opposite option (PE or CE)
    for key, item in applicable_quotes.items():
        try:
            if opposite_option_type == "PE":
                current_ltp = float(item["ltp"])
            else:
                current_ltp = float(item["ltp"])

            # Calculate the absolute difference
            difference = abs(entry_price - current_ltp)

            # Update the closest last price if a closer one is found
            if difference < min_difference:
                min_difference = difference
                closest_last_price = current_ltp
                closest_stock = key

        except ValueError:
            # Handle the case where opposite_last_price is not a valid number
            print(f"Invalid {opposite_option_type} last price, not a valid number")

    # Return the closest opposite option (PE or CE) stock identifier and its last price
    return closest_stock, closest_last_price
