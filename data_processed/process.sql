
SELECT LoanID AS Loan,
	Amount, FICO AS Fico,
	DTI AS Dti,
	HighBalFlag == 'Y' AS IsExpensive,
	PropState == 'CA' AS IsCalifornia,
	Purpose == 'Cashout' AS IsCashout,
	PropOcc == 'Primary' AS IsPrimary FROM LoanData;

SELECT PoolOptionj AS Pool,
	PoolType,
	PoolBalanceType,
	Servicer FROM PoolOptionData;

SELECT EligiblePricingCombinations.LoanID AS Loan,
	PoolOptonj AS Pool,
	PriceP_ijk / 100 * Amount AS Price
	FROM EligiblePricingCombinations INNER JOIN LoanData
	ON EligiblePricingCombinations.LoanID == LoanData.LoanID ORDER BY LoanData.LoanID;

SELECT PoolOptonj AS Pool,
	LoanData.LoanID AS Loan,
	PriceP_ijk / 100 * Amount AS Price
	FROM EligiblePricingCombinations INNER JOIN LoanData
	ON EligiblePricingCombinations.LoanID == LoanData.LoanID ORDER BY Pool;


SELECT DISTINCT PropOcc FROM LoanData;

SELECT DISTINCT PropState FROM LoanData;

SELECT DISTINCT PropType FROM LoanData;

SELECT DISTINCT Purpose FROM LoanData;
