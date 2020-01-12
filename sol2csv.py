import logging
import sys
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
with open('data_processed/Constraints.csv') as constraints_file:
    constraints_reader = csv.reader(constraints_file)
    for name, value_string in constraints_reader:
        value = float(value_string)
        constraints[name] = value

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

assert len(deals) > 0

taken_deal_ids = []
next(sys.stdin) # skip the csv heading
for line in sys.stdin:
    stripped = line.strip()
    taken_deal_id = int(stripped)
    taken_deal_ids.append(taken_deal_id)
logging.debug('I have sold {:,} / {:,} loans'.format(len(taken_deal_ids), len(loans)))
assert len(taken_deal_ids) > 0

pool_ids = set([deals[deal_id].pool_id for deal_id in taken_deal_ids])
logging.debug(f'I have sold to {len(pool_ids)} / {len(pools)} different pools')

solution_csv = csv.writer(sys.stdout)
solution_csv.writerow(['Loan', 'Pool', 'Servicer'])
for deal_id in taken_deal_ids:
    deal = deals[deal_id]
    pool = pools[deal.pool_id]
    solution_csv.writerow([deal.loan_id, 'pool_' + str(deal.pool_id), pool.servicer])

taken_deals = [deals[deal_id] for deal_id in taken_deal_ids]

taken_fannie_deals = [taken_fannie_deal for taken_fannie_deal in taken_deals if pools[taken_fannie_deal.pool_id].agency == 'Fannie Mae']
fannie_total_amount = sum(loans[deal.loan_id].amount for deal in taken_fannie_deals)
fannie_loans_weights = [(loans[deal.loan_id], loans[deal.loan_id].amount / fannie_total_amount) for deal in taken_fannie_deals]

taken_freddie_deals = [taken_freddie_deal for taken_freddie_deal in taken_deals if pools[taken_freddie_deal.pool_id].agency == 'Freddie Mac']
freddie_total_amount = sum(loans[deal.loan_id].amount for deal in taken_freddie_deals)
freddie_loans_weights = [(loans[deal.loan_id], loans[deal.loan_id].amount / freddie_total_amount) for deal in taken_freddie_deals]
logging.debug('----------------------------------------------------------------------------------------------------------------------')
logging.debug('Total number of deals: {:,}'.format(len(deals)))
logging.debug('Number of loans sold to a Fannie Mae pool: {:,}'.format(len(taken_fannie_deals)))
logging.debug('Number of loans sold to a Freddie Mac pool: {:,}'.format(len(taken_freddie_deals)))
logging.debug('Total amount sold to Fannie Mae pools: {:,}'.format(fannie_total_amount))
logging.debug('Total amount sold to Freddie Mac pools: {:,}'.format(freddie_total_amount))


weighted_ficos = [loan.fico * weight for loan, weight in fannie_loans_weights]
logging.debug('')
logging.debug('Constraint 13')
logging.debug(f'What is the amount-relative average FICO score among the loans sold to a Fannie Mae pool: {sum(weighted_ficos)}')
weighted_ficos = [loan.fico * weight for loan, weight in freddie_loans_weights]
logging.debug(f'What is the amount-relative average FICO score among the loans sold to a Freddie Mac pool: {sum(weighted_ficos)}')

weighted_dtis = [loan.dti * weight for loan, weight in fannie_loans_weights]
logging.debug('')
logging.debug('Constraint 14')
logging.debug(f'What is the amount-relative average debt-to-income ratio among the loans sold to a Fannie Mae pool: {sum(weighted_dtis)}')
weighted_dtis = [loan.dti * weight for loan, weight in freddie_loans_weights]
logging.debug(f'What is the amount-relative average debt-to-income ratio among the loans sold to a Freddie Mac pool: {sum(weighted_dtis)}')

taken_fannie_california_deals = [loans[taken_fannie_deal.loan_id].is_california for taken_fannie_deal in taken_fannie_deals]
taken_freddie_california_deals = [loans[taken_freddie_deal.loan_id].is_california for taken_freddie_deal in taken_freddie_deals]
logging.debug('')
logging.debug('Constraint 15')
c15_fannie = sum(taken_fannie_california_deals) / len(taken_fannie_deals)
c15_freddie = sum(taken_freddie_california_deals) / len(taken_freddie_deals)
logging.debug(f'For each loan, that is sold to a Fannie Mae pool, how many loans are also bound to a residence in California: {c15_fannie}')
logging.debug(f'For each loan, that is sold to a Freddie Mac pool, how many loans are also bound to a residence in California: {c15_freddie}')
c15_distance = abs(c15_fannie - c15_freddie)
logging.debug(f'Distance: {c15_distance}')


taken_fannie_primary_deals = [loans[taken_fannie_deal.loan_id].is_primary for taken_fannie_deal in taken_fannie_deals]
taken_freddie_primary_deals = [loans[taken_freddie_deal.loan_id].is_primary for taken_freddie_deal in taken_freddie_deals]
logging.debug('')
logging.debug('Constraint 16')
logging.debug(f'For each loan, that is sold to a Fannie Mae pool, how many loans are also bound to a primary residence: {sum(taken_fannie_primary_deals) / len(taken_fannie_deals)}')
logging.debug(f'For each loan, that is sold to a Freddie Mac pool, how many loans are also bound to a primary residence: {sum(taken_freddie_primary_deals) / len(taken_freddie_deals)}')

taken_fannie_cashout_deals = [loans[taken_fannie_deal.loan_id].is_cashout for taken_fannie_deal in taken_fannie_deals]
taken_freddie_cashout_deals = [loans[taken_freddie_deal.loan_id].is_cashout for taken_freddie_deal in taken_freddie_deals]
logging.debug('')
logging.debug('Constraint 17')
c17_fannie = sum(taken_fannie_cashout_deals) / len(taken_fannie_deals)
c17_freddie = sum(taken_freddie_cashout_deals) / len(taken_freddie_deals)
logging.debug(f'For each loan, that is sold to a Fannie Mae pool, how many loans have also been given out in cash: {c17_fannie}')
logging.debug(f'For each loan, that is sold to a Freddie Mac pool, how many loans have also been given out in cash: {c17_freddie}')
c17_distance = abs(c17_fannie - c17_freddie)
logging.debug(f'Distance: {c17_distance}')
