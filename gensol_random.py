import sqlite3
import logging
import random
import csv
import scorer

LOAN_FILE = './data/LoanData.csv'
OPTION_FILE = './data/PoolOptionData.csv'
COMBO_FILE = './data/EligiblePricingCombinationsSimple.csv'
CONSTRAINT_FILE = './data/ConstraintSimple.csv'

def choose_buyers():
    chosen_buyer = {}
    for loan_id in buyers:
        loan_buyers = buyers[loan_id]
        only_retained = [suggestion for suggestion in loan_buyers if suggestion[1] == 'Retained']

        if only_retained:
            chosen = random.choice(only_retained)
        else:
            chosen = random.choice(loan_buyers)
        chosen_buyer[loan_id] = chosen
    return chosen_buyer

SEED = 40
random.seed(SEED)
logging.error(f'Random seed set to {SEED}')

# get the dataset from the database
connection = sqlite3.connect('data/mortgages.db')
cursor = connection.cursor()
cursor.execute('''
    SELECT LoanID, PoolOptonj, Servicerk
        FROM EligiblePricingCombinations ORDER BY LoanID;
''')
sellings = cursor.fetchall()
connection.close()

buyers = {}
for selling in sellings:
    loan_id, pool, servicer = selling
    if loan_id not in buyers:
        buyers[loan_id] = []
    loan_buyers = buyers[loan_id]
    loan_buyers.append((pool, servicer))

loans, pools, combs, constraints, states, \
occupancy_types, purposes, property_types = scorer.load_everything(LOAN_FILE, OPTION_FILE, COMBO_FILE, CONSTRAINT_FILE)

feasible = False
solution_count = 0
while not feasible:
    chosen_buyer = choose_buyers()
    solution_count += 1
    logging.error(f'Solution #{solution_count}')

    feasible = True
    try:
        obj = 0
        used = set()
        for i, (j, k) in chosen_buyer.items():
            assert (i, j, k) in combs, f'Invalid combinations! {i}, {j}, {k}'
            assert (i, j, k) not in used, 'Duplicated combinations!'
            used.add((i, j, k))
            pijk = combs[(i, j, k)]
            obj += float(pijk) / 100 * loans[i].Li

        score = scorer.evaluate_loaded(loans, pools, combs, constraints, states, \
        occupancy_types, purposes, property_types, obj, used)
    except AssertionError as e:
        feasible = False

print('Found feasible solution:')
print(chosen_buyer)
