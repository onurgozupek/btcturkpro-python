import btcturk-python

#Create Order Example

pairSymbol = "BTC_TRY"
price = "53000"
quantity = "0.01"
orderType = "buy"
orderMethod = "limit"
stopPrice = "0"

createOrder(pairSymbol , price , quantity , orderType , orderMethod , stopPrice)

#Check Balances Example

checkBalances(pairSymbol)


#Delete Order Example

orderId = 1234567890
deleteOrder(orderId)


#Check Open Orders Example
checkOpenOrders(pairSymbol)


#Print OrderBook (last 10 orders) Example
orderBook(pairSymbol, 10, 1):


#Print OrderBook (last 30 orders) Example
orderBook(pairSymbol, 30, 1):


#Get User Transactions Example (buy orders)
numerator = "BTC"
denominator = "TRY"
orderType = "buy"
userTransactions(numerator, denominator, orderType)


#Get User Transactions Example (sell orders)
numerator = "BTC"
denominator = "TRY"
orderType = "sell"
userTransactions(numerator, denominator, orderType)


#Get User Transactions Example (all order types)
numerator = "BTC"
denominator = "TRY"
orderType = "all"
userTransactions(numerator, denominator, orderType)


#Get User Transactions Example (Only crypto pair transactions)
numerator = "crypto"
orderType = "all"
userTransactions(numerator, denominator, orderType)


#Get User Transactions Example (All pairs, both buy/sell transactions)
numerator = "all"
orderType = "all"
userTransactions(numerator, denominator, orderType)
