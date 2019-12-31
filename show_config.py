import argparse
import numpy as np
import itertools
import logging
import csv

# Do not allow importing this script from somewhere else
if __name__ != '__main__':
    logging.basicConfig(format='%(message)s')
    logging.error('Import forbidden! Exiting..')
    exit()

LOWER_BOUND = -1
UPPER_BOUND = 1
constraint_directions = {
    'c1': UPPER_BOUND,
    'c2': LOWER_BOUND,
    'c3': UPPER_BOUND,
    'c4': UPPER_BOUND,
    'c5': LOWER_BOUND,
    'c6': UPPER_BOUND,
    'c7': UPPER_BOUND,
    'c8': LOWER_BOUND,
    'c9': LOWER_BOUND,
    'c10': UPPER_BOUND,
    'c11': UPPER_BOUND,
    'c12': LOWER_BOUND
}

def check_constraints(pool, subset_loans):
    subset_size = len(subset_loans)

    amounts_sum = sum([loan.amount for loan in subset_loans])

    weights = [loan.amount/amounts_sum for loan in subset_loans]

    normalized_ficos = [loan.fico * weight for loan, weight in zip(subset_loans, weights)]
    normal_fico = sum(normalized_ficos)

    normalized_dtis = [loan.dti * weight for loan, weight in zip(subset_loans, weights)]
    normal_dti = sum(normalized_dtis)

    normalized_expenses = [loan.is_expensive * weight for loan, weight in zip(subset_loans, weights)]
    normal_expense = sum(normalized_expenses)

    averaged_californias = [loan.is_california / subset_size for loan in subset_loans]
    average_california = sum(averaged_californias)

    averaged_cashouts = [loan.is_cashout / subset_size for loan in subset_loans]
    average_cashout = sum(averaged_cashouts)

    averaged_primaries = [loan.is_primary / subset_size for loan in subset_loans]
    average_primary = sum(averaged_primaries)

    logging.debug(f'Sum of amounts: {amounts_sum}\n')

    show_list(weights, 'Weights:')

    show_list(normalized_ficos, 'Normalized FICOs:')
    logging.debug(f'Normal FICO: {normal_fico}\n')

    show_list(normalized_dtis, 'Normalized DTIs:')
    logging.debug(f'Normal DTI: {normal_dti}\n')

    show_list(normalized_expenses, 'Normalized expenses:')
    logging.debug(f'Normal expense: {normal_expense}\n')

    show_list(averaged_californias, 'Averaged californias:')
    logging.debug(f'Average california: {average_california}\n')

    show_list(averaged_cashouts, 'Averaged cashouts:')
    logging.debug(f'Average cashout: {average_cashout}\n')

    show_list(averaged_primaries, 'Averaged primaries:')
    logging.debug(f'Average primary: {average_primary}\n')

    ok = True

    logging.debug(f'OK: {ok}')

    return ok

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

buyer_string = '''Buyer {}
    Pool: {}
    Loan: {}
    Price: {}'''

class Loan:

    def __init__(self, loan_id, amount, fico, dti, is_expensive, is_california, is_cashout, is_primary):
        self.id = loan_id
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

class Buyer:

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
# parser.add_argument('--network-name', '-g', default=None)
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
with open('processed_small/Loans.csv') as loans_file:
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
        assert type(loan.amount) == float
        assert type(loan.fico) == float
        assert type(loan.dti) == float
        assert type(loan.is_expensive) == int, 'is_expensive should be an integer for easy multiplication and addition'
        assert type(loan.is_california) == int, 'is_california should be an integer for easy multiplication and addition'
        assert type(loan.is_cashout) == int, 'is_cashout should be an integer for easy multiplication and addition'
        assert type(loan.is_primary) == int, 'is_primary should be an integer for easy multiplication and addition'

pools = {}
with open('processed_small/Pools.csv') as pools_file:
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
with open('processed_small/Constraints.csv') as constraints_file:
    constraints_reader = csv.reader(constraints_file)
    for name, value_string in constraints_reader:
        value = float(value_string)
        constraints[name] = value

buyers = []
with open('processed_small/ChooseLoan.csv') as choose_pool_file:
    pool_loans_reader = csv.reader(choose_pool_file)
    next(pool_loans_reader) # consume the column names
    for pool_id_string, loan_id_string, price_string in pool_loans_reader:
        pool_id = int(pool_id_string[5:])
        buyer = Buyer(len(buyers), pool_id, int(loan_id_string), float(price_string))
        buyers.append(buyer)

        assert type(buyer.id) == int
        assert type(buyer.price) == float
        assert type(buyer.pool_id) == int
        assert type(buyer.loan_id) == int

assert type(loans) == dict, 'Loans should be in a dict'
assert type(pools) == dict, 'Pools should be in a dict'
assert type(constraints) == dict, 'Constraints should be in a dict'
assert type(buyers) == list, 'Buyers should be in a list'

# remove unnecessary loans (may be needed if this is a reduced input)
used_loan_ids = set([buyer.loan_id for buyer in buyers])
for loan_id in list(loans):
    if loan_id not in used_loan_ids:
        del loans[loan_id]

used_pool_ids = set([buyer.pool_id for buyer in buyers])
for pool_id in list(pools):
    if pool_id not in used_pool_ids:
        del pools[pool_id]

max_pool_id = max([pool_id for pool_id in pools])
PINGORA = max_pool_id + 1
TWO_HARBORS = max_pool_id + 2
ECONOMIC_VALUE = max_pool_id + 3

config_ids = sum([[(pool_id, 'c1'), (pool_id, 'c2')] for pool_id in pools], []) \
    + [(ECONOMIC_VALUE, '')]
num_features = len(config_ids)
config_values = np.zeros(shape=num_features)
config_normalizers = np.ones(shape=num_features)

for i, config_id in zip(range(num_features), config_ids):
    constraint_name = config_id[1]
    if constraint_name == 'c1':
        config_normalizers[i] = 0

logging.debug('Initial configuration vectors:')
logging.debug(config_values)
logging.debug(config_normalizers)
logging.debug('--------------------------------------------------------\n')

taken_buyers = []
for a in range(len(buyers)):
    # Choose some buyer
    fixed_buyer = None
    for buyer in buyers:
        if buyer in taken_buyers: continue
        fixed_buyer = buyer
        break
    if fixed_buyer  is None:
        logging.error('All buyers taken!')
        exit()
    taken_buyers.append(fixed_buyer)

    # Extract pool id and loan from that buyer
    fixed_pool_id = fixed_buyer.pool_id
    fixed_loan_id = fixed_buyer.loan_id
    fixed_loan = loans[fixed_loan_id]

    # Construct this buyer's translation vectors
    move_values = np.zeros(shape=num_features)
    move_normalizers = np.zeros(shape=num_features)

    index_c1 = config_ids.index((fixed_pool_id, 'c1'))
    move_values[index_c1] = fixed_loan.is_expensive
    move_normalizers[index_c1] = fixed_loan.amount

    index_c2 = index_c1 + 1
    move_values[index_c2] = fixed_loan.amount

    index_price = len(config_ids) - 1
    move_values[index_price] = fixed_buyer.price

    logging.debug(f'Translation vectors of iteration {a}:')
    logging.debug(fixed_buyer)
    logging.debug(move_values)
    logging.debug(move_normalizers)
    logging.debug('--------------------------------------------------------\n')

    # Apply this buyer's translation vectors to the total configuration
    config_values += move_values
    config_normalizers += move_normalizers

    logging.debug('Configuration vectors:')
    logging.debug(config_values)
    logging.debug(config_normalizers)
    logging.debug('--------------------------------------------------------\n')
