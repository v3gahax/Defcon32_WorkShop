#!/usr/bin/env python

from boofuzz import *

csv_log = open('fuzz_results.csv', 'wb') ## create a csv file
my_logger = [FuzzLoggerCsv(file_handle=csv_log)] ### create a FuzzLoggerCSV object with the file handle of our csv file

def main():
    session = Session(
        target=Target(
            connection=SocketConnection("172.16.49.131", 2575, proto='tcp')),sleep_time = 2)
    fuzz_loggers=my_logger

    s_initialize("Request") 
    #start_block = '\x0b'
    #end_block = '\x1c'
    #carriage_return = '\r'
    #hl7_message = "MSH|^~\\&|GHH_ADT||||20080115153000||ADT^A01^ADT_A01|0123456789|P|2.5||||AL|\r" \
     #             "PID|1||566-554-3423^^^GHH^MR||EVERYMAN^ADAM^A||19800101|M|||2222 HOME STREET^^ANN ARBOR^MI^^USA||555-555-2004~444-333-222|||||Y|\r" \
      #            "NK1|1|NUCLEAR^NELDA^W|SPO|2222 HOME STREET^^ANN ARBOR^MI^^USA|\r" \
       #           "PV1|1|I|GHH PATIENT WARD|U||||^SENDER^SAM^^MD|^PUMP^PATRICK^P|CAR||||2|A0|\r" \
        #          "IN1|1|HCID-GL^GLOBAL|HCID-23432|HC PAYOR, INC.|5555 INSURERS CIRCLE^^ANN ARBOR^MI^99999^USA||||||||||||||||||||||||||||||||||||||||||||444-33-3333"
    s_string("MSH|^~\\&|GHH_ADT||||20080115153000||ADT^A01^ADT_A01|0123456789|P|2.5||||AL|\r", fuzzable=False)     
    s_string("PID|1||566-554-3423^^^GHH^MR||EVERYMAN^ADAM^A||19800101|M|||", fuzzable=False)
    s_string("2222 HOME STREET^^ANN ARBOR^MI^^USA||555-555-2004~444-333-222|||||Y|\r", fuzzable=True)
   
    
    session.connect(s_get("Request"))
    session.fuzz()

   
if __name__ == "__main__":
    main()
    
