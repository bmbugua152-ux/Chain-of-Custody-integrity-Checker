import hashlib
import logging
import json
import os
from datetime import datetime

logging.basicConfig(
    filename='forensic_audit.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
def main_menu():
    print("\n=== KENYA POLICE EVIDENCE INTEGRITY SYSTEM ===")
    print("1. Create new case")
    print("2. Load existing case")
    print("3. Register evidence")
    print("4. Verify evidence")
    print("5. Verify all evidence")
    print("6. Generate chain of custody report")
    print("7. List all evidence")
    print("8. Exit")
    return input("Select option: ")

class EvidenceIntegrityChecker:
    
    SEVERITY_LEVELS = {
        'critical': 'PRIMARY EVIDENCE - Tampering constitutes criminal offense',
        'high': 'SECONDARY EVIDENCE - Tampering invalidates case',
        'medium': 'SUPPORTING DOCUMENT - Changes must be documented',
        'low': 'REFERENCE FILE - Monitor for unauthorized changes'
    }
    
    def __init__(self, case_number, investigator):
        self.case_number = case_number
        self.investigator = investigator
        self.registry_file = f'case_{case_number}_registry.json'
        self.load_registry()
    
    def load_registry(self):
        # loads existing evidence registry or creates new one
        try:
            with open(self.registry_file, 'r') as f:
                self.registry = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.registry = {}
            logging.info(f"New case registry created - Case: {self.case_number}")
    
    def register_evidence(self, filepath, severity='high', description=''):
        # register a file as evidence and save its hash
        if not os.path.exists(filepath):
            print(f"ERROR: Evidence file not found - {filepath}")
            logging.error(f"Case {self.case_number} - Evidence file missing: {filepath}")
            return False
        
        if os.path.getsize(filepath) == 0:
            print(f"WARNING: Evidence file is empty - {filepath}")
            logging.warning(f"Case {self.case_number} - Empty evidence file: {filepath}")
            return False
        
        if severity not in self.SEVERITY_LEVELS:
            print(f"ERROR: Invalid severity level. Choose from: {list(self.SEVERITY_LEVELS.keys())}")
            return False
        
        with open(filepath, 'rb') as f:
            file_data = f.read()
        
        evidence_hash = hashlib.sha256(file_data).hexdigest()
        
        self.registry[filepath] = {
            'hash': evidence_hash,
            'severity': severity,
            'description': description,
            'registered_by': self.investigator,
            'registered_at': datetime.now().isoformat(),
            'case_number': self.case_number,
            'file_size': os.path.getsize(filepath)
        }
        
        with open(self.registry_file, 'w') as f:
            json.dump(self.registry, f, indent=4)
        
        print(f"Evidence registered: {filepath}")
        print(f"Severity: {severity.upper()} - {self.SEVERITY_LEVELS[severity]}")
        print(f"SHA256: {evidence_hash}")
        logging.info(f"Case {self.case_number} - Evidence registered: {filepath} by {self.investigator}")
        return True
    
    def verify_evidence(self, filepath):
        # verify a registered evidence file hasnt been tampered with
        if filepath not in self.registry:
            print(f"ERROR: {filepath} is not registered as evidence in Case {self.case_number}")
            logging.warning(f"Case {self.case_number} - Unregistered file check attempted: {filepath}")
            return False
        
        if not os.path.exists(filepath):
            print(f"CRITICAL ALERT: Evidence file MISSING - {filepath}")
            logging.critical(f"Case {self.case_number} - EVIDENCE FILE MISSING: {filepath}")
            return False
        
        if os.path.getsize(filepath) == 0:
            print(f"CRITICAL ALERT: Evidence file is now EMPTY - {filepath}")
            logging.critical(f"Case {self.case_number} - Evidence file emptied: {filepath}")
            return False
        
        with open(filepath, 'rb') as f:
            current_hash = hashlib.sha256(f.read()).hexdigest()
        
        registered = self.registry[filepath]
        
        if current_hash == registered['hash']:
            print(f"VERIFIED: {filepath} - Integrity confirmed")
            print(f"Originally registered by {registered['registered_by']} on {registered['registered_at']}")
            logging.info(f"Case {self.case_number} - Integrity verified: {filepath}")
            return True
        else:
            print(f"TAMPERING DETECTED: {filepath}")
            print(f"Severity: {registered['severity'].upper()}")
            print(f"Registered hash:  {registered['hash']}")
            print(f"Current hash:     {current_hash}")
            print(f"Original registration: {registered['registered_at']}")
            print(f"Registered by: {registered['registered_by']}")
            logging.critical(
                f"Case {self.case_number} - TAMPERING DETECTED: {filepath} "
                f"registered by {registered['registered_by']} on {registered['registered_at']}"
            )
            return False
    
    def generate_chain_of_custody(self):
        # generate a chain of custody report for all evidence
        print(f"\n{'='*60}")
        print(f"CHAIN OF CUSTODY REPORT")
        print(f"Case Number: {self.case_number}")
        print(f"Generated: {datetime.now().isoformat()}")
        print(f"{'='*60}")
        
        if not self.registry:
            print("No evidence registered for this case.")
            return
        
        for filepath, details in self.registry.items():
            print(f"\nFile: {filepath}")
            print(f"Description: {details.get('description', 'N/A')}")
            print(f"Severity: {details['severity'].upper()}")
            print(f"Registered by: {details['registered_by']}")
            print(f"Registered at: {details['registered_at']}")
            print(f"File size: {details['file_size']} bytes")
            print(f"SHA256: {details['hash']}")
            print(f"-"*40)
        
        logging.info(f"Chain of custody report generated for Case {self.case_number}")


if __name__ == "__main__":
    # run this once to create test files
    screenshots_for_exhibits = str()
    with open('exhibit_a_screenshot.png', 'wb') as f:
        f.write(b'fake screenshot content for testing')

    with open('suspect_communications.txt', 'w') as f:
        f.write('WhatsApp logs: suspect said meet at 9pm')
    # Example usage - Case simulation
    checker = EvidenceIntegrityChecker(
        case_number="NBI-2026-0042",
        investigator="B. Mbugua"
    )
    
    # Register evidence files
    checker.register_evidence(
        'exhibit_a_screenshot.png',
        severity='critical',
        description='Screenshot of fraudulent M-Pesa transaction'
    )
    
    checker.register_evidence(
        'suspect_communications.txt',
        severity='high', 
        description='WhatsApp message logs extracted from suspect device'
    )
    
    # Verify integrity
    checker.verify_evidence('exhibit_a_screenshot.png')
    checker.verify_evidence('suspect_communications.txt')
    
    # Generate report
    checker.generate_chain_of_custody()