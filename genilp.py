import pulp
import json
import logging
import csv
import argparse

# Do not allow importing this script from somewhere else
if __name__ != '__main__':
    logging.basicConfig(format='%(message)s')
    logging.error('Import forbidden! Exiting..')
    exit()

def sum_deals(my_deals, my_factors = None):
    if my_factors is None:
        my_factors = [1] * len(my_deals)
    if type(my_factors) != list:
        my_factors = [my_factors] * len(my_deals)
    is_first = True
    my_sum = ''
    for deal, factor in zip(my_deals, my_factors):
        if is_first:
            if factor != 1:
                my_sum += f'{factor} * deals[{deal.id}]'
            else:
                my_sum += f'deals[{deal.id}]'
            is_first = False
        else:
            if factor != 1:
                my_sum += f'\n  + {factor} * deals[{deal.id}]'
            else:
                my_sum += f'\n  + deals[{deal.id}]'
    return my_sum

def show_dict(items):
    for _, item in items.items():
        logging.debug(item)
        logging.debug('')

def show_list(items, title=None):
    if title is not None:
        logging.debug(title)

    for item in items:
        logging.debug(item)
        logging.debug('')

def show_all(loans, pools, constraints, buyers):
    show_dict(loans)

    show_dict(pools)

    show_dict(constraints)

    show_list(buyers)

loan_string = '''Loan {}
    Amount: {}
    FICO credit score: {}
    Debt-To-Income ratio: {}
    Is expensive: {}
    Is in California: {}
    Is paid by cashout: {}
    Is primary residence: {}'''

pool_string = '''Pool {}
    Is standard: {}
    Is single: {}
    Servicer: {}'''

buyer_string = '''Deal {}
    Pool: {}
    Loan: {}
    Price: {}'''

class Loan:

    def __init__(self, loan_id, amount, fico, dti, is_expensive, is_california, is_cashout, is_primary,
        occupancy, location, property_type, purpose):
        self.id = loan_id
        if int(amount) == amount:
            self.amount = int(amount)
        else:
            self.amount = amount
        self.fico = fico
        self.dti = dti
        self.is_expensive = is_expensive
        self.is_california = is_california
        self.is_cashout = is_cashout
        self.is_primary = is_primary

        self.occupancy = occupancy
        self.location = location
        self.property_type = property_type
        self.purpose = purpose

    def __str__(self):
        return loan_string.format(self.id, self.amount, self.fico, self.dti,
                self.is_expensive, self.is_california, self.is_cashout, self.is_primary)

class Pool:

    def __init__(self, pool_id, is_standard, is_single, servicer, agency):
        self.id = pool_id
        self.is_standard = is_standard
        self.is_single = is_single
        self.servicer = servicer
        self.agency = agency

    def __str__(self):
        return pool_string.format(self.id,
            self.is_standard, self.is_single, self.servicer)

class Deal:

    def __init__(self, buyer_id, pool_id, loan_id, price):
        self.id = buyer_id
        self.pool_id = pool_id
        self.loan_id = loan_id
        self.price = price

    def __str__(self):
        return buyer_string.format(self.id, self.pool_id, self.loan_id, self.price)

# MAIN PROGRAM START
#######################################################################

parser = argparse.ArgumentParser()
parser.add_argument('--verbose', '-v', action='count')
args = parser.parse_args()

log_levels = {
    None: logging.WARNING,
    1: logging.INFO,
    2: logging.DEBUG
}
if args.verbose is not None and args.verbose >= len(log_levels):
    args.verbose = len(log_levels)-1
logging.basicConfig(format='%(message)s', level=log_levels[args.verbose])

