import pulp
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

    def __init__(self, loan_id, amount, fico, dti, is_expensive, is_california, is_cashout, is_primary):
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
with open('data_processed/Loans.csv') as loans_file:
    loans_reader = csv.reader(loans_file)
    next(loans_reader) # consume the column names
    for loan_id_string, amount_string, fico_string, dti_string,\
            is_expensive_string, is_california_string,\
            is_cashout_string, is_primary_string in loans_reader:

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
            is_expensive, is_california, is_cashout, is_primary)
        loans[loan_id] = loan

        assert type(loan.id) == int
        assert type(loan.amount) in [float, int]
        assert type(loan.fico) == float
        assert type(loan.dti) == float
        assert type(loan.is_expensive) == int, 'is_expensive should be an integer for easy multiplication and addition'
        assert type(loan.is_california) == int, 'is_california should be an integer for easy multiplication and addition'
        assert type(loan.is_cashout) == int, 'is_cashout should be an integer for easy multiplication and addition'
        assert type(loan.is_primary) == int, 'is_primary should be an integer for easy multiplication and addition'

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
with open('data_processed/Constraints.csv') as constraints_file:
    constraints_reader = csv.reader(constraints_file)
    for name, value_string in constraints_reader:
        value = float(value_string)
        constraints[name] = value if int(value) != value else int(value)

deals = []
with open('data_processed/ChooseLoan.csv') as choose_pool_file:
    pool_loans_reader = csv.reader(choose_pool_file)
    next(pool_loans_reader) # consume the column names
    for i, (pool_id_string, loan_id_string, price_string) in enumerate(pool_loans_reader):
        pool_id = int(pool_id_string[5:])
        deal = Deal(2 + len(deals), pool_id, int(loan_id_string), float(price_string))
        deals.append(deal)

        assert type(deal.id) == int
        assert type(deal.price) == float
        assert type(deal.pool_id) == int
        assert type(deal.loan_id) == int

assert type(loans) == dict, 'Loans should be in a dict'
assert type(pools) == dict, 'Pools should be in a dict'
assert type(constraints) == dict, 'Constraints should be in a dict'
assert type(deals) == list, 'Deals should be in a list'

# remove a couple deals to make the problem easier
take_every_deal = 1
for i in range(len(deals))[::-1]:
    if i % take_every_deal > 0:
        del deals[i]

# remove infeasible deals, because the corresponding pool is a single issuer pool that cannot possibly reach its lower bound on the amount
used_pool_ids = set([deal.pool_id for deal in deals])
for pool_id in list(pools):
    pool = pools[pool_id]
    if pool.is_single:
        pool_deals = [deal for deal in deals if deal.pool_id == pool_id]
        loans_sum = sum(loans[deal.loan_id].amount for deal in pool_deals)
        if loans_sum < constraints['c2']:
            logging.debug(f'Single issuer pool {pool_id} cannot possibly satisfy its constraint; removing all deals involving this pool..')
            for pool_deal in pool_deals:
                deals.remove(pool_deal)

# remove unnecessary loans (may be needed if this is a reduced input)
used_loan_ids = set([deal.loan_id for deal in deals])
for loan_id in list(loans):
    if loan_id not in used_loan_ids:
        del loans[loan_id]

# remove unnecessary pools (may be needed if this is a reduced input or some single issuer pools have been removed)
used_pool_ids = set([deal.pool_id for deal in deals])
for pool_id in list(pools):
    if pool_id not in used_pool_ids:
        del pools[pool_id]

assert len(deals) > 0

deal_ids = [deal.id for deal in deals]
vars = pulp.LpVariable.dicts('Deal', lowBound=0, upBound=1, indexs=deal_ids, cat=pulp.LpInteger)

single_pool_ids = [pool_id for pool_id in pools if pools[pool_id].is_single]
single_vars = pulp.LpVariable.dicts('SinglePool', lowBound=0, upBound=1, indexs=single_pool_ids, cat=pulp.LpInteger)

# Creates the 'program' variable to contain the problem data
program = pulp.LpProblem('MortgagesProblem', pulp.LpMaximize)

# Creates the objective function
program += pulp.lpSum([vars[deal.id] * deal.price for deal in deals]), 'Total Selling Price'

for loan_id in loans:
    loan_deals = [deal for deal in deals if deal.loan_id == loan_id]
    if len(loan_deals) > 1:
        program += pulp.lpSum([vars[deal.id] for deal in loan_deals]) <= 1, f'Mutex constraint for loan {loan_id}'

for pool_id, pool in pools.items():
    pool_deals = [deal for deal in deals if deal.pool_id == pool_id]
    high_balance_deals = [pool_deal for pool_deal in pool_deals if loans[pool_deal.loan_id].is_expensive]
    if pool.is_standard and high_balance_deals:
        lhs = pulp.lpSum([loans[high_balance_deal.loan_id].amount * vars[high_balance_deal.id] for high_balance_deal in high_balance_deals])
        rhs = pulp.lpSum([constraints['c1'] * loans[pool_deal.loan_id].amount * vars[pool_deal.id] for pool_deal in pool_deals])
        program += lhs <= rhs, f'Standard balance constraint for pool {pool_id}'
    if pool.is_single:
        pool_amounts = pulp.lpSum([loans[deal.loan_id].amount * vars[deal.id] for deal in pool_deals])
        single_inequation = pool_amounts >= constraints['c2'] * single_vars[pool_id], f'Single issuer constraint for pool {pool_id}'
        program +=  single_inequation
        for deal in pool_deals:
            single_helper_inequation = single_vars[pool_id] >= vars[deal.id], f'Pool {pool_id} is not empty if loan {deal.loan_id} is sold to it'
            program += single_helper_inequation

