import socket
import logging
import argparse
from hl7apy.parser import parse_message
from hl7apy.exceptions import HL7apyException

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def handle_message(raw_message):
    """
    Process the incoming raw HL7 message, extract patient information including the death indicator, and log details.
    """
    try:
        message = parse_message(raw_message, find_groups=False)

        # Find PID segment
        pid_segments = [seg for seg in message.children if seg.name == 'PID']
        if not pid_segments:
            logging.warning("PID segment not found in message.")
            return

        pid_segment = pid_segments[0]

        # Extract and log patient information
        patient_id = pid_segment.pid_3[0].cx_1.value if pid_segment.pid_3 and len(pid_segment.pid_3) > 0 else "N/A"
        patient_name = f"{pid_segment.pid_5[0].xpn_1.value} {pid_segment.pid_5[0].xpn_2.value}" if pid_segment.pid_5 and len(pid_segment.pid_5) > 0 else "N/A"
        date_of_birth = pid_segment.pid_7.value if pid_segment.pid_7 else "N/A"
        gender = pid_segment.pid_8.value if pid_segment.pid_8 else "N/A"
        address = pid_segment.pid_11[0].xad_1.value if pid_segment.pid_11 and len(pid_segment.pid_11) > 0 else "N/A"
        phone_numbers = [phone.xtn_1.value for phone in pid_segment.pid_13] if pid_segment.pid_13 else ["N/A"]
        ssn = pid_segment.pid_19.value if pid_segment.pid_19 else "N/A"
        death_indicator = pid_segment.pid_30.value if pid_segment.pid_30 else "N/A"

        logging.info(f"Patient Information: ID: {patient_id}, Name: {patient_name}, DOB: {date_of_birth}, Gender: {gender}, Address: {address}, Phone Numbers: {phone_numbers}, SSN: {ssn}, Death Indicator: {death_indicator}")

        if death_indicator.strip().upper() == 'Y':
            logging.info("OMFG you killed the patient!!!!")
        else:
            logging.info("Patient is alive.")

        # Find IN1 segments for insurance information
        insurance_segments = [seg for seg in message.children if seg.name == 'IN1']
        if insurance_segments:
            for insurance_segment in insurance_segments:
                insurer_name = insurance_segment.in1_4.value if insurance_segment.in1_4 else "N/A"
                policy_number = insurance_segment.in1_2.value if insurance_segment.in1_2 else "N/A"
                logging.info(f"Insurance Information: Insurer: {insurer_name}, Policy Number: {policy_number}")

    except HL7apyException as e:
        logging.error(f"Failed to process message due to HL7apyException: {e}")
    except Exception as e:
        logging.error(f"Failed to process message due to an unexpected error: {e}")

def start_server(port):
    """
    Start an HL7 listener server on the specified port.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(('', port))
        server_socket.listen(1)
        logging.info(f"Listening for HL7 messages on port {port}...")

        while True:
            conn, addr = server_socket.accept()
            with conn:
                logging.info(f"Connected by {addr}")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    raw_message = data.decode('utf-8').strip('\x0b\x1c\r')
                    handle_message(raw_message)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start an HL7 listener server.')
    parser.add_argument('--port', type=int, default=2575, help='Port to listen on (default: 2575)')
    args = parser.parse_args()
    start_server(args.port)

