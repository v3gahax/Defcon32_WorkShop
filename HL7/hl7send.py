import socket
from hl7apy.parser import parse_message

# Define the HL7 message
hl7_message = 
"""MSH|^~\&|EPIC|EPICADT|iFW|SMSADT|199912271408|CHARRIS|ADT^A04|1817457|D|2.5|
PID||0493575^^^2^ID 1|454721||DOE^JOHN^^^^|DOE^JOHN^^^^|19480203|M||B|254 
MYSTREET 
AVE^^MYTOWN^OH^44123^USA||(216)123-4567|||M|NON|400003403~1129086|
NK1||ROE^MARIE^^^^|SPO||(216)123-4567||EC|||||||||||||||||||||||||||
PV1||O|168 ~219~C~PMA^^^^^^^^^||||277^ALLEN 
MYLASTNAME^BONNIE^^^^|||||||||| 
||2688684|||||||||||||||||||||||||199912271408||||||002376853"""

# Parse the HL7 message to ensure it is correctly formatted
parsed_message = parse_message(hl7_message)

# Convert the parsed message back to a string
hl7_message_str = parsed_message.to_er7()

# Define the remote HL7 server details
hl7_server_host = 'hl7.server.address'
hl7_server_port = 12345

# Create a socket object
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to the HL7 server
    sock.connect((hl7_server_host, hl7_server_port))
    
    # Add start block and end block characters to the HL7 message
    hl7_message_str_with_wrappers = f"\x0b{hl7_message_str}\x1c\x0d"

    # Send the HL7 message
    sock.sendall(hl7_message_str_with_wrappers.encode('utf-8'))
    
    # Receive the response from the server
    response = sock.recv(4096).decode('utf-8')
    print("Received response from the server:", response)
    
finally:
    # Close the socket connection
    sock.close()

