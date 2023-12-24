"""
╦╔╗╔╔═╗╦╔╗╔╦╔╦╗╦ ╦  ╔═╗╔═╗╔═╗╦  
║║║║╠╣ ║║║║║ ║ ╚╦╝  ╠═╝║ ║║ ║║  
╩╝╚╝╚  ╩╝╚╝╩ ╩  ╩   ╩  ╚═╝╚═╝╩═╝

model by
                                                       
litepresence 2023 wtfpl

as per whitepaper by

Fernando Martinelli
Nikolai Mushegian
2019-09-19
pool.fi/whitepaper.pdf

Usage:

# Instantiate the InfinityPool
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
)
"""
# STANDARD MODULES
import math
from typing import Dict, Tuple

# GLOGAL CONSTANTS
SUPPLY = 10.0**15  # maximum supply of pool shares
FIRST = 10.0**8  # amount of shares issued to first depositor


class InfinityPool:
    """
    A non-custodial portfolio manager, liquidity provider, and price sensor.
    """

    def __init__(self, tokens: list):
        if len(tokens) < 2:
            raise ValueError("There must be at least two tokens in the pool.")

        # list() of token names used to instantiate the InfinityPool
        self.tokens = tokens
        # dict() of weights for each token established upon the first deposit
        self.weights = {token: 0.0 for token in tokens}
        # dict() of current balances of each token held by the pool
        self.balances = {token: 0.0 for token in tokens}
        # the total pool shares currently issued by the pool
        self.shares_issued = 0.0
        # the current size of the swap invariant k
        self.invariant = 0.0

    def status(self) -> dict:
        """
        A dictionary of all items in the InfinityPool's namespace
        """
        return {
            "tokens": self.tokens,
            "weights": self.weights,
            "balances": self.balances,
            "shares_supply": SUPPLY,
            "shares_issued": self.shares_issued,
            "invariant": self.invariant,
        }

    def initialize(self, amount_in: Dict[str, float]) -> None:
        """
        Upon the first deposit initialize the pool balances and weights
        """
        if set(amount_in.keys()) != set(self.tokens):
            raise ValueError("Keys of new balances must match the tokens in the pool.")
        if any(balance <= 0 for balance in amount_in.values()):
            raise ValueError("Initial balances must be greater than zero.")
        self.balances = amount_in
        self.weights = {t: amount_in[t] / sum(amount_in.values()) for t in self.tokens}
        self.shares_issued = FIRST

    def set_invariant(self) -> float:
        """
        InfinityPool’s exchange functions is a surface defined by constraining a value
        function of the pool’s weights and balances to a constant. This surface implies
        a spot price at each point such that, no matter what exchanges are carried out,
        the share of value of each token in the pool remains constant.

        The value function is defined as:

        k=1
        for t in range len(b):
            k *= b[t]**w[t]

        Where
            t ranges over the tokens in the pool;
            b is the balance of each token in the pool;
            w is the normalized weight of each token such that sum of all weights is 1;
            k constant defining an invariant-value surface;

        Note
            k remains constant during swap operations;
            k increases after a deposit of tokens to obtain pool shares;
            k decreases after a withdrawal of pool shares to obtain tokens;
            k defaults to zero before the pool has an initial deposit
        """
        if self.weights[self.tokens[0]]:
            invariant = 1
            for token in self.tokens:
                invariant *= self.balances[token] ** self.weights[token]
            self.invariant = invariant
        return self.invariant

    def calculate_spot_price(self, asset: str, currency: str) -> float:
        """
        Args:

        str(asset): token name of the asset being valued
        str(currency): token name of the currency the asset is being valued in

        Returns:

        float() the price of i per o


        Each pair of tokens in a pool has a spot price defined entirely by the weights
        and balances of just that pair of tokens.

        The spot price (sp) between any two tokens is the the ratio of the token
        balances normalized by their weights:

        sp = (bi/wi)/(bo/wo)

        Where:

        bi is the balance of token i
        bo is the balance of token o
        wi is the weight of token i
        wo is the weight of token o
        """
        if asset not in self.tokens or currency not in self.tokens:
            raise ValueError("Invalid token indices.")

        return (self.balances[asset] / self.weights[asset]) / (
            self.balances[currency] / self.weights[currency]
        )

    def deposit_all(self, amount_in: Dict[str, float]) -> float:
        """
        Args:

        dict(amount_in) an amount of each token to deposit with dict keys corresponding to tokens

        Returns:

        float(shares_to_issue) the pool issued amount of share tokens given to the depositor

        Pool Tokens

        Pools can aggregate the liquidity provided by several different users.
        In order for them to be able to freely deposit and withdraw assets from the pool,
        InfinityPool Protocol has the concept of pool tokens.
        Pool tokens represent ownership of the assets contained in the pool.
        The outstanding supply of pool tokens is proportional to the Value Function of the pool.
        If a deposit of assets increases the pool Value Function by 10%,
        then the outstanding supply of pool tokens also increases by 10%.
        This is because the depositor is issued 10% of new pool tokens in return for the deposit.


        An “all-asset” deposit has to follow the distribution of existing assets in the pool.
        If the deposit contains 10% of each of the assets already in the pool,
        then the Value Function will increase by 10%
        and the depositor will be minted 10% of the current outstanding pool token supply.
        So to receive pool issued (pi) pool tokens
        given an existing total supply of pool supply (ps),
        one needs to deposit tokens (dk) for each of the tokens in the pool:

        dk = (((ps + pi)/ps)-1)*bk

        Simplified

        dk = (pi*bk)/ps

        Solving for pool shares issued

        pi = (dk*ps)/bk

        Where

        ps is the total pool share supply
        pi is the amount the pool will issue to the user of pool shares
        dk is the amount of each token the user will give
        bk is the amount of each token the pool has before deposit dk
        """
        # Iterate over each token in the deposit
        for token, amount in amount_in.items():
            # Ensure the amount in is positive
            if amount <= 0:
                raise ValueError(f"Amount in {token} quantity {amount} must be positive")
        
        # if the pool has an inital deposit
        if self.weights[self.tokens[0]]:
            if not self.check_deposit_ratio(amount_in, tolerance=1e-6):
                raise ValueError(
                    "The deposit ratio does not match the existing token balances"
                    " ratio."
                )
            for token in self.tokens:
                self.balances[token] += amount_in[token]
            # pi = (dk*ps)/bk
            shares_to_issue = (amount_in[self.tokens[0]] * SUPPLY) / self.balances[
                self.tokens[0]
            ]
        else:

            # the first deposit in the pool sets the pool weights
            self.initialize(amount_in)
            shares_to_issue = FIRST

        # invariant K gets updated after every deposit or withdrawal
        self.set_invariant()
        return shares_to_issue

    def check_deposit_ratio(
        self, amount_in: Dict[str, float], tolerance: float = 1e-9
    ) -> bool:
        """
        Check if the ratio of the deposit is close to the ratio of pool balances.

        Args:
            amount_in (dict): An amount of each token to deposit with keyed by token.
            tolerance (float): Tolerance for comparing ratios.

        Returns:
            bool: True if the ratio is close, False otherwise.
        """
        existing_ratio = [
            balance / sum(self.balances.values())
            for token, balance in self.balances.items()
        ]
        deposit_ratio = [
            amount / sum(amount_in.values()) for token, amount in amount_in.items()
        ]

        return all(
            math.isclose(existing, deposit, rel_tol=tolerance)
            for existing, deposit in zip(existing_ratio, deposit_ratio)
        )

    def deposit_one(self, amount_in: Dict[str, float]) -> float:
        """
        Args:

        dict(amount_in) an amount of each token to deposit with dict keys corresponding to tokens

        Returns:

        float(pi) the pool issued amount of share tokens given to the depositor

        NOTE: all Dict values must be zero except for the deposited one, key indicates token (t)

        Single-Asset Deposit
        When a user wants to provide liquidity to a pool, they may likely not have all of the assets
        in the right proportions required for a weighted-asset deposit.
        InfinityPool allows anyone to get pool tokens from a shared pool by depositing a single asset,
        provided that the pool contains that asset.

        pi = ps*((1+(at/bt)^wt-1)

        where
        ps is the pool supply
        pi is the amount of pool shares the pool will issue
        at is the amount of asset t the user deposited
        bt is the balance of asset t in the pool prior to deposit
        wt is the static weight of asset t set at pool genesis

        Depositing a single asset A to a shared pool is equivalent to depositing all pool assets
        proportionally and then selling more of asset A to get back all the other tokens deposited.
        This way a depositor would end up spending only asset A,
        since the amounts of the other tokens deposited would be returned through the trades.
        """
        # Ensure pool has an initial deposit
        if not self.weights[self.tokens[0]]:
            raise ValueError(
                "Single-asset deposit is not allowed until weights are assigned."
            )
        # Ensure that only one element of the amount_in is non-zero
        if sum(1 for amount in amount_in.values() if amount != 0) != 1:
            raise ValueError("Exactly one element in amount_in should be non-zero.")
        # Find the key of the non-zero element
        t_key = next(key for key, amount in amount_in.items() if amount != 0)
        # Ensure the amount in is positive
        if amount_in[t_key] < 0:
            raise ValueError("The deposited amount must be positive")
        # pi = ps*((1+(at/bt)^wt-1)
        shares_to_issue = SUPPLY * (
            1 + (amount_in[t_key] / self.balances[t_key]) ** self.weights[t_key] - 1
        )
        # update the pool balance for this token
        self.balances[t_key] += amount_in[t_key]
        # update the total pool shares issued
        self.shares_issued += shares_to_issue
        # Update the invariant K after every deposit or withdrawal
        self.set_invariant()
        # issue the shares to the user
        return shares_to_issue

    def deposit_any(self, amount_in: Dict[str, float]) -> float:
        """
        This is not mentioned in the whitepaper but through summation:
        Multi Token Deposit for Pool Shares

        Args:
            amount_in (dict): Amount of each token to deposit with keys corresponding to tokens.

        Returns:
            float: The pool issued amount of share tokens given to the depositor.

        NOTE: The 'amount_in' dictionary can include any number of tokens or zero amounts.

        Mixed Asset Deposit:
        Accepts a dictionary 'amount_in'; the amount of each token the user wants to deposit.
        Iterates over the dictionary and calculates the sum shares to issue for the mixed deposit.

        pi = Σ(ps*((1+(at/bt)^wt-1))

        where
        ps is the pool supply
        pi is the amount of pool shares the pool will issue
        at is the amount of asset t the user deposited
        bt is the balance of asset t in the pool prior to deposit
        wt is the static weight of asset t set at pool genesis
        """
        # Ensure the pool has an initial deposit
        if not self.weights[self.tokens[0]]:
            raise ValueError("Must use deposit_all on first deposit")
        # Iterate over each token in the deposit
        for token, amount in amount_in.items():
            # Ensure the amount in is positive
            if amount < 0:
                raise ValueError("The deposited amount must be positive")
        # Iterate over each token in the deposit
        for token, amount in amount_in.items():
            # Ensure the amount in is positive
            # Update the pool balance for this token
            self.balances[token] += amount
        # Calculate the total pool shares to issue
        # pi = ps*((1+(at/bt)^wt-1)
        shares_to_issue = sum(
            SUPPLY
            * (1 + (amount_in[token] / self.balances[token]) ** self.weights[token] - 1)
            for token in self.tokens
        )
        # Update the invariant K after every deposit or withdrawal
        self.set_invariant()

        # Return the total pool shares issued to the user
        return shares_to_issue

    def withdraw_all(self, redeem: float) -> Dict[str, float]:
        """

        Args:
            float(redeem) : amount of share tokens the user is redeeming

        Return:
            dict(amount_out): amounts of each token the user will receive

        A weighted-asset withdrawal is the reverse operation where a pool token holder redeems their
        pool tokens in return for a proportional share of each of the assets held by the pool.
        By redeeming pool redeemed (pd) pool tokens given an existing total pool supply of (ps),
        one withdraws from the pool an amount (at) of token t for each of the tokens in the pool:

        at = (1-((ps-pd)/ps))*bt

        Where
        bt is the token balance of token t before the withdrawal
        ps is the pool supply
        pd is the amount of pool tokens the user is redeeming

        """
        # Ensure the pool has an inital deposit
        if not self.weights[self.tokens[0]]:
            raise ValueError("Withdrawal is not allowed until weights are assigned.")
        # reserve the redeemed shares
        self.shares_issued -= redeem
        # at = (1-((ps-pd)/ps))*bt
        amount_out = {
            token: (1 - ((SUPPLY - redeem) / SUPPLY)) * self.balances[token]
            for token in self.tokens
        }
        # update the balances
        self.balances = {
            token: self.balances[token] - amount_out[token] for token in self.tokens
        }
        # Update the invariant K after every deposit or withdrawal
        self.set_invariant()

        return amount_out

    def withdraw_one(self, token: str, redeem: float) -> float:
        """
        Perform a single-asset withdrawal from the pool.

        Args:
            token (str): The name of the pool token to be redeemed.
            pool_tokens (float): The amount of pool tokens the user wishes to redeem.

        Returns:
            dict: A dictionary containing the withdrawn amount for each token.


        Single-Asset Withdrawal:
        When a pool token holder redeems their pool tokens for a single asset,
        the amount withdrawn in asset 't' is given by:

        at = bt * (1 - (1 - (pd / ps)) ** (1 / wt))

        where:
        - ps is the total pool supply.
        - pd is the amount of pool shares the user wants to redeem.
        - at is the amount of asset 't' the user will receive.
        - bt is the balance of asset 't' in the pool prior to withdrawal.
        - wt is the static weight of asset 't' set at pool genesis.

        Note: Using the deposit and withdrawal formulas without considering fees,
        depositing 'at' asset for pool tokens and then redeeming the same amount
        of pool tokens for asset 't' should result in getting the same 'at' back.
        """
        # Ensure the pool has an inital deposit
        if not self.weights[0]:
            raise ValueError("Withdrawal is not allowed until weights are assigned.")
        # reserve the redeemed shares
        self.shares_issued -= redeem
        # at = bt * (1 - (1 - (pd / ps)) ** (1 / wt))
        amount_out = self.balances[token] * (
            1 - (1 - (redeem / SUPPLY)) ** (1 / self.weights[token])
        )
        # update the balances
        self.balances[token] -= amount_out
        # Update the invariant K after every deposit or withdrawal
        self.set_invariant()

        return amount_out

    def withdraw_any(self, redeem: float, ratios: Dict[str, float]) -> float:
        """
        This is not mentioned in the whitepaper but through summation:
        Perform a multi-token withdrawal from the pool.

        Args:
            redeem (dict): The ratio of pool tokens the user wishes to redeem.

        Returns:
            (dict): a dict of pool token amounts the user receives.


        Single-Asset Withdrawal:
        When a pool token holder redeems their pool tokens for a single asset,
        the amount withdrawn in asset 't' is given by:

        at = Σ(bt * (1 - (1 - (pd / ps)) ** (1 / wt)))

        where:
        - ps is the total pool supply.
        - pd is the amount of pool shares the user wants to redeem.
        - at is the amount of asset 't' the user will receive.
        - bt is the balance of asset 't' in the pool prior to withdrawal.
        - wt is the static weight of asset 't' set at pool genesis.

        Note: Using the deposit and withdrawal formulas without considering fees,
        depositing 'at' asset for pool tokens and then redeeming the same amount
        of pool tokens for asset 't' should result in getting the same 'at' back.
        """
        # Ensure the pool has an inital deposit
        if not self.weights[0]:
            raise ValueError("Withdrawal is not allowed until weights are assigned.")
        # reserve the redeemed shares
        self.shares_issued -= redeem
        # at = Σ(bt * (1 - (1 - (pd / ps)) ** (1 / wt)))
        amount_out = {}
        for token, ratio in ratios.items():
            amount_out[token] = self.balances[token] * (
                1
                - (1 - ((ratio / sum(ratios.values())) / SUPPLY))
                ** (1 / self.weights[token])
            )
            self.balances -= amount_out[token]
        # Update the invariant K after every deposit or withdrawal
        self.set_invariant()
        return amount_out

    def swap(self, t_in: str, t_out: str, amount_in: float) -> float:
        """
        Args:

        str(t_in): name of the token being swapped in
        str(t_out): name of the token being swapped out
        float(amount_in): the amount of token being swapped in

        Returns:

        float(amount_out) the amount of token o being swapped out

        Calculating the trade outcomes for any given InfinityPool Pool is easy
        if we consider that the Value Function must remain invariant,
        i.e. must have the same value before and after any trade.

        When a user sends ai tokens to get ao tokens ,
        all other token balances remain the same.
        Therefore, if we define ai as the amount of tokens and exchanged,
        we can calculate the amount ao a users gets when sending ai.
        The value function after the trade should be the same as before the trade,

        Thus we can write:

        ao = bo*(1-(bi/(bi+ai)^(wi/wo)))

        i is the asset the user is giving the into the pool
        o is the asset the user is getting back out
        wi is the static weight of asset i set at pool genesis
        wo is the static weight of asset o set at pool genesis
        bi is amount of balance i in the pool prior to swap
        bo is amount of balance o in the pool prior to swap
        ai is the amount swapping into the pool
        ao is the amount the pool gives back
        """
        # Ensure the pool has an inital deposit
        if not self.weights[self.tokens[0]]:
            raise ValueError("No swaps until first deposit.")
        # Ensure the tokens are traded in this pool
        if t_in not in self.tokens or t_out not in self.tokens:
            raise ValueError("Invalid token indices.")
        # Ensure the tokens don't match
        if t_in == t_out:
            raise ValueError("Cannot swap token for itself")
        # ao = bo*(1-(bi/(bi+ai)^(wi/wo)))
        amount_out = self.balances[t_out] * (
            1
            - (self.balances[t_in] / (self.balances[t_in] + amount_in))
            ** (self.weights[t_in] / self.weights[t_out])
        )
        self.balances[t_in] += amount_in
        self.balances[t_out] -= amount_out

        return amount_out

    def equalize(
        self,
        inputs: Tuple[Dict[str, float], float],
        ratio_out: Tuple[Dict[str, float], float],
    ) -> Tuple[Dict[str, float], float]:
        """
        Equalize the pool by adjusting the token balances to match the specified output ratio.

         Args:
             inputs (Tuple[Dict[str, float], float]):
                A tuple containing an input dictionary of tokens and their amounts,
                and the amount of pool shares to be deposited.
             ratio_out (Tuple[Dict[str, float], float]):
                A tuple containing a ratio dictionary of desired tokens outputs,
                and the ratio of pool shares to be redeemed.

         Returns:
             Tuple[Dict[str, float], float]:
                A tuple containing an output dictionary of returned tokens amounts,
                 and the amount of pool shares issued.

         Raises:
             ValueError: If the pool has no initial deposit
                and the specified output ratio is non-zero,
                or if share redemption is specified on the first deposit,
                or if the first deposit does not contain some of each token.

         Note:
             This method is the primary function exposed to the user.
        """
        sum_tokens_ratio = sum(ratio_out[0].values())
        # Ensure the pool has an inital deposit
        if self.weights[self.tokens[0]]:
            # deposit all tokens given by the user and add shares given by the user
            shares_owed = inputs[1] + self.deposit_any(inputs[0])
            # determine how much of the equalize request was tokens vs shares
            denom = sum_tokens_ratio + ratio_out[1]
            token_ratio = sum_tokens_ratio / denom
            share_ratio = 1 - token_ratio
            # cash in some of the shares to withdraw tokens
            tokens_out = self.withdraw_any(shares_owed * token_ratio, ratio_out[0])
            # remaining shares are returned
            shares_out = shares_owed * share_ratio

        else:
            # Initialze the pool
            if sum_tokens_ratio + ratio_out[1]:
                raise ValueError("Cannot specify output ratio on initial deposit")
            if inputs[1]:
                raise ValueError("Cannot specify share redemption on first deposit")
            if not all(inputs[0].values()):
                raise ValueError("First deposit must contain some of each token")
            tokens_out = {token: 0.0 for token in self.tokens}
            shares_out = self.deposit_all(inputs[0])

        return (tokens_out, shares_out)


