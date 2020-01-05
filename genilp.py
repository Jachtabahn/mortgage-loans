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

    def __init__(self, pool_id, is_standard, is_single, servicer):
        self.id = pool_id
        self.is_standard = is_standard
        self.is_single = is_single
        self.servicer = servicer

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
    for pool_id_string, standard_string, single_string, servicer in pools_reader:

        # parse the pool row
        pool_id = int(pool_id_string[5:])
        is_standard = (standard_string == 'Standard Balance')
        is_single = (single_string == 'Single-Issuer')

        pool = Pool(pool_id, is_standard, is_single, servicer)
        pools[pool_id] = pool

        assert type(pool.id) == int
        assert type(pool.is_standard) == bool
        assert type(pool.is_single) == bool
        assert type(pool.servicer) == str

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
        if loans_sum < constraints["c2"]:
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

program = ''
program += f'// Declaration of {len(deals)} decision variables\n'
program += '{int} DealIds = {\n'
is_first = True
for deal in deals:
    if is_first:
        program += f'  {deal.id}'
        is_first = False
    else:
        program += f',\n  {deal.id}'
program += '};\n'
program += f'dvar int deals[DealIds] in 0..1;\n'
program += f'// <------------------------------------------------------- Declaration of {len(deals)} decision variables\n\n\n'

program += '// Objective function\n'
is_first = True
for deal in deals:
    if is_first:
        program += f'maximize {deal.price} * deals[{deal.id}]'
        is_first = False
    else:
        program += f'\n  + {deal.price} * deals[{deal.id}]'
program += f';\n'
program += '// <------------------------------------------------------- Objective function\n\n\n'

program += 'subject to {\n'

num_mutex_inequations = 0
program += '// Mutual exclusion inequations\n'
for loan_id in loans:
    loan_deals = [deal for deal in deals if deal.loan_id == loan_id]
    deal_ids = [loan_deal.id for loan_deal in loan_deals]

    if len(deal_ids) > 1:
        program += f'// Loan {loan_id} has {len(deal_ids)} pools in total\n'
        is_first = True
        for deal_id in deal_ids:
            if is_first:
                program += f'deals[{deal_id}]'
                is_first = False
                continue
            program += f' + deals[{deal_id}]'
        program +=' <= 1;'
        program +='\n\n'
        num_mutex_inequations += 1
program += '// <------------------------------------------------------- Mutual exclusion inequations\n\n'

num_standard_inequations = 0
num_single_disjunctions = 0
program += f'// Inequations for {len(pools)} pools \n'
for pool_id, pool in pools.items():
    pool_deals = [deal for deal in deals if deal.pool_id == pool_id]
    program += f'// Pool {pool_id}\n'
    if pool.is_standard:
        expensive_deals = [pool_deal for pool_deal in pool_deals if loans[pool_deal.loan_id].is_expensive]
        program += f'// has {len(pool_deals)} loans in total and {len(expensive_deals)} expensive ones\n'
        if expensive_deals:
            is_first = True
            for pool_deal in expensive_deals:
                loan = loans[pool_deal.loan_id]
                if is_first:
                    program += f'{loan.amount} * deals[{pool_deal.id}]'
                    is_first = False
                else:
                    program += f' + {loan.amount} * deals[{pool_deal.id}]'
            program += f' <= '
            is_first = True
            for pool_deal in pool_deals:
                loan = loans[pool_deal.loan_id]
                reduced_amount = constraints["c1"] * loan.amount
                if int(reduced_amount) == reduced_amount:
                    reduced_amount = int(reduced_amount)
                if is_first:
                    program += f'{reduced_amount} * deals[{pool_deal.id}]'
                    is_first = False
                else:
                    program += f' + {reduced_amount} * deals[{pool_deal.id}]'
            program += ';'
            num_standard_inequations += 1
    program += f'\n'
    if pool.is_single:
        program += f'// is a single issuer pool\n'
        is_first = True
        for pool_deal in pool_deals:
            loan = loans[pool_deal.loan_id]
            if is_first:
                program += f'deals[{pool_deal.id}]'
                is_first = False
            else:
                program += f' + deals[{pool_deal.id}]'
        program += f' == 0\n  || '

        is_first = True
        for pool_deal in pool_deals:
            loan = loans[pool_deal.loan_id]
            if is_first:
                program += f'{loan.amount} * deals[{pool_deal.id}]'
                is_first = False
            else:
                program += f' + {loan.amount} * deals[{pool_deal.id}]'
        program += f' >= {constraints["c2"]};'
        num_single_disjunctions += 1
    program += f'\n\n'
program += f'// <------------------------------------------------------- Inequations for {len(pools)} pools\n\n\n'

program += '// 5 Pingora inequations\n'
pingora_deals = [deal for deal in deals if pools[deal.pool_id].servicer == 'Pingora']
program += f'// There are {len(deals)} deals in total\n'
program += f'// Of those, {len(pingora_deals)} are Pingora deals\n'

program += '// Amount inequation\n'
pingora_amounts = [loans[deal.loan_id].amount for deal in pingora_deals]
program += sum_deals(pingora_deals, pingora_amounts)
program += f'\n  <= {constraints["c3"]}'
program += ';\n\n'

