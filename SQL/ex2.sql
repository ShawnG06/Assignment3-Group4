--Tables 

CREATE TABLE Roles(
	roleName VARCHAR(30) PRIMARY KEY
);

CREATE TABLE Company(
	companyId INT PRIMARY KEY,
	companyName VARCHAR(150) NOT NULL,
	sector VARCHAR(100) NOT NULL
);

CREATE TABLE Users(
	email VARCHAR (255) PRIMARY KEY,
	passwordHash VARCHAR(255) NOT NULL,
	balance DECIMAL(18,2) NOT NULL DEFAULT 0,
	createdAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	roleName VARCHAR(30) NOT NULL,
	assignedDate DATE NOT NULL,

	CONSTRAINT fk_users_role
		FOREIGN KEY (roleName)
		REFERENCES Roles(roleName)
);

CREATE TABLE Stocks(
	tickerSymbol VARCHAR(10) PRIMARY KEY,
	companyId INT NOT NULL,
	exchange VARCHAR(30) NOT NULL,

	CONSTRAINT fk_stocks_company
		FOREIGN KEY (companyId)
		REFERENCES Company(companyId)
);

CREATE TABLE Holdings(
	email VARCHAR(255) NOT NULL,
	tickerSymbol VARCHAR(10) NOT NULL,
	holdingName VARCHAR(100),
	quantity DECIMAL(18,6) NOT NULL,
	averagePrice DECIMAL(12,4) NOT NULL,

	PRIMARY KEY (email, tickerSymbol),

	CONSTRAINT fk_holdings_user
		FOREIGN KEY (tickerSymbol)
		REFERENCES Users(email),
	
	CONSTRAINT chk_holdings_stock
		FOREIGN KEY (tickerSymbol)
		REFERENCES Stocks(tickerSymbol),
	
	CONSTRAINT chk_holdings_quantity
		CHECK (quantity >=0),
	
	CONSTRAINT chk_holdings_price
		CHECK (averagePrice >=0)
);

CREATE TABLE Transactions(
	id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	email VARCHAR(255) NOT NULL,
	tickerSymbol VARCHAR(10) NOT NULL,
	quantity DECIMAL(18,6) NOT NULL,
	createdAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	
	transactionType VARCHAR(4) NOT NULL,
	price DECIMAL(12,4) NOT NULL,

	CONSTRAINT fk_transactions_user
		FOREIGN KEY (email)
		REFERENCES Users(email),

	CONSTRAINT fk_transactions_stock
		FOREIGN KEY (tickerSymbol)
		REFERENCES Stocks(tickerSymbol),

	CONSTRAINT chk_transactions_type
		CHECK (transactionType IN ('BUY', 'SELL')),
	
	CONSTRAINT chk_transactions_quantity
		CHECK (quantity > 0),

	CONSTRAINT chk_transaction_price
		CHECK(price > 0)
);

CREATE TABLE StockPrices(
	tickerSymbol VARCHAR(10) NOT NULL,
	tradingDate DATE NOT NULL,
	openingPrice DECIMAL(12,4) NOT NULL,
	closingPrice DECIMAL(12,4) NOT NULL,
	dailyMax DECIMAL(12,4) NOT NULL,
	dailyMin DECIMAL(12,4) NOT NULL,

	PRIMARY KEY (tickerSymbol, tradingDate),

	CONSTRAINT fk_stockprices_stock
		FOREIGN KEY (tickerSymbol)
		REFERENCES Stocks(tickerSymbol),
	
	CONSTRAINT chk_stockprices_min
		CHECK (dailyMin >0),

	CONSTRAINT chk_stockprices_max
		CHECK(dailyMax > dailyMin),
	
	CONSTRAINT chk_stockprices_range
		CHECK (openingPrice BETWEEN dailyMin AND dailyMax),
	
	CONSTRAINT chk_stockprices_closing
		CHECK (closingPrice BETWEEN dailyMin AND dailyMax)
);

CREATE TABLE AIAnalyses(
	analysisUUID CHAR(36) PRIMARY KEY,
	tickerSymbol VARCHAR(10) NOT NULL,
	predictionTimestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	predictedPrice DECIMAL(12,4) NOT NULL,
	recommendation VARCHAR(10) NOT NULL,
	modelAccuracy DECIMAL (5,4) NOT NULL,
	reasoning TEXT NOT NULL, 

	CONSTRAINT fk_aianalyses_stock
		FOREIGN KEY (tickerSymbol)
		REFERENCES Stocks(tickerSymbol),

	CONSTRAINT chk_aianalyses_price
		CHECK (predictedPrice > 0),
	
	CONSTRAINT chk_aianalyses_recommendation
		CHECK (recommendation IN ('BUY', 'SELL', 'HOLD')),

	CONSTRAINT chk_aianalyses_accuracy
		CHECK (modelAccuracy BETWEEN 0 AND 1)
);

CREATE TABLE AnnualRevenueReport(
	revenueId INT PRIMARY KEY,
	companyId INT NOT NULL,
	fiscalYear SMALLINT NOT NULL,
	totalRevenue DECIMAL(20,2) NOT NULL,
	currency CHAR(3) NOT NULL,

	CONSTRAINT fk_revenue_company
		FOREIGN KEY (companyId)
		REFERENCES Company(companyId),
	
	CONSTRAINT uq_revenue_company_year
		UNIQUE (companyId, fiscalYear),
	
	CONSTRAINT chk_revenue_total
		CHECK (totalRevenue >= 0),

	CONSTRAINT chk_revenue_year
		CHECK (fiscalYear >= 1900)

);

CREATE TABLE RevenueAnalysis(
	analysisUUID UUID NOT NULL,
	revenueId INT NOT NULL,

	PRIMARY KEY (analysisUUID, revenueId),

	CONSTRAINT fk_revenue_analysis_analysis
		FOREIGN KEY(analysisUUID)
		REFERENCES AIAnalyses(analysisUUID),

	CONSTRAINT fk_revenue_analysis_revenue
		FOREIGN KEY (revenueId)
		REFERENCES AnnualRevenueReport(revenueId)
);




