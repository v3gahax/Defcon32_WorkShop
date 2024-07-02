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
        logging.info(f"Raw HL7 Message: {raw_message}")
        message = parse_message(raw_message, find_groups=False)

        # Log all segments and their fields
        for segment in message.children:
            logging.info(f"Segment: {segment.name}")
            for field in segment.children:
                logging.info(f"  Field {field.name}: {field.to_er7() if field.to_er7() else field.value}")

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
        death_indicator = pid_segment.pid_30.value if pid_segment.pid_30 else "N/A"

        logging.info(f"Patient Information: ID: {patient_id}, Name: {patient_name}, DOB: {date_of_birth}, Gender: {gender}, Death Indicator: {death_indicator}")
        print(f"Death Indicator (PID-30): {death_indicator}")

        if death_indicator.strip().upper() == 'Y':
            logging.info("Patient is deceased.")
        else:
            logging.info("Patient is alive.")

        # Log insurance information if available
        insurance_segments = [seg for seg in message.children if seg.name == 'IN1']
        if insurance_segments:
            logging.info("Insurance Information:")
            for insurance_segment in insurance_segments:
                insurer_name = insurance_segment.in1_4.value if insurance_segment.in1_4 else "N/A"
                policy_number = insurance_segment.in1_2.value if insurance_segment.in1_2 else "N/A"
                logging.info(f"Insurer: {insurer_name}, Policy Number: {policy_number}")

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

