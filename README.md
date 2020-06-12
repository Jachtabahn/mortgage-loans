# Mortgage Pooling Optimization

There are people who want to buy a house. But they don't have enough money, so they ask a bank to buy a house for them and pay it off to the bank via small payments until the full price plus something extra is paid off.

Now we are the bank. We don't want to deal with those small payments ourselves. We take note of which houses people want to buy and buy those houses. But then we immediately sell them again to government entities. These entities take care of the people and their regular small payments. We make profit almost immediately.

Now, the thing is that we can only sell *whole sets of houses* to those government entities, because they won't buy individual houses. But now, not all of these sets are feasible, because some government entity might not want to buy a certain set of houses, where the people that will have to pay them off have a low average [FICO score](https://www.bankrate.com/finance/credit/what-is-a-fico-score.aspx).

So, we need to balance all the houses that we have bought into appropriate sets of houses such that the relevant government entities will want to buy them and will want to buy them for a good price. Because, of course, in the end we want to maximize our profit in this business.

The problem boils down to this: Assign a house (mortgage loan) to a government entity, such that the set of all houses belonging to a specific government entity satisfies a [sequence of specific conditions](https://github.com/Jachtabahn/mortgage-loans/blob/construct-ilp-with-pulp/Constraints.pdf).

The code in this repository reduces the problem to an [integer linear program](https://github.com/Jachtabahn/mortgage-loans/blob/construct-ilp-with-pulp/genilp.py).

This integer linear program can be solved in a few minutes with [CPLEX](https://www.ibm.com/analytics/cplex-optimizer), but not with [COIN OR](https://www.coin-or.org/).

This code was submitted to a [TopCoder](https://www.topcoder.com/) competition, but it didn't win the main prize.