loans = {}
with open('data_processed/LoansFull.csv') as loans_file:
    loans_reader = csv.reader(loans_file)
    next(loans_reader) # consume the column names
    for loan_id_string, amount_string, fico_string, dti_string,\
            is_expensive_string, is_california_string,\
            is_cashout_string, is_primary_string,\
            occupancy, location, property_type, purpose in loans_reader:

        # parse the loan row
        loan_id = int(loan_id_string)
        amount = float(amount_string)
        fico = float(fico_string)
        dti = float(dti_string)
        is_expensive = int(is_expensive_string == '1')
        is_california = int(is_california_string == '1')
        is_cashout = int(is_cashout_string == '1')
        is_primary = int(is_primary_string == '1')

        loan = Loan(loan_id, amount, fico, dti,
            is_expensive, is_california, is_cashout, is_primary,
            occupancy, location, property_type, purpose)
        loans[loan_id] = loan

        assert type(loan.id) == int
        assert type(loan.amount) in [float, int]
        assert type(loan.fico) == float
        assert type(loan.dti) == float
        assert type(loan.is_expensive) == int, 'is_expensive should be an integer for easy multiplication and addition'
        assert type(loan.is_california) == int, 'is_california should be an integer for easy multiplication and addition'
        assert type(loan.is_cashout) == int, 'is_cashout should be an integer for easy multiplication and addition'
        assert type(loan.is_primary) == int, 'is_primary should be an integer for easy multiplication and addition'
        assert type(loan.occupancy) == str
        assert type(loan.location) == str
        assert type(loan.property_type) == str
        assert type(loan.purpose) == str

pools = {}
with open('data_processed/Pools.csv') as pools_file:
    pools_reader = csv.reader(pools_file)
    next(pools_reader) # consume the column names
    for pool_id_string, issuer_type, balance_type, agency, servicer in pools_reader:

        # parse the pool row
        pool_id = int(pool_id_string[5:])
        is_standard = (balance_type == 'Standard Balance')
        is_single = (issuer_type == 'Single-Issuer')

        pool = Pool(pool_id, is_standard, is_single, servicer, agency)
        pools[pool_id] = pool

        assert type(pool.id) == int
        assert type(pool.is_standard) == bool
        assert type(pool.is_single) == bool
        assert type(pool.servicer) == str
        assert type(pool.agency) == str

constraints = {}
with open('data/ConstraintsComparability.csv') as constraints_file:
    constraints_reader = csv.reader(constraints_file)
    for name, value_string in constraints_reader:
        value = float(value_string)
        constraints[name] = value if int(value) != value else int(value)

deals = {}
with open('data_processed/ChooseLoan.csv') as choose_pool_file:
    pool_loans_reader = csv.reader(choose_pool_file)
    next(pool_loans_reader) # consume the column names
    for i, (deal_id_string, pool_id_string, loan_id_string, price_string) in enumerate(pool_loans_reader):
        pool_id = int(pool_id_string[5:])
        deal_id = int(deal_id_string)
        deal = Deal(deal_id, pool_id, int(loan_id_string), float(price_string))
        deals[deal_id] = deal

        assert type(deal.id) == int
        assert type(deal.price) == float
        assert type(deal.pool_id) == int
        assert type(deal.loan_id) == int

assert type(loans) == dict, 'Loans should be in a dict'
assert type(pools) == dict, 'Pools should be in a dict'
assert type(constraints) == dict, 'Constraints should be in a dict'
assert type(deals) == dict, 'Deals should be in a dict'

# remove a couple deals to make the problem easier
take_every_deal = 1
for deal_id in deals:
    if deal_id % take_every_deal > 0:
        del deals[deal_id]

# remove infeasible deals, because the corresponding pool is a single issuer pool that cannot possibly reach its lower bound on the amount
used_pool_ids = set([deal.pool_id for _, deal in deals.items()])
for pool_id in list(pools):
    pool = pools[pool_id]
    if pool.is_single:
        pool_deals = [deal for _, deal in deals.items() if deal.pool_id == pool_id]
        loans_sum = sum(loans[deal.loan_id].amount for deal in pool_deals)
        if loans_sum < constraints['c2']:
            logging.debug(f'Single issuer pool {pool_id} cannot possibly satisfy its constraint; removing all deals involving this pool..')
            for pool_deal in pool_deals:
                del deals[pool_deal.id]

