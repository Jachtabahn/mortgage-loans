import logging
import csv
import argparse

# Do not allow importing this script from somewhere else
if __name__ != '__main__':
    logging.basicConfig(format='%(message)s')
    logging.error('Import forbidden! Exiting..')
    exit()

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
        constraints[name] = value

deals = []
take_every_line = 1
with open('data_processed/ChooseLoan.csv') as choose_pool_file:
    pool_loans_reader = csv.reader(choose_pool_file)
    next(pool_loans_reader) # consume the column names
    for i, (pool_id_string, loan_id_string, price_string) in enumerate(pool_loans_reader):
        if i % take_every_line > 0: continue
        pool_id = int(pool_id_string[5:])
        buyer = Deal(len(deals), pool_id, int(loan_id_string), float(price_string))
        deals.append(buyer)

        assert type(buyer.id) == int
        assert type(buyer.price) == float
        assert type(buyer.pool_id) == int
        assert type(buyer.loan_id) == int

assert type(loans) == dict, 'Loans should be in a dict'
assert type(pools) == dict, 'Pools should be in a dict'
assert type(constraints) == dict, 'Constraints should be in a dict'
assert type(deals) == list, 'Deals should be in a list'

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
used_loan_ids = set([buyer.loan_id for buyer in deals])
for loan_id in list(loans):
    if loan_id not in used_loan_ids:
        del loans[loan_id]

used_pool_ids = set([buyer.pool_id for buyer in deals])
for pool_id in list(pools):
    if pool_id not in used_pool_ids:
        del pools[pool_id]

assert len(deals) > 0

decisions = None
with open('allocation1.sol') as file:
    decisions = file.read().split()
assert decisions is not None

deal_ids = [i for i in range(len(decisions)) if decisions[i] == '1']
logging.debug(f'I have {len(decisions)} decisions')
logging.debug(f'I have sold {len(deal_ids)} / {len(loans)} loans')

pool_ids = set([deals[deal_id].pool_id for deal_id in deal_ids])
logging.debug(f'I have sold to {len(pool_ids)} / {len(pools)} pools')

with open('solution/without-servicers.csv', 'w') as file:
    solution_csv = csv.writer(file)
    solution_csv.writerow(['Loan', 'Pool', 'Servicer'])
    for deal_id in deal_ids:
        deal = deals[deal_id]
        pool = pools[deal.pool_id]
        solution_csv.writerow([deal.loan_id, 'pool_' + str(deal.pool_id), pool.servicer])
