class Loan:

    def __init__(self, row):
        self.i = row['LoanID']
        self.Li = float(row['Amount'].replace(',', ''))
        assert row['HighBalFlag'] in ['Y', 'N']
        self.HighBalFlag = int(row['HighBalFlag'] == 'Y')
        self.FICO = float(row['FICO'])
        self.DTI = float(row['DTI'])
        self.state = row['PropState']
        self.purpose = row['Purpose']
        self.occupancy = row['PropOcc']
        self.property_type = row['PropType']


class Pool:

    def __init__(self, row):
        self.j = row['Pool Option, j']
        self.pool_type = row['Pool Type']
        assert self.pool_type in ['Multi-Issuer', 'Single-Issuer']
        self.balance_type = row['Pool Balance Type']
        self.agency = row['Agency']


import csv

def load_loans(filename):
    loans = {}
    try:
        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                loan = Loan(row)
                assert loan.i not in loans
                loans[loan.i] = loan
        print(f'[INFO] Total # of loans = {len(loans)}')
    except:
        print('[Error] LoadData.csv has a wrong format!')

    return loans


def load_pools(filename):
    pools = {}
    try:
        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                pool = Pool(row)
                assert pool.j not in pools
                pools[pool.j] = pool
        print(f'[INFO] Total # of pools = {len(pools)}')
    except:
        print('[Error] PoolOptionData.csv has a wrong format!')

    return pools


def load_combs(filename):
    combs = {}
    try:
        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                i = row['LoanID']
                j = row['Pool Opton, j']
                k = row['Servicer, k']

                assert k in ['Pingora', 'Retained', 'Two Harbors']
                pijk = row['Price, P_ijk']

                assert (i, j, k) not in combs
                combs[(i, j, k)] = pijk
        print(f'[INFO] Total # of combs = {len(combs)}')
    except:
        print('[Error] EligiblePricingCombinations.csv has a wrong format!')

    return combs


def load_constraints(filename):
    constraints = {}
    try:
        for line in open(filename):
            parts = line.split(',')
            c = parts[0]
            assert c[0] == 'c' and int(c[1:]) <= 18 and (int(c[1:])) >= 1
            assert c not in constraints
            constraints[c] = float(parts[1])
        print(f'[INFO] Total # of constraints = {len(constraints)}')
    except:
        print('[Error] Constraint file has a wrong format!')

    return constraints