pingora_deals = [deal for deal in deals if pools[deal.pool_id].servicer == 'Pingora']
sum_pingora_amounts = pulp.lpSum([loans[deal.loan_id].amount * vars[deal.id] for deal in pingora_deals])
c3_inequation = sum_pingora_amounts <= constraints['c3'], f'Upper bound on the total amount sold to Pingora'
program += c3_inequation

sum_pingora_expensive_amounts = pulp.lpSum([loans[deal.loan_id].is_expensive * loans[deal.loan_id].amount * vars[deal.id] for deal in pingora_deals])
c4_inequation = sum_pingora_expensive_amounts <= constraints['c4'] * sum_pingora_amounts, f'Upper bound on high balance loans sold to Pingora'
program += c4_inequation

sum_pingora_fico_amounts = pulp.lpSum([loans[deal.loan_id].fico * loans[deal.loan_id].amount * vars[deal.id] for deal in pingora_deals])
c5_inequation = sum_pingora_fico_amounts >= constraints['c5'] * sum_pingora_amounts, f'Lower bound on the amount-relative average FICO score of loans sold to Pingora'
program += c5_inequation

sum_pingora_dti_amounts = pulp.lpSum([loans[deal.loan_id].dti * loans[deal.loan_id].amount * vars[deal.id] for deal in pingora_deals])
c6_inequation = sum_pingora_dti_amounts <= constraints['c6'] * sum_pingora_amounts, f'Upper bound on the amount-relative average DTI of loans sold to Pingora'
program += c6_inequation

sum_pingora_californias = pulp.lpSum([loans[deal.loan_id].is_california * vars[deal.id] for deal in pingora_deals])
num_pingora_deals = pulp.lpSum([vars[deal.id] for deal in pingora_deals])
c7_inequation = sum_pingora_californias <= constraints['c7'] * num_pingora_deals, f'Upper bound on the number of loans issued to buy a residence in California and sold to Pingora'
program += c7_inequation


two_harbors_deals = [deal for deal in deals if pools[deal.pool_id].servicer == 'Two Harbors']
two_harbors_amounts = pulp.lpSum([loans[deal.loan_id].amount * vars[deal.id] for deal in two_harbors_deals])
c8_inequation = two_harbors_amounts >= constraints['c8'], 'Lower bound on the total amount sold to Two Harbors'
program += c8_inequation

two_harbors_fico_amounts = pulp.lpSum([loans[deal.loan_id].fico * loans[deal.loan_id].amount * vars[deal.id] for deal in two_harbors_deals])
c9_inequation = two_harbors_fico_amounts >= constraints['c9'] * two_harbors_amounts, 'Lower bound on the amount-relative average FICO score of loans sold to Two Harbors'
program += c9_inequation

two_harbors_dti_amounts = pulp.lpSum([loans[deal.loan_id].dti * loans[deal.loan_id].amount * vars[deal.id] for deal in two_harbors_deals])
c10_inequation = two_harbors_dti_amounts <= constraints['c10'] * two_harbors_amounts, 'Upper bound on the amount-relative average DTI of loans sold to Two Harbors'
program += c10_inequation

num_two_harbors_deals = pulp.lpSum([vars[deal.id] for deal in two_harbors_deals])
two_harbors_cashouts = pulp.lpSum([loans[deal.loan_id].is_cashout * vars[deal.id] for deal in two_harbors_deals])
c11_inequation = two_harbors_cashouts <= constraints['c11'] * num_two_harbors_deals, 'Upper bound on the number of loans issued in cash and sold to Two Harbors'
program += c11_inequation

two_harbors_primaries = pulp.lpSum([loans[deal.loan_id].is_primary * vars[deal.id] for deal in two_harbors_deals])
c12_inequation = two_harbors_primaries >= constraints['c12'] * num_two_harbors_deals, 'Upper bound on the number of loans issued to finance a primary residence and sold to Two Harbors'
program += c12_inequation

program.writeLP('MortgagesProblem.lp')

my_solver = pulp.solvers.CPLEX_CMD(path='/opt/ibm/ILOG/CPLEX_Studio129/cplex/bin/x86-64_linux/cplex')
program.solve(solver=my_solver)
logging.debug(f'Solver status: {pulp.LpStatus[program.status]}')
logging.debug(f'Objective: {pulp.value(program.objective)}')
with open('MortgagesProblem.sol', 'w') as solution_file:
    csvwriter = csv.writer(solution_file)
    csvwriter.writerow(['DealId', 'Take'])
    for deal_id, variable in vars.items():
        if variable.varValue is None: continue
        csvwriter.writerow([deal_id, int(variable.varValue)])

    for pool_id, variable in single_vars.items():
        if variable.varValue is None: continue
        csvwriter.writerow([f'pool_{pool_id}', int(variable.varValue)])