# remove unnecessary loans (may be needed if this is a reduced input)
used_loan_ids = set([deal.loan_id for _, deal in deals.items()])
for loan_id in list(loans):
    if loan_id not in used_loan_ids:
        del loans[loan_id]

# remove unnecessary pools (may be needed if this is a reduced input or some single issuer pools have been removed)
used_pool_ids = set([deal.pool_id for _, deal in deals.items()])
for pool_id in list(pools):
    if pool_id not in used_pool_ids:
        del pools[pool_id]

assert len(deals) > 0

deal_ids = [deal.id for _, deal in deals.items()]
variables = pulp.LpVariable.dicts('Deal', lowBound=0, upBound=1, indexs=deal_ids, cat=pulp.LpInteger)

single_pool_ids = [pool_id for pool_id in pools if pools[pool_id].is_single]
single_variables = pulp.LpVariable.dicts('SinglePool', lowBound=0, upBound=1, indexs=single_pool_ids, cat=pulp.LpInteger)

program = pulp.LpProblem('MortgagesProblem', pulp.LpMaximize)

# Objective function
program += pulp.lpSum([variables[deal.id] * deal.price for _, deal in deals.items()]), 'Total Selling Price'

# For each loan having at least two pools: One mutex constraint
for loan_id in loans:
    loan_deals = [deal for _, deal in deals.items() if deal.loan_id == loan_id]
    if len(loan_deals) >= 2:
        program += pulp.lpSum([variables[deal.id] for deal in loan_deals]) <= 1, f'Mutex constraint for loan {loan_id}'

# For each pool having at least one high balance loan: One standard balance constraint
# For each single issuer pool: One single issuer constraint plus as many helper constraints as this pool is allowed loans
for pool_id, pool in pools.items():
    pool_deals = [deal for _, deal in deals.items() if deal.pool_id == pool_id]
    high_balance_deals = [pool_deal for pool_deal in pool_deals if loans[pool_deal.loan_id].is_expensive]
    if pool.is_standard and high_balance_deals:
        lhs = pulp.lpSum([loans[high_balance_deal.loan_id].amount * variables[high_balance_deal.id] for high_balance_deal in high_balance_deals])
        rhs = pulp.lpSum([constraints['c1'] * loans[pool_deal.loan_id].amount * variables[pool_deal.id] for pool_deal in pool_deals])
        program += lhs <= rhs, f'Standard balance constraint for pool {pool_id}'
    if pool.is_single:
        pool_amounts = pulp.lpSum([loans[deal.loan_id].amount * variables[deal.id] for deal in pool_deals])
        single_inequation = pool_amounts >= constraints['c2'] * single_variables[pool_id], f'Single issuer constraint for pool {pool_id}'
        program +=  single_inequation
        for deal in pool_deals:
            single_helper_inequation = single_variables[pool_id] >= variables[deal.id], f'Pool {pool_id} is not empty if loan {deal.loan_id} is sold to it'
            program += single_helper_inequation

# 5 Pingora constraints
pingora_deals = [deal for _, deal in deals.items() if pools[deal.pool_id].servicer == 'Pingora']
sum_pingora_amounts = pulp.lpSum([loans[deal.loan_id].amount * variables[deal.id] for deal in pingora_deals])
c3_inequation = sum_pingora_amounts <= constraints['c3'], f'Upper bound on the total amount sold to Pingora'
program += c3_inequation

sum_pingora_expensive_amounts = pulp.lpSum([loans[deal.loan_id].is_expensive * loans[deal.loan_id].amount * variables[deal.id] for deal in pingora_deals])
c4_inequation = sum_pingora_expensive_amounts <= constraints['c4'] * sum_pingora_amounts, f'Upper bound on high balance loans sold to Pingora'
program += c4_inequation

