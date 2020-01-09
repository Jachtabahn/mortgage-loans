#!/bin/bash

python genilp.py -vv && python sol2csv.py < MortgagesProblem.sol > solution/MortgagesSolution.csv && python scorer.py
