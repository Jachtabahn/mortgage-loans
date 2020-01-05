import csv, sys, traceback
import collections
from data import *

def evaluate(LOAN_FILE, OPTION_FILE, COMBO_FILE, CONSTRAINT_FILE, SOLUTION_FILE):
    print(f'[INFO] Loan File: {LOAN_FILE}')
    print(f'[INFO] Pool File: {OPTION_FILE}')
    print(f'[INFO] Combination File: {COMBO_FILE}')
    print(f'[INFO] Constraint File: {CONSTRAINT_FILE}')
    print(f'[INFO] Solution File: {SOLUTION_FILE}')

    loans = load_loans(LOAN_FILE)
    pools = load_pools(OPTION_FILE)
    combs = load_combs(COMBO_FILE)
    constraints = load_constraints(CONSTRAINT_FILE)
    print('[INFO]', constraints)

    states = sorted(list(set([loan.state for loan in loans.values()])))
    occupancy_types = sorted(list(set([loan.occupancy for loan in loans.values()])))
    purposes = sorted(list(set([loan.purpose for loan in loans.values()])))
    property_types = sorted(list(set([loan.property_type for loan in loans.values()])))
    print('[INFO] # of states =', len(states))
    print('[INFO] # of occupancies =', len(occupancy_types))
    print('[INFO] # of property_types =', len(property_types))
    print('[INFO] # of purposes =', len(purposes))

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

    used = sorted(list(used))
    group_by_j, group_by_k = {}, {}
    byAgency = {}
    agentA, agentB = 'Freddie Mac', 'Fannie Mae'
    byAgency[agentA] = []
    byAgency[agentB] = []
    for (i, j, k) in used:
        if j not in group_by_j:
            group_by_j[j] = []
        if k not in group_by_k:
            group_by_k[k] = []
        group_by_j[j].append((i, k))
        group_by_k[k].append((i, j))
        byAgency[pools[j].agency].append(loans[i])

    print(len(group_by_j), len(group_by_k))

    for j, pairs in group_by_j.items():
        high_ratio, total = 0, 0
        for (i, k) in pairs:
            high_ratio += loans[i].HighBalFlag * loans[i].Li
            total += loans[i].Li
        if total > 0:
            high_ratio /= total

        if 'c1' in constraints:
            if pools[j].balance_type.find('Standard') != -1:
                assert high_ratio <= constraints['c1'], f'[Error] c1 violated on pool {j}: {high_ratio}'
            else:
                assert high_ratio <= 1, f'[Error] c1 violated on pool {j}'

        if 'c2' in constraints:
            if pools[j].pool_type == 'Single-Issuer':
                assert total >= constraints['c2'], f'c2 violated on pool {j}: {total}'
            else:
                assert total >= 0, f'c2 violated on pool {j}, {total}'

    if True:
        k = 'Pingora'
        high_ratio, avg_fico, avg_dti, total = 0, 0, 0, 0
        p_ca, cnt_pingora = 0, 0
        for i, j in group_by_k[k]:
            cnt_pingora += int(k == 'Pingora')
            p_ca += int((loans[i].state == 'CA') and (k == 'Pingora'))

            total += loans[i].Li
            high_ratio += loans[i].HighBalFlag * loans[i].Li
            avg_fico += loans[i].FICO * loans[i].Li
            avg_dti += loans[i].DTI * loans[i].Li
        if total > 0:
            high_ratio /= total
            avg_fico /= total
            avg_dti /= total
        if cnt_pingora > 0:
            p_ca /= cnt_pingora

        if 'c3' in constraints:
            assert total <= constraints['c3'], f'c3 violated on pool {j}: {total}'
        if 'c4' in constraints:
            assert high_ratio <= constraints['c4'], f'c4 violated on pool {j}: {high_ratio}'
        if 'c5' in constraints:
            assert avg_fico >= constraints['c5'], f'c5 violated on pool {j}: {avg_fico}'
        if 'c6' in constraints:
            assert avg_dti <= constraints['c6'], f'c6 violated on pool {j}: {avg_dti}'
        if 'c7' in constraints:
            assert p_ca <= constraints['c7'], f'c7 violated on pool {j}: {p_ca}'

    if True:
        k = 'Two Harbors'
        high_ratio, avg_fico, avg_dti, total = 0, 0, 0, 0
        p_r, p_pr, cnt_two_harbors = 0, 0, 0
        for i, j in group_by_k[k]:
            cnt_two_harbors += int(k == 'Two Harbors')
            p_r += int((loans[i].purpose == 'Cashout') and (k == 'Two Harbors'))
            p_pr += int((loans[i].occupancy == 'Primary') and (k == 'Two Harbors'))

            total += loans[i].Li
            high_ratio += loans[i].HighBalFlag * loans[i].Li
            avg_fico += loans[i].FICO * loans[i].Li
            avg_dti += loans[i].DTI * loans[i].Li
        if total > 0:
            high_ratio /= total
            avg_fico /= total
            avg_dti /= total
        if cnt_two_harbors > 0:
            p_r /= cnt_two_harbors
            p_pr /= cnt_two_harbors

        if 'c8' in constraints:
            assert total >= constraints['c8'], f'c8 violated on pool {j}: {total}'
        if 'c9' in constraints:
            assert avg_fico >= constraints['c9'], f'c9 violated on pool {j}: {avg_fico}'
        if 'c10' in constraints:
            assert avg_dti <= constraints['c10'], f'c10 violated on pool {j}: {avg_dti}'
        if 'c11' in constraints:
            assert p_r <= constraints['c11'], f'c11 violated on pool {j}: {p_r}'
        if 'c12' in constraints:
            assert p_pr >= constraints['c12'], f'c12 violated on pool {j}: {p_pr}'


    measure = {}
    for agency, loan_list in byAgency.items():
        total, avg_fico, avg_dti = 0, 0, 0
        state_cnt, occupancy_cnt, purpose_cnt, property_type_cnt = \
            collections.defaultdict(int), collections.defaultdict(int), collections.defaultdict(int), collections.defaultdict(int)
        for loan in loan_list:
            total += loan.Li
            avg_fico += loan.FICO * loan.Li
            avg_dti += loan.DTI * loan.Li
            state_cnt[loan.state] += 1
            occupancy_cnt[loan.occupancy] += 1
            purpose_cnt[loan.purpose] += 1
            property_type_cnt[loan.property_type] += 1
        if total > 0:
            avg_fico /= total
            avg_dti /= total
        measure[agency] = [avg_fico, avg_dti]
        for state in states:
            measure[agency].append(state_cnt[state] / len(loan_list))
        for occupancy in occupancy_types:
            measure[agency].append(occupancy_cnt[occupancy] / len(loan_list))
        for purpose in purposes:
            measure[agency].append(purpose_cnt[purpose] / len(loan_list))
        for property_type in property_types:
            measure[agency].append(property_type_cnt[property_type] / len(loan_list))

    ptr = 0
    if 'c13' in constraints:
        assert abs(measure[agentA][ptr] - measure[agentB][ptr]) <= constraints['c13'], f'c13 violated: {measure[agentA][ptr]} vs. {measure[agentB][ptr]}'
    ptr = 1

    if 'c14' in constraints:
        assert abs(measure[agentA][ptr] - measure[agentB][ptr]) <= constraints['c14'], f'c14 violated: {measure[agentA][ptr]} vs. {measure[agentB][ptr]}'
    ptr = 2

    if 'c15' in constraints:
        for i in range(len(states)):
            assert abs(measure[agentA][ptr + i] - measure[agentB][ptr + i]) <= constraints['c15'], f'c15 violated on state {states[i]}: {measure[agentA][ptr + i]} vs. {measure[agentB][ptr + i]}'
    ptr += len(states)

    if 'c16' in constraints:
        for i in range(len(occupancy_types)):
            assert abs(measure[agentA][ptr + i] - measure[agentB][ptr + i]) <= constraints['c16'], f'c16 violated on occupancy_type {occupancy_types[i]}: {measure[agentA][ptr + i]} vs. {measure[agentB][ptr + i]}'
    ptr += len(occupancy_types)

    if 'c17' in constraints:
        for i in range(len(purposes)):
            assert abs(measure[agentA][ptr + i] - measure[agentB][ptr + i]) <= constraints['c17'], f'c17 violated on purpose {purposes[i]}: {measure[agentA][ptr + i]} vs. {measure[agentB][ptr + i]}'
    ptr += len(purposes)

    if 'c18' in constraints:
        for i in range(len(property_types)):
            assert abs(measure[agentA][ptr + i] - measure[agentB][ptr + i]) <= constraints['c18'], f'c17 violated on property_type {property_types[i]}: {measure[agentA][ptr + i]} vs. {measure[agentB][ptr + i]}'
    print('[INFO] all checks passed')
    print(f'[INFO] Score = {obj}')
    return obj