sum_pingora_fico_amounts = pulp.lpSum([loans[deal.loan_id].fico * loans[deal.loan_id].amount * variables[deal.id] for deal in pingora_deals])
c5_inequation = sum_pingora_fico_amounts >= constraints['c5'] * sum_pingora_amounts, f'Lower bound on the amount-relative average FICO score of loans sold to Pingora'
program += c5_inequation

sum_pingora_dti_amounts = pulp.lpSum([loans[deal.loan_id].dti * loans[deal.loan_id].amount * variables[deal.id] for deal in pingora_deals])
c6_inequation = sum_pingora_dti_amounts <= constraints['c6'] * sum_pingora_amounts, f'Upper bound on the amount-relative average DTI of loans sold to Pingora'
program += c6_inequation

sum_pingora_californias = pulp.lpSum([loans[deal.loan_id].is_california * variables[deal.id] for deal in pingora_deals])
num_pingora_deals = pulp.lpSum([variables[deal.id] for deal in pingora_deals])
c7_inequation = sum_pingora_californias <= constraints['c7'] * num_pingora_deals, f'Upper bound on the number of loans issued to buy a residence in California and sold to Pingora'
program += c7_inequation

# 5 Two Harbors constraints
two_harbors_deals = [deal for _, deal in deals.items() if pools[deal.pool_id].servicer == 'Two Harbors']
two_harbors_amounts = pulp.lpSum([loans[deal.loan_id].amount * variables[deal.id] for deal in two_harbors_deals])
c8_inequation = two_harbors_amounts >= constraints['c8'], 'Lower bound on the total amount sold to Two Harbors'
program += c8_inequation

two_harbors_fico_amounts = pulp.lpSum([loans[deal.loan_id].fico * loans[deal.loan_id].amount * variables[deal.id] for deal in two_harbors_deals])
c9_inequation = two_harbors_fico_amounts >= constraints['c9'] * two_harbors_amounts, 'Lower bound on the amount-relative average FICO score of loans sold to Two Harbors'
program += c9_inequation

two_harbors_dti_amounts = pulp.lpSum([loans[deal.loan_id].dti * loans[deal.loan_id].amount * variables[deal.id] for deal in two_harbors_deals])
c10_inequation = two_harbors_dti_amounts <= constraints['c10'] * two_harbors_amounts, 'Upper bound on the amount-relative average DTI of loans sold to Two Harbors'
program += c10_inequation

num_two_harbors_deals = pulp.lpSum([variables[deal.id] for deal in two_harbors_deals])
two_harbors_cashouts = pulp.lpSum([loans[deal.loan_id].is_cashout * variables[deal.id] for deal in two_harbors_deals])
c11_inequation = two_harbors_cashouts <= constraints['c11'] * num_two_harbors_deals, 'Upper bound on the number of loans issued in cash and sold to Two Harbors'
program += c11_inequation

two_harbors_primaries = pulp.lpSum([loans[deal.loan_id].is_primary * variables[deal.id] for deal in two_harbors_deals])
c12_inequation = two_harbors_primaries >= constraints['c12'] * num_two_harbors_deals, 'Upper bound on the number of loans issued to finance a primary residence and sold to Two Harbors'
program += c12_inequation

# Special constraints for fairness between Fanny Mae and Freddy Mac
fannie_deals = [deal for _, deal in deals.items() if pools[deal.pool_id].agency == 'Fannie Mae']
freddie_deals = [deal for _, deal in deals.items() if pools[deal.pool_id].agency == 'Freddie Mac']
logging.debug(f'Have {len(deals)} deals in total')
logging.debug(f'Have {len(fannie_deals)} Fannie Mae deals')
logging.debug(f'Have {len(freddie_deals)} Freddie Mac deals')


with open('start.json') as start_file:
    start = json.load(start_file)

sum_fannies = pulp.lpSum([variables[deal.id] for deal in fannie_deals])
sum_freddies = pulp.lpSum([variables[deal.id] for deal in freddie_deals])

sum_califonia_fannies = pulp.lpSum([variables[deal.id] for deal in fannie_deals if loans[deal.loan_id].is_california])
sum_califonia_freddies = pulp.lpSum([variables[deal.id] for deal in freddie_deals if loans[deal.loan_id].is_california])

