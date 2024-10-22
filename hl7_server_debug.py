import socket
from hl7apy.parser import parse_message
from hl7apy.exceptions import HL7apyException

def handle_message(raw_message):
    """
    Process the incoming raw HL7 message and print patient information and 
insurance details if available.
    """
    try:
        message = parse_message(raw_message, find_groups=False)

        # Find PID segment
        pid_segments = [seg for seg in message.children if seg.name == 
'PID']
        if not pid_segments:
            print("PID segment not found in message.")
            return

        pid_segment = pid_segments[0]

        # Access fields correctly
        patient_id = pid_segment.pid_3[0].cx_1.value if pid_segment.pid_3 
and len(pid_segment.pid_3) > 0 and pid_segment.pid_3[0].cx_1 else "N/A"
        patient_name = f"{pid_segment.pid_5[0].xpn_1.value} 
{pid_segment.pid_5[0].xpn_2.value}" if pid_segment.pid_5 and 
len(pid_segment.pid_5) > 0 and pid_segment.pid_5[0].xpn_1 and 
pid_segment.pid_5[0].xpn_2 else "N/A"
        date_of_birth = pid_segment.pid_7.value if pid_segment.pid_7 else 
"N/A"
        gender = pid_segment.pid_8.value if pid_segment.pid_8 else "N/A"
        death_indicator = pid_segment.pid_30.value if pid_segment.pid_30 
else "N/A"

        print("Patient Information:")
        print(f"ID: {patient_id}")
        print(f"Name: {patient_name}")
        print(f"Date of Birth: {date_of_birth}")
        print(f"Gender: {gender}")
        print(f"Death Indicator: {death_indicator}")  # Debugging 
statement

        if death_indicator == 'Y':
            print("Patient is dead.")
        else:
            print("Patient is alive.")

        # Print insurance information if available
        insurance_segments = [seg for seg in message.children if seg.name 
== 'IN1']
        if insurance_segments:
            print("\nInsurance Information:")
            for insurance_segment in insurance_segments:
                insurer_name = insurance_segment.in1_3.value if 
insurance_segment.in1_3 else "N/A"
                policy_number = insurance_segment.in1_2.value if 
insurance_segment.in1_2 else "N/A"
                print(f"Insurer: {insurer_name}")
                print(f"Policy Number: {policy_number}")

    except HL7apyException as e:
        print(f"Failed to process message due to HL7apyException: {e}")
    except Exception as e:
        print(f"Failed to process message due to an unexpected error: 
{e}")



def start_server(port=2575):
    """
    Start an HL7 listener server on the specified port.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as 
server_socket:
        server_socket.bind(('', port))
        server_socket.listen(1)
        print(f"Listening for HL7 messages on port {port}...")

        while True:
            conn, addr = server_socket.accept()
            with conn:
                print(f"Connected by {addr}")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    raw_message = data.decode('utf-8').strip('\x0b\x1c\r')
                    handle_message(raw_message)

if __name__ == "__main__":
    start_server() 
