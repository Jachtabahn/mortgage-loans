

# Diminish the number of buyers
cat data_processed/ChooseLoan.csv | sed -n '1~2p' > processed_small/ChooseLoan.csv
