**BSIP:** TBD
**Title:** Infinity Pool Smart Contract
**Authors:** litepresence finitestate@tutamail.com
**Status:** Draft
**Type:** Protocol
**Created:** 2023-12-23
**Discussion:** TBD
**Worker:** TBD

# Abstract
This BSIP proposes the addition of an "Infinity Pool" smart contract to the core cpp codebase of the BitShares blockchain. The Infinity Pool is a dynamic liquidity pool that supports an infinite number of tokens, allowing users to create pools with any combination of tokens they wish to support. The smart contract is based on the provided Python reference implementation, which is a non-custodial portfolio manager, liquidity provider, and price sensor.

# Motivation
The current liquidity pool model in BitShares has limitations in terms of the number of supported tokens and flexibility in creating custom pools. The proposed Infinity Pool smart contract addresses these limitations by providing a generic solution that allows users to create pools with any combination of tokens.

# Rationale
The Infinity Pool smart contract is based on the whitepaper by Fernando Martinelli and Nikolai Mushegian, dated 2019-09-19. It introduces the concept of a dynamic liquidity pool with the ability to support an infinite number of tokens. The contract handles deposits, withdrawals, swaps, and equalization operations to maintain a constant value function.

# Specifications
The proposed smart contract is based on the provided Python reference implementation, which includes the following key features:

- Initialization: Users can initialize the pool by depositing an initial amount of each token or a single token.
- Deposits: Users can deposit any combination of tokens into the pool, receiving pool shares in return.
- Withdrawals: Users can withdraw tokens from the pool by redeeming pool shares.
- Swaps: Users can perform token swaps within the pool, adjusting token balances accordingly.
- Equalization: Users can equalize their portfolio by the pool adjusting token balances to match a requested output ratio.

# Discussion
The proposed Infinity Pool smart contract introduces a flexible and extensible liquidity pool model to the BitShares blockchain. Community feedback and discussion are encouraged to refine and improve the specifications of the smart contract.

# Summary for Shareholders
The addition of the Infinity Pool smart contract enhances the liquidity provision capabilities of the BitShares blockchain, allowing users to create diverse and customizable pools. This contributes to the overall flexibility and competitiveness of the BitShares decentralized exchange.

# Copyright
This BSIP and the associated smart contract are provided under WTFPL terms.

# See Also
- Whitepaper by Fernando Martinelli and Nikolai Mushegian: [pool.fi/whitepaper.pdf]
- Python reference implementation: [link to the Python code]
