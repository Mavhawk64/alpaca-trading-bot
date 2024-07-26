

# PATH 1 -- Deciding to sell current positions

async def check_current():
    pass


async def get_positions():
    pass


async def decide_sell():
    if False:
        sell()


async def sell():
    price = get_limit_price()
    post_order()


async def get_limit_price():
    return 0


# PATH 2 -- Deciding to buy new positions
async def check_scan():
    pass


async def get_small_cap_stocks():
    pass


async def decide_buy():
    if False:
        buy()


async def buy():
    price, amt = get_limit_price_and_amt()
    post_order()


async def get_limit_price_and_amt():
    return 0, 0


# Finally, post the order
async def post_order():
    pass


async def main():
    pass

if __name__ == "__main__":
    main()
