# Infinity-Pool-Balancer
n-Asset Invariant Liquidity Pool



# ╦╔╗╔╔═╗╦╔╗╔╦╔╦╗╦ ╦  ╔═╗╔═╗╔═╗╦  
# ║║║║╠╣ ║║║║║ ║ ╚╦╝  ╠═╝║ ║║ ║║  
# ╩╝╚╝╚  ╩╝╚╝╩ ╩  ╩   ╩  ╚═╝╚═╝╩═╝

A non-custodial portfolio manager, liquidity provider, and price sensor.


model by
                                                       
litepresence 2023 wtfpl

as per whitepaper by

Fernando Martinelli
Nikolai Mushegian
2019-09-19
pool.fi/whitepaper.pdf

Usage:

```# Instantiate the InfinityPool
pool = InfinityPool(["X", "Y", "Z"])

# Initialize the pool
pool.equalize(
    ({"X": 1.0, "Y": 2.0, "Z": 3.0}, 0)
    ({"X": 0, "Y": 0, "Z": 0}, 0)
)

# Trade (...)
pool.equalize(
    ({"X": 2.0, "Y": 0, "Z": 33.0}, 1.0)
    ({"X": 0, "Y": 7.0, "Z": 3.0}, 7.0)
)
pool.equalize(
    ({"X": 2.0, "Y": 2.0, "Z": 1.0}, 1.0)
    ({"X": 5.0, "Y": 0, "Z": 6.0}, 5.0)
)
pool.equalize(
    ({"X": 8.0, "Y": 4.0, "Z": 1.0}, 1.0)
    ({"X": 3.0, "Y": 1.0, "Z": 3.0}, 0.0)
)```
