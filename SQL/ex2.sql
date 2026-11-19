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

	CONSTRAINT fk_users_role
		FOREIGN KEY (roleName)
		REFERENCES Roles(roleName),
);

CREATE TABLE Stocks(
	tickerSymbol VARCHAR(10) PRIMARY KEY,
	companyId, INT NOT NULL,
	exchange VARCHAR(30) NOT NULL,

	CONSTRAINT fk_stocks_company
		FOREIGN KEY (companyId)
		REFERENCES Company(companyId)
);

CREATE TABLE Holdings(
	email VARCHAR(255) NOT NULL),
	tickerSymbol VARCHAR(10) NOT NULL,
	holdingName VARCHAR(100),
	quantity DECIMAL(18,6) NOT NULL,
	averagePrice DECIMAL(12,4) NOT NULL,

	PRIMARY KEY (email, tickerSymbol),

	CONSTRAINT fk_holdings_user
		FOREIGN KEY (tickerSymbol)
		REFERENCES Stocks(tickerSymbol),
	
	CONSTRAINT chk_holdings_stock
		FOREIGN KEY (tickerSymbol)
		REFERENCES Stocks(tickerSymbol),
	
	CONSTRAINT chk_holdings_quantity
		CHECK (quantity >=0),
	
	CONSTRAINT chk_holdings_price
		CHECK (average
);

CREATE TABLE Transactions(
	id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	email VARCHAR(255) NOT NULL,
	tickerSymbol VARCHAR(10) NOT NULL,
	
	createdAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	
	transactionType 
);

CREATE TABLE StockPrices();

CREATE TABLE AIAnalyses();

CREATE TABLE AnnualRevenueReport();

CREATE TABLE RevenueAnalysis();



