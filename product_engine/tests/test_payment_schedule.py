from product_engine.src.app.util import payment_schedule
import datetime

def test_payment1():
    schedule = payment_schedule(principal=1000000, interest=12, term=24, start_date=datetime.date.today())
    reference_principal = [37073.47, 37444.21, 37818.65, 38196.84, 38578.80, 38964.59, 39354.24, 39747.78, 40145.26, 40546.71, 
                           40952.18, 41361.70, 41775.32, 42193.07, 42615.00, 43041.15, 43471.56, 43906.28, 44345.34, 44788.79, 
                           45236.68, 45689.05, 46145.94, 46607.40]
    reference_interest = [10000.00, 9629.27, 9254.82, 8876.64, 8494.67, 8108.88, 7719.23, 7325.69, 6928.21, 6526.76, 6121.29,
                          5711.77, 5298.16, 4880.40, 4458.47, 4032.32, 3601.91, 3167.19, 2728.13, 2284.68, 1836.79, 1384.42,
                          927.53, 466.07]
    for i in range(len(schedule)):
        assert schedule[i]["principal_payment"] == reference_principal[i]
        assert schedule[i]["interest_payment"] == reference_interest[i]

def test_payment2():
    schedule = payment_schedule(principal=10000, interest=90, term=8, start_date=datetime.date.today())
    reference_principal = [957.27, 1029.07, 1106.25, 1189.21, 1278.40, 1374.29, 1477.36, 1588.16]
    reference_interest = [750.00, 678.20, 601.02, 518.06, 428.87, 332.99, 229.91, 119.11]
    for i in range(len(schedule)):
        assert schedule[i]["principal_payment"] == reference_principal[i]
        assert schedule[i]["interest_payment"] == reference_interest[i]


def test_payment3():
    schedule = payment_schedule(principal=500000, interest=22, term=36, start_date=datetime.date.today())
    reference_principal = [9928.56, 10110.58, 10295.94, 10484.70, 10676.92, 10872.67, 11072.00, 11274.99, 11481.69, 
                           11692.19, 11906.55, 12124.83, 12347.12, 12573.49, 12804.00, 13038.74, 13277.78, 13521.21,
                           13769.10, 14021.53, 14278.59, 14540.37, 14806.94, 15078.40, 15354.84, 15636.35, 15923.01,
                           16214.93, 16512.21, 16814.93, 17123.21, 17437.13, 17756.81, 18082.35, 18413.86, 18751.45,]
    reference_interest = [9166.67, 8984.64, 8799.28, 8610.52, 8418.30, 8222.56, 8023.23, 7820.24, 7613.53, 7403.04,
                          7188.68, 6970.39, 6748.10, 6521.74, 6291.23, 6056.49, 5817.44, 5574.02, 5326.13, 5073.69,
                          4816.63, 4554.86, 4288.28, 4016.82, 3740.39, 3458.88, 3172.21, 2880.29, 2583.02, 2280.30,
                          1972.02, 1658.10, 1338.42, 1012.87, 681.36, 343.78]
    for i in range(len(schedule)):
        assert schedule[i]["principal_payment"] == reference_principal[i]
        assert schedule[i]["interest_payment"] == reference_interest[i]