if __name__ == '__main__':
    if len(sys.argv) == 3:
        DATA_FOLDER = sys.argv[1]
        SOLUTION_FOLDER = sys.argv[2]
    else:
        DATA_FOLDER = './data'
        SOLUTION_FOLDER = './solution'

    COMBO_FILE = DATA_FOLDER + '/EligiblePricingCombinations.csv'
    LOAN_FILE = DATA_FOLDER + '/LoanData.csv'
    OPTION_FILE = DATA_FOLDER + '/PoolOptionData.csv'
    CONSTARINT_FILES = [DATA_FOLDER + '/Constraints.csv']
    SOLUTION_FILES = [SOLUTION_FOLDER + '/twoharbors_allocation.csv']

    scores = []
    for CONSTRAINT_FILE, SOLUTION_FILE in zip(CONSTARINT_FILES, SOLUTION_FILES):
        score = 0
        try:
            score = evaluate(LOAN_FILE, OPTION_FILE, COMBO_FILE, CONSTRAINT_FILE, SOLUTION_FILE)
        except AssertionError as e:
            _, _, tb = sys.exc_info()
            traceback.print_tb(tb) # Fixed format
            print('Error Message:', e)
        except FileNotFoundError as e:
            _, _, tb = sys.exc_info()
            traceback.print_tb(tb) # Fixed format
            print('Error Message:', e)
        scores.append(score)

    final_score = sum(scores) / len(scores)

    print(f'Final Score = {final_score}')