lower_california_fannie = start['c15']['CA'] * sum_fannies <= sum_califonia_fannies, 'Lower bound on number of Fannie Mae loans bound to a residence in CA'
upper_california_fannie = sum_califonia_fannies <= (start['c15']['CA'] + constraints['c15']) * sum_fannies, 'Upper bound on number of Fannie Mae loans bound to a residence in CA'
lower_california_freddie = start['c15']['CA'] * sum_freddies <= sum_califonia_freddies, 'Lower bound on number of Freddie Mac loans bound to a residence in CA'
upper_california_freddie = sum_califonia_freddies <= (start['c15']['CA'] + constraints['c15']) * sum_freddies, 'Upper bound on number of Freddie Mac loans bound to a residence in CA'

program += lower_california_fannie
program += upper_california_fannie
program += lower_california_freddie
program += upper_california_freddie

all_purposes = set([loan.purpose for _, loan in loans.items()])
for i, purpose in enumerate(all_purposes):
    sum_purpose_fannies = pulp.lpSum([variables[deal.id] for deal in fannie_deals if loans[deal.loan_id].purpose == purpose])
    sum_purpose_freddies = pulp.lpSum([variables[deal.id] for deal in freddie_deals if loans[deal.loan_id].purpose == purpose])
    lower_purpose_fannie = start['c17'][purpose] * sum_fannies <= sum_purpose_fannies, f'Lower bound on number of Fannie Mae loans given out as a {purpose.replace("/"," per ")}'
    upper_purpose_fannie = sum_purpose_fannies <= (start['c17'][purpose] + constraints['c17']) * sum_fannies, f'Upper bound on number of Fannie Mae loans given out as a {purpose.replace("/"," per ")}'
    lower_purpose_freddie = start['c17'][purpose] * sum_freddies <= sum_purpose_freddies, f'Lower bound on number of Freddie Mac loans given out as a {purpose.replace("/"," per ")}'
    upper_purpose_freddie = sum_purpose_freddies <= (start['c17'][purpose] + constraints['c17']) * sum_freddies, f'Upper bound on number of Freddie Mac loans given out as a {purpose.replace("/"," per ")}'

    program += lower_purpose_fannie
    program += upper_purpose_fannie
    program += lower_purpose_freddie
    program += upper_purpose_freddie

all_types = set([loan.property_type for _, loan in loans.items()])
for i, property_type in enumerate(all_types):
    sum_property_type_fannies = pulp.lpSum([variables[deal.id] for deal in fannie_deals if loans[deal.loan_id].property_type == property_type])
    sum_property_type_freddies = pulp.lpSum([variables[deal.id] for deal in freddie_deals if loans[deal.loan_id].property_type == property_type])
    lower_property_type_fannie = start['c18'][property_type] * sum_fannies <= sum_property_type_fannies, f'Lower bound on number of Fannie Mae loans bound to a residence of type {property_type.replace("/"," per ")}'
    upper_property_type_fannie = sum_property_type_fannies <= (start['c18'][property_type] + constraints['c18']) * sum_fannies, f'Upper bound on number of Fannie Mae loans bound to a residence of type {property_type.replace("/"," per ")}'
    lower_property_type_freddie = start['c18'][property_type] * sum_freddies <= sum_property_type_freddies, f'Lower bound on number of Freddie Mac loans bound to a residence of type {property_type.replace("/"," per ")}'
    upper_property_type_freddie = sum_property_type_freddies <= (start['c18'][property_type] + constraints['c18']) * sum_freddies, f'Upper bound on number of Freddie Mac loans bound to a residence of type {property_type.replace("/"," per ")}'

    program += lower_property_type_fannie
    program += upper_property_type_fannie
    program += lower_property_type_freddie
    program += upper_property_type_freddie

program.writeLP('MortgagesProblem.lp')
logging.info('Integer Linear Program written to MortgagesProblem.lp')
