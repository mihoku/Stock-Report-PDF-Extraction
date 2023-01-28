import PyPDF2
import re
import pandas as pd

def read_pdf(filename):
    pdfFileObj = open(filename, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    extracted_text=''
    for i in range(pdfReader.numPages):
        pageObj = pdfReader.getPage(i)
        extracted_text+=pageObj.extractText()
    pdfFileObj.close()
    return extracted_text

def process_text(text):
    keyword_start = '\nSummary including statutory levies -\nBuy\nSell'
    keyword_limit = '\n(`) Order\nTimeGross Rate'
    return text[text.find(keyword_start)+len(keyword_start):text.find(keyword_limit)]

def transaction_splitter(text):
    limiter = '\nSummary including statutory levies -\nBuy\nSell'
    return text.split(limiter)

def anomaly_parser(text):
    transaction_line = []
    splitted_text = text.split('\n')
    #read the transaction type
    if splitted_text[7][0]!='0':
        transaction_line.append('SELL')
    else:
        transaction_line.append('BUY')
    #read the security/stock name
    transaction_line.append(re.sub('\Security$', '', splitted_text[4]))
    #read the transaction quantity
    quantity_text = ''
    if splitted_text[7][0]!='0':
        transaction_line.append(int(splitted_text[7].split(' ')[0])/10)
        quantity_text+=splitted_text[7].split(' ')[0][:-1]
    else:
        transaction_line.append(int(splitted_text[7].split(' ')[0]))
        quantity_text+=splitted_text[7].split(' ')[0][1:]
    #read the transaction value
    transaction_value_text = ''
    if splitted_text[7][-4:]=='0.00':
        transaction_line.append(float(splitted_text[8][:-6]))
        transaction_value_text +=splitted_text[8][:-6]
    else:
        transaction_line.append(float(splitted_text[7].split(' ')[1]))
        transaction_value_text +=splitted_text[7].split(' ')[1]
    #calculate trade price per unit
    unit_price = transaction_line[3]/transaction_line[2]
    transaction_line.append(unit_price)
    #read the total brokerage value
    brokerage_text = ''
    if splitted_text[7][0]!='0':
        transaction_line.append(float(splitted_text[9][:-6]))
    else:
        brokerage_text+=splitted_text[8][4:]
        transaction_line.append(float(brokerage_text))
    #read exchange transaction charge
    if splitted_text[7][0]!='0':
        transaction_line.append(float(splitted_text[10][:-6]))
    else:
        transaction_line.append(float(splitted_text[9][6:]))
    #read the SEBI turnover charges
    if splitted_text[7][0]!='0':
        transaction_line.append(float(splitted_text[13].split(' ')[1][:splitted_text[13].split(' ')[1].find('SEBI')]))
    else:
        transaction_line.append(float(splitted_text[15][:splitted_text[15].find('(`)Total Goods')]))
    #read total goods and services tax
    if splitted_text[7][0]!='0':
        transaction_line.append(float(splitted_text[19]))
    else:
        transaction_line.append(float(splitted_text[18]))        
    #read stamp duty
    if splitted_text[7][0]!='0':
        transaction_line.append(float(splitted_text[11][:-6]))
    else:
        transaction_line.append(float(splitted_text[10][6:]))        
    #read the security transaction tax (stt)
    if splitted_text[7][0]!='0':
        transaction_line.append(float(splitted_text[12][:-6]))
    else:
        transaction_line.append(float(splitted_text[11][6:]))  
    #read the net payable/receivable
    if splitted_text[7][0]!='0':
        transaction_line.append(float(splitted_text[13].split(' ')[0]))
    else:
        transaction_line.append(float(splitted_text[12][6:]))  
    return transaction_line

def transaction_parser(text):
    transaction_line = []
    if(text.find(' Page ')==-1):
        splitted_text = text.split('\n')
        #read the transaction type
        if splitted_text[9][-4:]=='0.00':
            transaction_line.append('SELL')
        else:
            transaction_line.append('BUY')
        #read the security/stock name
        transaction_line.append(re.sub('\Security$', '', splitted_text[5]))
        #read the transaction quantity
        quantity_text = ''
        if splitted_text[8][0]!=' ':
            if splitted_text[8][0]!='0':
                transaction_line.append(int(splitted_text[8])/10)
                quantity_text+=splitted_text[8][:-1]
            else:
                transaction_line.append(int(splitted_text[8][1:]))
                quantity_text+=splitted_text[8][1:]
        else:
            if splitted_text[8].split(' ')[1]!='0':
                transaction_line.append(int(splitted_text[8].split(' ')[1]))
                quantity_text+=splitted_text[8].split(' ')[1]
            else:
                transaction_line.append(int(splitted_text[8].split(' ')[2]))
                quantity_text+=splitted_text[8].split(' ')[2]
        #read the transaction value
        transaction_value_text = ''
        if splitted_text[9][-4:]=='0.00':
            transaction_line.append(float(splitted_text[10]))
            transaction_value_text +=splitted_text[10]
        else:
            transaction_line.append(float(splitted_text[9][len(quantity_text):]))
            transaction_value_text +=splitted_text[9][len(quantity_text):]
        #calculate trade price per unit
        unit_price = transaction_line[3]/transaction_line[2]
        transaction_line.append(unit_price)
        #read the total brokerage value
        brokerage_text = ''
        if splitted_text[11]!='0.0000':
            transaction_line.append(float(splitted_text[12][:-6]))
        else:
            brokerage_text+=splitted_text[11][len(transaction_value_text):]
            transaction_line.append(float(brokerage_text))
        #read exchange transaction charge
        if splitted_text[12][:-6]!='0.0000':
            transaction_line.append(float(splitted_text[13]))
        else:
            transaction_line.append(float(splitted_text[12][-6:]))
        #read the SEBI turnover charges
        if splitted_text[11]!='0.0000':
            transaction_line.append(float(splitted_text[22][:splitted_text[22].find('0.0000(`)Total Goods')]))
        else:
            transaction_line.append(float(splitted_text[22][6:splitted_text[22].find('(`)Total Goods')]))
        #read total goods and services tax
        if splitted_text[11]!='0.0000':
            transaction_line.append(float(splitted_text[-2]))
        else:
            transaction_line.append(float(splitted_text[-3]))        
        #read stamp duty
        stamp_duty_text = ''
        if splitted_text[11]!='0.0000':
            transaction_line.append(float(splitted_text[15]))
        else:
            stamp_duty_text+=splitted_text[14].split(' ')[1][len(brokerage_text):]
            transaction_line.append(float(stamp_duty_text))        
        #read the security transaction tax (stt)
        security_transaction_tax_text = ''
        if splitted_text[11]!='0.0000':
            transaction_line.append(float(splitted_text[17]))
        else:
            security_transaction_tax_text+=splitted_text[16][len(stamp_duty_text):]
            transaction_line.append(float(security_tansaction_tax_text)) 
        #read the net payable/receivable
        net_payable_receivable_text=''
        if splitted_text[11]!='0.0000':
            net_payable_receivable_text+=splitted_text[19]
            transaction_line.append(float(splitted_text[19]))
        else:
            net_payable_receivable_text+=splitted_text[18][len(security_tansaction_tax_text):]
            transaction_line.append(float(net_payable_receivable_text))
        return transaction_line
    else:
        transact_line = anomaly_parser(text)
        return transact_line

def stock_transaction_report_reader(filename):
    transactions = transaction_splitter(process_text(read_pdf(filename)))
    transaction_list=[]
    for i in transactions:
        transaction_list.append(transaction_parser(i))
    fields = 'Transaction Type	Stock	Quantity	Value	Trade Price per Unit	Total Brokerage	Exchange Transaction Charges	SEBI Turnover Charges	Total Goods and Service Tax	Stamp Duty	Security Transaction Tax (STT)	Net Payable / Receivable'
    #import to csv using pandas
    transaction_df = pd.DataFrame(transaction_list, columns = fields.split('\t'))
    transaction_df.to_csv('Stock Transactions.csv',index=False)
    return transaction_df    

#testing the script to a pdf file
stock_transaction_report_reader('pdf.pdf')