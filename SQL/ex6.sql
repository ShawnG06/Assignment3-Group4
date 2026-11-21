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


-- 3. Link AI analyses to earlier company revenue reports.
INSERT INTO RevenueAnalysis (analysisUUID, revenueId)
SELECT a.analysisUUID, r.revenueId
FROM AIAnalyses AS a
JOIN Stocks AS s
    ON s.tickerSymbol = a.tickerSymbol
JOIN AnnualRevenueReport AS r
    ON r.companyId = s.companyId
   AND r.fiscalYear < EXTRACT(YEAR FROM a.predictionTimestamp)
WHERE NOT EXISTS (
    SELECT 1
    FROM RevenueAnalysis AS ra
    WHERE ra.analysisUUID = a.analysisUUID
      AND ra.revenueId = r.revenueId
);
