import argparse
import itertools
import logging
import csv

def compute_feasible_subsets(pool, pool_buyers):
    feasible_subsets = []
    num_subsets, num_feasible = 0, 0
    for subset_buyers in itertools.combinations(pool_buyers, 1):
        num_subsets += 1
        logging.debug(f'Subset of buyers {num_subsets}')
        for buyer in subset_buyers:
            logging.debug(buyer)

        # check constraints on the subset_buyers given the loans and pools
        subset_loan_ids = [buyer.loan_id for buyer in subset_buyers]
        subset_loans = [loans[loan_id] for loan_id in subset_loan_ids]
        show_list(subset_loans)

        ok = check_constraints(pool, subset_loans)
        logging.debug(f'OK: {ok}')
        logging.debug(f'---------------------------------------------------\n\n')

        if ok:
            num_feasible += 1
            feasible_subsets.append(subset_buyers)
    return feasible_subsets

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

    if pool.is_standard:
        logging.debug('Check c1: normal_expense <= c1')
        logging.debug(f'Check c1: {normal_expense} <= {constraints["c1"]}')
        c1 = (normal_expense <= constraints["c1"])
        logging.debug(f'Check c1: {c1}')
        ok = ok and c1

    if pool.is_single:
        logging.debug('Check c2: amounts_sum >= c2')
        logging.debug(f'Check c2: {amounts_sum} >= {constraints["c2"]}')
        c2 = (amounts_sum >= constraints["c2"])
        logging.debug(f'Check c2: {c2}')
        ok = ok and c2

    if pool.servicer == 'Pingora':
        logging.debug('Check c3: amounts_sum <= c3')
        logging.debug(f'Check c3: {amounts_sum} <= {constraints["c3"]}')
        c3 = (amounts_sum <= constraints["c3"])
        logging.debug(f'Check c3: {c3}')
        ok = ok and c3

        logging.debug('Check c4: normal_expense <= c4')
        logging.debug(f'Check c4: {normal_expense} <= {constraints["c4"]}')
        c4 = (normal_expense <= constraints["c4"])
        logging.debug(f'Check c4: {c4}')
        ok = ok and c4

        logging.debug('Check c5: normal_fico >= c5')
        logging.debug(f'Check c5: {normal_fico} >= {constraints["c5"]}')
        c5 = (normal_fico >= constraints["c5"])
        logging.debug(f'Check c5: {c5}')
        ok = ok and c5

        logging.debug('Check c6: normal_dti <= c6')
        logging.debug(f'Check c6: {normal_dti} <= {constraints["c6"]}')
        c6 = (normal_dti <= constraints["c6"])
        logging.debug(f'Check c6: {c6}')
        ok = ok and c6

        logging.debug('Check c7: average_california <= c7')
        logging.debug(f'Check c7: {average_california} <= {constraints["c7"]}')
        c7 = (average_california <= constraints["c7"])
        logging.debug(f'Check c7: {c7}')
        ok = ok and c7

    if pool.servicer == 'Two Harbors':
        logging.debug('Check c8: amounts_sum >= c8')
        logging.debug(f'Check c8: {amounts_sum} >= {constraints["c8"]}')
        c8 = (amounts_sum >= constraints["c8"])
        logging.debug(f'Check c8: {c8}')
        ok = ok and c8

        logging.debug('Check c9: normal_fico >= c9')
        logging.debug(f'Check c9: {normal_fico} >= {constraints["c9"]}')
        c9 = (normal_fico >= constraints["c9"])
        logging.debug(f'Check c9: {c9}')
        ok = ok and c9

        logging.debug('Check c10: normal_dti <= c10')
        logging.debug(f'Check c10: {normal_dti} <= {constraints["c10"]}')
        c10 = (normal_dti <= constraints["c10"])
        logging.debug(f'Check c10: {c10}')
        ok = ok and c10

        logging.debug('Check c11: average_cashout <= c11')
        logging.debug(f'Check c11: {average_cashout} <= {constraints["c11"]}')
        c11 = (average_cashout <= constraints["c11"])
        logging.debug(f'Check c11: {c11}')
        ok = ok and c11

        logging.debug('Check c12: average_primary >= c12')
        logging.debug(f'Check c12: {average_primary} >= {constraints["c12"]}')
        c12 = (average_primary >= constraints["c12"])
        logging.debug(f'Check c12: {c12}')
        ok = ok and c12

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

if __name__ == '__main__':
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
    with open('data/processed/Loans.csv') as loans_file:
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
    with open('data/processed/Pools.csv') as pools_file:
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
    with open('data/processed/Constraints.csv') as constraints_file:
        constraints_reader = csv.reader(constraints_file)
        for name, value_string in constraints_reader:
            value = float(value_string)
            constraints[name] = value

    buyers = []
    with open('data/processed/ChooseLoan.csv') as choose_pool_file:
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

    buyer_subsets = []

    num_total_subsets = 0
    logging.debug(f'Will only consider subsets of size 1..')

    for pool_id in pools:
        pool = pools[pool_id]
        pool_buyers = [buyer for buyer in buyers if buyer.pool_id == pool_id]
        feasible_subsets = compute_feasible_subsets(pool, pool_buyers)
        buyer_subsets.extend(feasible_subsets)

        # num_total_subsets += num_pool_subsets
        # logging.info(f'Found {num_feasible} feasible subsets out of {num_pool_subsets} subsets for pool {pool_id}')
        # logging.info(f'Found {len(buyer_subsets)} feasible subsets out of {num_total_subsets} considered subsets in total.')
        # logging.info('-------------------------------------------------------\n')

    # for subset in buyer_subsets:
    #     logging.info('--------------->')
    #     for buyer in subset:
    #         logging.info(buyer)
    #     logging.info('<---------------')

    logging.info(f'We know {len(buyer_subsets)} feasible subsets.')

    chosen_buyers = []

    chosen_subset = buyer_subsets[0]
    chosen_buyers.extend(chosen_subset)

    chosen_loan_ids = [buyer.loan_id for buyer in chosen_subset]

    logging.info(f'Chosen loan ids: {chosen_loan_ids}')

    delete_indices = []
    for i, subset in enumerate(buyer_subsets):
        contains_chosen_loan = False
        for buyer in subset:
            if buyer.loan_id in chosen_loan_ids:
                contains_chosen_loan = True
                break
        if contains_chosen_loan:
            delete_indices.append(i)

    for i in delete_indices[::-1]:
        subset = buyer_subsets[i]
        for buyer in subset:
            logging.info(buyer)
        del buyer_subsets[i]

    logging.info(f'We know {len(buyer_subsets)} feasible subsets.')