program += '// High balance inequation\n'
expensive_deals = [deal for deal in pingora_deals if loans[deal.loan_id].is_expensive]
expensive_amounts = [loans[deal.loan_id].amount for deal in expensive_deals]
program += sum_deals(expensive_deals, expensive_amounts)
program += '\n  <= '
expensive_c4_amounts = [constraints["c4"] * loans[deal.loan_id].amount for deal in pingora_deals]
program += sum_deals(pingora_deals, expensive_c4_amounts)
program += ';\n\n'

program += '// FICO inequation\n'
pingora_fico_amounts = [loans[deal.loan_id].fico * loans[deal.loan_id].amount for deal in pingora_deals]
program += sum_deals(pingora_deals, pingora_fico_amounts)
program += '\n  >= '
pingora_c5_amounts = [constraints["c5"] * loans[deal.loan_id].amount for deal in pingora_deals]
program += sum_deals(pingora_deals, pingora_c5_amounts)
program += ';\n\n'

program += '// DTI inequation\n'
pingora_dti_amounts = [loans[deal.loan_id].dti * loans[deal.loan_id].amount for deal in pingora_deals]
program += sum_deals(pingora_deals, pingora_dti_amounts)
program += '\n  <= '
pingora_c6_amounts = [constraints["c6"] * loans[deal.loan_id].amount for deal in pingora_deals]
program += sum_deals(pingora_deals, pingora_c6_amounts)
program += ';\n\n'

program += '// California inequation\n'
california_deals = [california_deal for california_deal in pingora_deals if loans[california_deal.loan_id].is_california]
program += f'// There are {len(california_deals)} deals involving houses in California \n'
program += sum_deals(california_deals)
program += f'\n  <= '
program += sum_deals(pingora_deals, constraints["c7"])
program += ';\n\n'

program += '// <------------------------------------------------------- 5 Pingora inequations\n\n\n'

program += '// 5 Two Harbors inequations\n'
two_harbors_deals = [deal for deal in deals if pools[deal.pool_id].servicer == 'Two Harbors']
program += f'// There are {len(deals)} deals in total\n'
program += f'// Of those, {len(two_harbors_deals)} are Two Harbors deals\n'

program += '// Amount inequation\n'
two_harbors_amounts = [loans[deal.loan_id].amount for deal in two_harbors_deals]
program += sum_deals(two_harbors_deals, two_harbors_amounts)
program += f'\n  >= {constraints["c8"]}'
program += ';\n\n'

program += '// FICO inequation\n'
two_harbors_fico_amounts = [loans[deal.loan_id].fico * loans[deal.loan_id].amount for deal in two_harbors_deals]
program += sum_deals(two_harbors_deals, two_harbors_fico_amounts)
program += '\n  >= '
two_harbors_c9_amounts = [constraints["c9"] * loans[deal.loan_id].amount for deal in two_harbors_deals]
program += sum_deals(two_harbors_deals, two_harbors_c9_amounts)
program += ';\n\n'

program += '// DTI inequation\n'
two_harbors_dti_amounts = [loans[deal.loan_id].dti * loans[deal.loan_id].amount for deal in two_harbors_deals]
program += sum_deals(two_harbors_deals, two_harbors_dti_amounts)
program += '\n  <= '
two_harbors_c10_amounts = [constraints["c10"] * loans[deal.loan_id].amount for deal in two_harbors_deals]
program += sum_deals(two_harbors_deals, two_harbors_c10_amounts)
program += ';\n\n'

program += '// Cashout inequation\n'
cashout_deals = [deal for deal in two_harbors_deals if loans[deal.loan_id].is_cashout]
program += f'// There are {len(cashout_deals)} deals with loans that have been given out in cash \n'
program += sum_deals(cashout_deals)
program += f'\n  <= '
program += sum_deals(two_harbors_deals, constraints["c11"])
program += ';\n\n'

program += '// Primary residence inequation\n'
primary_deals = [deal for deal in two_harbors_deals if loans[deal.loan_id].is_primary]
program += f'// There are {len(primary_deals)} deals involving houses used as a primary residence \n'
program += sum_deals(primary_deals)
program += f'\n  >= '
program += sum_deals(two_harbors_deals, constraints["c12"])
program += ';\n\n'

program += '// <------------------------------------------------------- 5 Two Harbors inequations\n\n\n'

program += '}\n'

print(program)

logging.debug('')
logging.debug('----------------------------- SUMMARY -----------------------------')
logging.debug(f'Number of loans: {len(loans)}')
logging.debug(f'Number of pools: {len(pools)}')
logging.debug(f'Number of deals: {len(deals)}')
logging.debug('-----------------------------------------')

logging.debug(f'Number of Mutex inequations: {num_mutex_inequations}')
logging.debug(f'Number of Standard Balance inequations: {num_standard_inequations}')
logging.debug(f'Number of Single Issuer disjunctions: {num_single_disjunctions}')
logging.debug(f'Number of Pingora inequations: 5')
logging.debug(f'Number of Two Harbors inequations: 5')
logging.debug('-----------------------------------------')

total = num_mutex_inequations + num_standard_inequations + num_single_disjunctions + 5 + 5
logging.debug(f'Total number of inequations or disjunctions: {total}')
