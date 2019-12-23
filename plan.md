# Quick profit from mortgages

## Description of the high-level problem

I am a bank and there are individuals who want to purchase big houses. They want money from me and they promise that they will pay back this money and a little more over the long term. Individuals, that I deem trustworthy, become my customers and I buy their desired houses to lend to them.

But I don't want to keep taking money from the individuals over the long term, so I pay someone to do this for me. This someone buys a given house from me, because they have enough patience to receive the entire house price plus interests back to them over the long term. I pay them by selling the house at a slightly smaller amount than I would probably receive, if I were patient enough to wait all those years; but this slightly smaller amount is still greater than the original price of the house. This way I profit a little from the customer and the buyer.

There are many potential buyers. In the end, there will be buyers who will buy at least one house from me. Every one of those buyers wants their houses to satisfy certain conditions. The following properties of these houses may be relevant to a given buyer:
* What is the total cost of these houses?
* Is the total cost bounded from above by a certain threshold?
* Is the total cost bounded from below by a certain threshold?

* Which houses are classified as *expensive* houses?
* What is the weighted number of *expensive* houses? (An *expensive* house is weighted by the relative cost of the house in this set of houses.)


* What are the credit rates of the borrowers of these houses?
* What is the sum of weighted credit rates of the borrowers of these houses? (A credit rate is weighted by the relative cost of the house in this set of houses.)

* What are the debt-to-income ratios of the borrowers of these houses?
* What is the sum of weighted debt-to-income ratios of the borrowers of these houses? (A debt-to-income ratio is weighted by the relative cost of the house in this set of houses.)

* What is the relative number of houses *standing in California*?
* What is the relative number of houses having customers who have a pay-back contract of type *Cashout*?
* What is the relative number of houses that will be used by their borrowers as their *primary residence*?

## Optimization problem

I will write an optimization program, that receives as input:
* a set of houses
* each house has a cost
* each house is either *expensive* or not
* each house has a credit rate
* each house has a debt-to-income ratio
* each house either stands in *California* or not
* each house either is redeemed via *Cashout* or not
* each house is either used as a *primary residence* or not
* each house has a set of suggestions, where each suggestion consists of a buyer and a price, that this buyer is willing to pay for the house
* a buyer is either of type *Standard Balance Pool* or *High Balance Pool*
* a buyer is either of type *Single Issuer Pool* or *Multi Issuer Pool*
* a buyer is either of type *Retained* or *Pingora* or *Two Harbors*

My optimization program will output an allocation, which assigns to each house exactly one of its suggestions, such that all of the following is satisfied.

Every house is assigned a suggestion. Every suggestion has a buyer. In this way, every house is assigned a buyer. Every buyer buys a (possibly empty) set of houses. If a buyer buys at least one house, then this buyer's set of houses must satisfy some conditions depending on the categories of this buyer.

If the buyer is of type *Standard Balance Pool*, the following condition must be satisfied:
* The weighted number of *expensive* houses is bounded from above by threshold #1.

If the buyer is of type *Single Issuer Pool*, the following condition must be satisfied:
* The total cost is bounded from below by threshold #2.

If the buyer is of type *Pingora*, the following conditions must be satisfied:
* The total cost is bounded from above by threshold #3.
* The weighted number of *expensive* houses is bounded from above by threshold #4.
* The sum of weighted credit rates is bounded from below by threshold #5.
* The sum of weighted debt-to-income ratios is bounded from above by threshold #6.
* The relative number of houses *standing in California* is bounded from above by threshold #7.

If the buyer is of type *Two Harbors*, the following conditions must be satisfied:
* The total cost is bounded from below by threshold #8.
* The sum of weighted credit rates is bounded from below by threshold #9.
* The sum of weighted debt-to-income ratios is bounded from above by threshold #10.
* The relative number of houses *redeemed by Cashout* is bounded from above by threshold #11.
* The relative number of houses *used as primary residences* is bounded from below by threshold #12.

In this allocation, each house is sold to the price of its assigned suggestion. The sum of these prices is the total selling price. In addition to satisfying all above conditions, I want to maximize the total selling price of my allocation.
