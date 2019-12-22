import sqlite3
import random
import csv
import scorer

LOAN_FILE = './data/LoanData.csv'
OPTION_FILE = './data/PoolOptionData.csv'
COMBO_FILE = './data/EligiblePricingCombinations.csv'
CONSTRAINT_FILE = './data/ConstraintA.csv'
SOLUTION_FILE = './solution/A.csv'

def choose_buyers():
    chosen_buyer = {}
    for loan_id in buyers:
        loan_buyers = buyers[loan_id]
        chosen = random.choice(loan_buyers)
        chosen_buyer[loan_id] = chosen
    return chosen_buyer

SEED = 40
random.seed(SEED)

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
occupancy_types, purposes, property_types = load_everything(LOAN_FILE, OPTION_FILE, COMBO_FILE, CONSTRAINT_FILE)



feasible = False
i = 0
while not feasible:
    chosen_buyer = choose_buyers()
    i += 1
    print(f'Chosen solution {i} of random seed {SEED}')

    with open(SOLUTION_FILE, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        obj = 0
        used = set()
        for row in reader:
            i = row['Loan']
            j = row['Pool']
            k = row['Servicer']
            assert (i, j, k) in combs, f'Invalid combinations! {i}, {j}, {k}'
            assert (i, j, k) not in used, 'Duplicated combinations!'
            used.add((i, j, k))
            pijk = combs[(i, j, k)]
            obj += float(pijk) / 100 * loans[i].Li
    return obj, used

    with open('solution/A.csv', 'w') as solution_file:
        writer = csv.writer(solution_file)
        writer.writerow(['Loan','Pool','Servicer'])
        for loan_id, (pool, servicer) in chosen_buyer.items():
            writer.writerow([loan_id, pool, servicer])

    feasible = True
    try:
        score = evaluate_loaded(loans, pools, combs, constraints, states, \
        occupancy_types, purposes, property_types, obj, used)
    except AssertionError as e:
        feasible = False