def main():
    """
    Unit Tests
    """

    # Example usage of the InfinityPool class with three tokens

    # Define the tokens in the pool
    tokens = ["X", "Y", "Z"]

    # Instantiate the InfinityPool
    pool = InfinityPool(tokens)

    # Check the initial status of the pool
    print("Infinity Pool Status:")
    print(pool.status())

    # DEPOSITS

    # ALL: Initialize Pool weights by deposit some tokens into the pool using deposit_all
    deposits = {"X": 200.0, "Y": 300.0, "Z": 150.0}
    shares = pool.deposit_all(deposits)
    print(f"\nDeposit All Assets Result: {deposits} -> {shares} Pool Shares")
    print("Infinity Pool Status:")
    print(pool.status())

    # ONE: Deposit a single asset into the pool
    deposit = {"X": 100.0, "Y": 0.0, "Z": 0.0}
    shares = pool.deposit_one(deposit)
    print(f"\nDeposit One Asset Result: {deposit} -> {shares} Pool Shares")
    print("Infinity Pool Status:")
    print(pool.status())

    # ANY: Deposit arbitrary tokens into the pool using deposit_any
    deposits = {"X": 200.0, "Y": 300.0, "Z": 0}
    shares = pool.deposit_any(deposits)
    print(f"\nDeposit Any Asset Result: {deposits} -> {shares} Pool Shares")
    print("Infinity Pool Status:")
    print(pool.status())

    # WITHDRAWALS

    # ALL: Withdraw equal value of all tokens from the pool
    pool_shares = 20
    withdrawn_wallet = pool.withdraw_all(pool_shares)
    print(f"\nWithdraw All Assets {pool_shares} Result: {withdrawn_wallet} X")
    print("Infinity Pool Status:")
    print(pool.status())

    # ONE: Withdraw a single asset from the pool
    withdrawn_single_asset = pool.withdraw_one("X", 20.0)
    print(f"\nWithdraw One Asset Result: {withdrawn_single_asset} A")
    print("Infinity Pool Status:")
    print(pool.status())

    # ANY: Withdraw some pool shares into a basket of currencies specified by ratio
    shares = 20
    withdrawal_ratio = {"X": 5.0, "Y": 7.0, "Z": 3.0}
    withdrawn_wallet = pool.withdraw_any(shares, withdrawal_ratio)
    print(
        f"\nWithdraw Any Asset Result: {shares}{withdrawal_ratio} Pool Shares -> {withdrawn_wallet}"
    )
    print("Infinity Pool Status:")
    print(pool.status())

    # SWAPS

    # Perform a swap from X to Y
    amount_in = 50.0
    amount_out = pool.swap("X", "Y", amount_in)
    print(f"\nSwap Result: {amount_in} X -> {amount_out} Y")
    print("Infinity Pool Status:")
    print(pool.status())

    # EQUAlIZE

    # Arbitrary input of tokens and shares, arbitrary output value ratio
    withdrawal_inputs = ({"X": 2.0, "Y": 0, "Z": 33.0}, 1.0)
    withdrawal_ratio = ({"X": 5.0, "Y": 7.0, "Z": 3.0}, 7.0)
    withdrawn_wallet = pool.equalize(withdrawal_inputs, withdrawal_ratio)
    print(
        f"\nWithdraw Inputs: {withdrawal_inputs} Ratio {withdrawal_ratio} Pool Shares"
        f" -> {withdrawn_wallet}"
    )
    print("Infinity Pool Status:")
    print(pool.status())


if __name__ == "__main__":
    main()
