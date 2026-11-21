-- Assignment 3, Item 6: data modification commands
-- Run after the schema, sample inserts, and generated data are loaded.

-- 1. Delete low-confidence SELL analyses under 55% accuracy.
DELETE FROM AIAnalyses
WHERE recommendation = 'SELL'
  AND modelAccuracy < 0.55;

-- 2. Change low-confidence BUY predictions to HOLD.
UPDATE AIAnalyses
SET recommendation = 'HOLD'
WHERE recommendation = 'BUY'
  AND modelAccuracy < 0.60;

-- 3. Link each analysis to the company's revenue reports
-- from fiscal years before the prediction year.
INSERT INTO RevenueAnalysis (analysisUUID, revenueId)
SELECT a.analysisUUID, r.revenueId
FROM AIAnalyses AS a
JOIN Stocks AS s
  ON s.tickerSymbol = a.tickerSymbol
JOIN AnnualRevenueReport AS r
  ON r.companyId = s.companyId
 AND r.fiscalYear < EXTRACT(YEAR FROM a.predictionTimestamp)
ON CONFLICT (analysisUUID, revenueId) DO NOTHING;