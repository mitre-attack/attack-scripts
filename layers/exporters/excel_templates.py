import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill

def BadTemplateException(exception):
    pass

class excel_templates:
    enterprise_template = {(1, 1): 'Initial Access',
                    (1, 2): 'Execution',
                    (1, 3): 'Persistence',
                    (1, 4): 'Privilege Escalation',
                    (1, 5): 'Defense Evasion',
                    (1, 6): 'Credential Access',
                    (1, 7): None,
                    (1, 8): 'Discovery',
                    (1, 9): 'Lateral Movement',
                    (1, 10): 'Collection',
                    (1, 11): 'Command and Control',
                    (1, 12): 'Exfiltration',
                    (1, 13): 'Impact',
                    (2, 1): 'Drive-by Compromise',
                    (2, 2): 'Command and Scripting Interpreter',
                    (2, 3): 'Account Manipulation',
                    (2, 4): 'Abuse Elevation Control Mechanism',
                    (2, 5): 'Abuse Elevation Control Mechanism',
                    (2, 6): 'Brute Force',
                    (2, 7): 'Credential Stuffing',
                    (2, 8): 'Account Discovery',
                    (2, 9): 'Exploitation of Remote Services',
                    (2, 10): 'Archive Collected Data',
                    (2, 11): 'Application Layer Protocol',
                    (2, 12): 'Automated Exfiltration',
                    (2, 13): 'Account Access Removal',
                    (3, 1): 'Exploit Public-Facing Application',
                    (3, 2): 'Exploitation for Client Execution',
                    (3, 3): 'BITS Jobs',
                    (3, 4): 'Access Token Manipulation',
                    (3, 5): 'BITS Jobs',
                    (3, 6): None,
                    (3, 7): 'Password Cracking',
                    (3, 8): 'Application Window Discovery',
                    (3, 9): 'Internal Spearphishing',
                    (3, 10): 'Audio Capture',
                    (3, 11): 'Communication Through Removable Media',
                    (3, 12): 'Data Transfer Size Limits',
                    (3, 13): 'Data Destruction',
                    (4, 1): 'External Remote Services',
                    (4, 2): 'Inter-Process Communication',
                    (4, 3): 'Boot or Logon Autostart Execution',
                    (4, 4): 'Boot or Logon Autostart Execution',
                    (4, 5): 'Deobfuscate/Decode Files or Information',
                    (4, 6): None,
                    (4, 7): 'Password Guessing',
                    (4, 8): 'Browser Bookmark Discovery',
                    (4, 9): 'Lateral Tool Transfer',
                    (4, 10): 'Automated Collection',
                    (4, 11): 'Data Encoding',
                    (4, 12): 'Exfiltration Over Alternative Protocol',
                    (4, 13): 'Data Encrypted for Impact',
                    (5, 1): 'Hardware Additions',
                    (5, 2): 'Native API',
                    (5, 3): 'Boot or Logon Initialization Scripts',
                    (5, 4): 'Boot or Logon Initialization Scripts',
                    (5, 5): 'Direct Volume Access',
                    (5, 6): None,
                    (5, 7): 'Password Spraying',
                    (5, 8): 'Domain Trust Discovery',
                    (5, 9): 'Remote Service Session Hijacking',
                    (5, 10): 'Clipboard Data',
                    (5, 11): 'Data Obfuscation',
                    (5, 12): 'Exfiltration Over C2 Channel',
                    (5, 13): 'Data Manipulation',
                    (6, 1): 'Phishing',
                    (6, 2): 'Scheduled Task/Job',
                    (6, 3): 'Browser Extensions',
                    (6, 4): 'Create or Modify System Process',
                    (6, 5): 'Execution Guardrails',
                    (6, 6): 'Credentials from Password Stores',
                    (6, 8): 'File and Directory Discovery',
                    (6, 9): 'Remote Services',
                    (6, 10): 'Data from Information Repositories',
                    (6, 11): 'Dynamic Resolution',
                    (6, 12): 'Exfiltration Over Other Network Medium',
                    (6, 13): 'Defacement',
                    (7, 1): 'Replication Through Removable Media',
                    (7, 2): 'Shared Modules',
                    (7, 3): 'Compromise Client Software Binary',
                    (7, 4): 'Event Triggered Execution',
                    (7, 5): 'Exploitation for Defense Evasion',
                    (7, 6): 'Exploitation for Credential Access',
                    (7, 8): 'Network Service Scanning',
                    (7, 9): 'Replication Through Removable Media',
                    (7, 10): 'Data from Local System',
                    (7, 11): 'Encrypted Channel',
                    (7, 12): 'Exfiltration Over Physical Medium',
                    (7, 13): 'Disk Wipe',
                    (8, 1): 'Supply Chain Compromise',
                    (8, 2): 'Software Deployment Tools',
                    (8, 3): 'Create Account',
                    (8, 4): 'Exploitation for Privilege Escalation',
                    (8, 5): 'File and Directory Permissions Modification',
                    (8, 6): 'Forced Authentication',
                    (8, 8): 'Network Share Discovery',
                    (8, 9): 'Software Deployment Tools',
                    (8, 10): 'Data from Network Shared Drive',
                    (8, 11): 'Fallback Channels',
                    (8, 12): 'Exfiltration Over Web Service',
                    (8, 13): 'Endpoint Denial of Service',
                    (9, 1): 'Trusted Relationship',
                    (9, 2): 'System Services',
                    (9, 3): 'Create or Modify System Process',
                    (9, 4): 'Group Policy Modification',
                    (9, 5): 'Group Policy Modification',
                    (9, 6): 'Input Capture',
                    (9, 8): 'Network Sniffing',
                    (9, 9): 'Taint Shared Content',
                    (9, 10): 'Data from Removable Media',
                    (9, 11): 'Ingress Tool Transfer',
                    (9, 12): 'Scheduled Transfer',
                    (9, 13): 'Firmware Corruption',
                    (10, 1): 'Valid Accounts',
                    (10, 2): 'User Execution',
                    (10, 3): 'Event Triggered Execution',
                    (10, 4): 'Hijack Execution Flow',
                    (10, 5): 'Hide Artifacts',
                    (10, 6): 'Man-in-the-Middle',
                    (10, 8): 'Password Policy Discovery',
                    (10, 9): 'Use Alternate Authentication Material',
                    (10, 10): 'Data Staged',
                    (10, 11): 'Multi-Stage Channels',
                    (10, 13): 'Inhibit System Recovery',
                    (11, 2): 'Windows Management Instrumentation',
                    (11, 3): 'External Remote Services',
                    (11, 4): 'Process Injection',
                    (11, 5): 'Hijack Execution Flow',
                    (11, 6): 'Modify Authentication Process',
                    (11, 8): 'Peripheral Device Discovery',
                    (11, 10): 'Email Collection',
                    (11, 11): 'Non-Application Layer Protocol',
                    (11, 13): 'Network Denial of Service',
                    (12, 3): 'Hijack Execution Flow',
                    (12, 4): 'Scheduled Task/Job',
                    (12, 5): 'Impair Defenses',
                    (12, 6): 'Network Sniffing',
                    (12, 8): 'Permission Groups Discovery',
                    (12, 10): 'Input Capture',
                    (12, 11): 'Non-Standard Port',
                    (12, 13): 'Resource Hijacking',
                    (13, 3): 'Office Application Startup',
                    (13, 4): 'Valid Accounts',
                    (13, 5): 'Indicator Removal on Host',
                    (13, 6): 'OS Credential Dumping',
                    (13, 8): 'Process Discovery',
                    (13, 10): 'Man in the Browser',
                    (13, 11): 'Protocol Tunneling',
                    (13, 13): 'Service Stop',
                    (14, 3): 'Pre-OS Boot',
                    (14, 5): 'Indirect Command Execution',
                    (14, 6): 'Steal or Forge Kerberos Tickets',
                    (14, 8): 'Query Registry',
                    (14, 10): 'Man-in-the-Middle',
                    (14, 11): 'Proxy',
                    (14, 13): 'System Shutdown/Reboot',
                    (15, 3): 'Scheduled Task/Job',
                    (15, 5): 'Masquerading',
                    (15, 6): 'Steal Web Session Cookie',
                    (15, 8): 'Remote System Discovery',
                    (15, 10): 'Screen Capture',
                    (15, 11): 'Remote Access Software',
                    (16, 3): 'Server Software Component',
                    (16, 5): 'Modify Authentication Process',
                    (16, 6): 'Two-Factor Authentication Interception',
                    (16, 8): 'Software Discovery',
                    (16, 10): 'Video Capture',
                    (16, 11): 'Traffic Signaling',
                    (17, 3): 'Traffic Signaling',
                    (17, 5): 'Modify Registry',
                    (17, 6): 'Unsecured Credentials',
                    (17, 8): 'System Information Discovery',
                    (17, 11): 'Web Service',
                    (18, 3): 'Valid Accounts',
                    (18, 5): 'Obfuscated Files or Information',
                    (18, 8): 'System Network Configuration Discovery',
                    (19, 5): 'Pre-OS Boot',
                    (19, 8): 'System Network Connections Discovery',
                    (20, 5): 'Process Injection',
                    (20, 8): 'System Owner/User Discovery',
                    (21, 5): 'Rogue Domain Controller',
                    (21, 8): 'System Service Discovery',
                    (22, 5): 'Rootkit',
                    (22, 8): 'System Time Discovery',
                    (23, 5): 'Signed Binary Proxy Execution',
                    (24, 5): 'Signed Script Proxy Execution',
                    (25, 5): 'Subvert Trust Controls',
                    (26, 5): 'Template Injection',
                    (27, 5): 'Traffic Signaling',
                    (28, 5): 'Trusted Developer Utilities Proxy Execution',
                    (29, 5): 'Use Alternate Authentication Material',
                    (30, 5): 'Valid Accounts',
                    (31, 5): 'Virtualization/Sandbox Evasion',
                    (32, 5): 'XSL Script Processing',
                    (33, 5): 'Access Token Manipulation'}
    mobile_template = {(1, 1): 'Initial Access',
                       (1, 2): 'Execution',
                       (1, 3): 'Persistence',
                       (1, 4): 'Privilege Escalation',
                       (1, 5): 'Defense Evasion',
                       (1, 6): 'Credential Access',
                       (1, 7): 'Discovery',
                       (1, 8): 'Lateral Movement',
                       (1, 9): 'Collection',
                       (1, 10): 'Command and Control',
                       (1, 11): 'Exfiltration',
                       (1, 12): 'Impact',
                       (2, 1): 'Deliver Malicious App via Authorized App Store',
                       (2, 2): 'Broadcast Receivers',
                       (2, 3): 'Abuse Device Administrator Access to Prevent Removal',
                       (2, 4): 'Code Injection',
                       (2, 5): 'Application Discovery',
                       (2, 6): 'Access Notifications',
                       (2, 7): 'Application Discovery',
                       (2, 8): 'Attack PC via USB Connection',
                       (2, 9): 'Access Calendar Entries',
                       (2, 10): 'Alternate Network Mediums',
                       (2, 11): 'Alternate Network Mediums',
                       (2, 12): 'Carrier Billing Fraud',
                       (3, 1): 'Deliver Malicious App via Other Means',
                       (3, 2): 'Native Code',
                       (3, 3): 'Broadcast Receivers',
                       (3, 4): 'Exploit OS Vulnerability',
                       (3, 5): 'Code Injection',
                       (3, 6): 'Access Sensitive Data in Device Logs',
                       (3, 7): 'Evade Analysis Environment',
                       (3, 8): 'Exploit Enterprise Resources',
                       (3, 9): 'Access Call Log',
                       (3, 10): 'Commonly Used Port',
                       (3, 11): 'Commonly Used Port',
                       (3, 12): 'Clipboard Modification',
                       (4, 1): 'Drive-by Compromise',
                       (4, 3): 'Code Injection',
                       (4, 4): 'Exploit TEE Vulnerability',
                       (4, 5): 'Device Lockout',
                       (4, 6): 'Access Stored Application Data',
                       (4, 7): 'File and Directory Discovery',
                       (4, 9): 'Access Contact List',
                       (4, 10): 'Domain Generation Algorithms',
                       (4, 11): 'Data Encrypted',
                       (4, 12): 'Data Encrypted for Impact',
                       (5, 1): 'Exploit via Charging Station or PC',
                       (5, 3): 'Compromise Application Executable',
                       (5, 5): 'Disguise Root/Jailbreak Indicators',
                       (5, 6): 'Android Intent Hijacking',
                       (5, 7): 'Location Tracking',
                       (5, 9): 'Access Notifications',
                       (5, 10): 'Remote File Copy',
                       (5, 11): 'Standard Application Layer Protocol',
                       (5, 12): 'Delete Device Data',
                       (6, 1): 'Exploit via Radio Interfaces',
                       (6, 3): 'Foreground Persistence',
                       (6, 5): 'Download New Code at Runtime',
                       (6, 6): 'Capture Clipboard Data',
                       (6, 7): 'Network Service Scanning',
                       (6, 9): 'Access Sensitive Data in Device Logs',
                       (6, 10): 'Standard Application Layer Protocol',
                       (6, 12): 'Device Lockout',
                       (7, 1): 'Install Insecure or Malicious Configuration',
                       (7, 3): 'Modify Cached Executable Code',
                       (7, 5): 'Evade Analysis Environment',
                       (7, 6): 'Capture SMS Messages',
                       (7, 7): 'Process Discovery',
                       (7, 9): 'Access Stored Application Data',
                       (7, 10): 'Standard Cryptographic Protocol',
                       (7, 12): 'Generate Fraudulent Advertising Revenue',
                       (8, 1): 'Lockscreen Bypass',
                       (8, 3): 'Modify OS Kernel or Boot Partition',
                       (8, 5): 'Input Injection',
                       (8, 6): 'Exploit TEE Vulnerability',
                       (8, 7): 'System Information Discovery',
                       (8, 9): 'Capture Audio',
                       (8, 10): 'Uncommonly Used Port',
                       (8, 12): 'Input Injection',
                       (9, 1): 'Masquerade as Legitimate Application',
                       (9, 3): 'Modify System Partition',
                       (9, 5): 'Install Insecure or Malicious Configuration',
                       (9, 6): 'Input Capture',
                       (9, 7): 'System Network Configuration Discovery',
                       (9, 9): 'Capture Camera',
                       (9, 10): 'Web Service',
                       (9, 12): 'Manipulate App Store Rankings or Ratings',
                       (10, 1): 'Supply Chain Compromise',
                       (10, 3): 'Modify Trusted Execution Environment',
                       (10, 5): 'Kill Switch',
                       (10, 6): 'Input Prompt',
                       (10, 7): 'System Network Connections Discovery',
                       (10, 9): 'Capture Clipboard Data',
                       (10, 12): 'Modify System Partition',
                       (11, 5): 'Masquerade as Legitimate Application',
                       (11, 6): 'Network Traffic Capture or Redirection',
                       (11, 9): 'Capture SMS Messages',
                       (12, 5): 'Modify OS Kernel or Boot Partition',
                       (12, 6): 'URL Scheme Hijacking',
                       (12, 9): 'Data from Local System',
                       (13, 5): 'Modify System Partition',
                       (13, 9): 'Foreground Persistence',
                       (14, 5): 'Modify Trusted Execution Environment',
                       (14, 9): 'Input Capture',
                       (15, 5): 'Native Code',
                       (15, 9): 'Location Tracking',
                       (16, 5): 'Obfuscated Files or Information',
                       (16, 9): 'Network Information Discovery',
                       (17, 5): 'Suppress Application Icon',
                       (17, 9): 'Network Traffic Capture or Redirection',
                       (18, 9): 'Screen Capture'}

    def __init__(self, mode='enterprise'):
        if mode in ['enterprise', 'mobile']:
            self.mode = mode
        else:
            raise BadTemplateException

    def _build_raw(self):
        template = self.mobile_template
        if self.mode == 'enterprise':
            template = self.enterprise_template
        wb = openpyxl.Workbook()

        sheet = wb.active

        header_template_f = Font(name='Calibri', bold=True)
        header_template_a = Alignment(horizontal='center', vertical='bottom')
        header_template_b = Border(bottom=Side(border_style='thin'))
        header_template_c = PatternFill(patternType='solid', start_color='DDDDDD', end_color='DDDDDD')

        for entry in template:
            c = sheet.cell(row=entry[0], column=entry[1])
            c.value = template[entry]
            if entry[0] == 1:
                c.font = header_template_f
                c.alignment = header_template_a
                c.border = header_template_b
                c.fill = header_template_c

        ## patch widths
        dims = {}
        sheet_handle = wb.active
        for row in sheet_handle:
            for cell in row:
                if cell.value:
                    dims[cell.column_letter] = max((dims.get(cell.column_letter, 0), len(str(cell.value))))
        for col, value in dims.items():
            sheet_handle.column_dimensions[col].width = value
        return wb


    def export(self):
        wb = self._build_raw()
        if self.mode == 'enterprise':
            sheet_handle = wb.active
            sheet_handle.merge_cells('F2:F5')

            adjust = sheet_handle.cell(row=2, column=6)
            adjust.alignment = Alignment(vertical='top')
            return wb
        else:
            return wb