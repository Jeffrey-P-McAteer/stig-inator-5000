
import os
import sys
import shutil
import json
import time
import datetime

# asd_stig_xml = '/j/downloads/U_ASD_V5R3_STIG/U_ASD_V5R3_Manual_STIG/U_ASD_STIG_V5R3_Manual-xccdf.xml'

is_debug_mode = 't' in os.environ.get('DEBUG', '') or '1' in os.environ.get('DEBUG', '')

tool_name = os.environ.get('TOOL_NAME', '')
while len(tool_name.strip()) < 1:
  tool_name = input('TOOL_NAME: ').strip()

poc_name = ''
try:
  import win32api
  import win32net
  user_info = win32net.NetUserGetInfo(win32net.NetGetAnyDCName(), win32api.GetUserName(), 2)
  poc_name = user_info['full_name']
except:
  pass

if len(os.environ.get('POC_NAME', '')) > 0:
  poc_name = os.environ.get('POC_NAME', poc_name)

while len(poc_name) < 1:
  poc_name = input('POC_NAME: ').strip()

if len(os.environ.get('POC_POSTFIX', '')) > 0:
  poc_name += ' '+os.environ.get('POC_POSTFIX', '')
else:
  print('WARNING: POC_POSTFIX is empty, you usually want a value like POC_POSTFIX="JP6" in there!')
  input('Press enter to continue')

poc_name += f" {datetime.datetime.today().strftime('%Y-%m-%d')}"

# valid 'status': values are ['open', 'not_a_finding', 'not_reviewed', 'not_applicable']

auto_stigs = [
  # Strict, we-can-repeat-DISA-language matches
  {
    'match': ['if the application does not utilize SAML assertions, this check is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that does not utilize SAML assertions.',
  },
  {
    'match': ['if the application does not utilize soap messages, this check is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that does not utilize SOAP messages.',
  },
  {
    'match': ['if the application does not utilize ws-security tokens, this check is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that does not utilize ws-security tokens.',
  },
  {
    'match': ['if the application does not utilize wss or saml assertions, this requirement is not applicable', 'if the application does not utilize saml assertions, this check is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that does not utilize wss or saml assertions.',
  },
  {
    'match': ['if there is no official requirement for shared or group application accounts, this requirement is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that has no official requirement for shared or group application accounts, nor does the desktop app manage accounts in any way.',
  },
  {
    'match': ['if official documentation exist that disallows the use of temporary user accounts within the application, this requirement is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that does not have user accounts. Because {tool_name} does not have user accounts, it implicitly disallows the use of temporary user accounts.',
  },
  {
    'match': ['if emergency accounts are not used, this requirement is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that that does not have user accounts. Because {tool_name} does not have user accounts, any emergency accounts cannot be used.',
  },
  {
    'match': ['if the application is configured to use an enterprise-based application user management capability that is stig compliant, the requirement is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that is configured to use an enterprise-based application user management capability that is stig compliant.',
  },
  {
    'match': ['if there are no data mining protections required, this requirement is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that has data mining protections required.',
  },
  {
    'match': ['if the application does not implement discretionary access controls, this requirement is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that does not implement discretionary access controls. (Or any other kind of access control for that matter, it is a desktop application and inherits the operating system\'s access control).',
  },
  {
    'match': ['if the user interface is only available via the os console, e.g., a fat client application installed on a gfe desktop or laptop, and that gfe is configured to display the dod banner, this requirement is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that is only available via the os console, e.g., a fat client application which is installed and deployed on a gfe desktop which is configured to display the dod banner.',
  },
  {
    'match': ['if the application is not publicly accessible, this requirement is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that is not publicly accessible.',
  },
  {
    'match': ['if the application documentation specifically states that non-repudiation services for application users are not defined as part of the application design, this requirement is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that has documentation which specifically states that non-repudiation services for application users are not defined as part of the application design.',
  },
  {
    'match': ['if the application does not provide log aggregation services, this requirement is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that not provide log aggregation services, though it may use a logger which aggregates multiple applications worth of logs into one dashboard.',
  },
  {
    'match': ['if a web-based application', 'this is not a finding'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} is a desktop application that is NOT a web-based application.',
  },
  {
    'match': ['if the application generates session id creation event logs by default, and that behavior cannot be disabled, this is not a finding'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} is a desktop application that generates session creation (aka application start-up) event logs by default and this behavior cannot be disabled.',
  },
  {
    'match': ['if the application requirements do not call for compartmentalized data and data protection, this requirement is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application whose requirements do not call for compartmentalized data and data protection as {tool_name} runs on an operating system which already provides this.',
  },
  {
    'match': ['if the application does not provide direct access to the system, this requirement is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that does not provide direct access to the system outside the existing access used to run the program.',
  },
  {
    'match': ['if the application design documentation indicates the application does not initiate connections to remote systems this requirement is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that does not initiate connections to remote systems.',
  },
  # {
  #   'match': ['if the application uses a database configured to use transaction sql logging this is not a finding'],
  #   'status': 'not_applicable',
  #   'comments': f'{tool_name} is a desktop application that does not use a database.',
  # },
  {
    'match': ['if the application is configured to log application event entries to a centralized, enterprise based logging solution that meets this requirement, the requirement is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that is configured to log application event entries to a centralized, enterprise based logging solution that meets this requirement',
  },
  {
    'match': ['if the application is configured to utilize a centralized logging solution, this requirement is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that is configured to utilize a centralized logging solution.',
  },
  {
    'match': ['if the application utilizes a centralized logging system that provides storage capacity alarming, this requirement is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that utilizes a centralized logging system that provides storage capacity alarming.',
  },
  {
    'match': ['if the application utilizes a centralized logging system that provides the real-time alarms, this requirement is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that utilizes a centralized logging system that provides the real-time alarms.',
  },
  {
    'match': ['if the application utilizes a centralized logging system that provides the audit processing failure alarms, this requirement is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that utilizes a centralized logging system that provides the audit processing failure alarms.',
  },
  {
    'match': ['if the application utilizes a centralized logging system that provides the capability to review the log files from one central location, this requirement is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that utilizes a centralized logging system that provides the capability to review the log files from one central location.',
  },
  {
    'match': ['if the application utilizes a centralized logging system that provides the capability to filter log events based upon the following events, this requirement is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that utilizes a centralized logging system that provides the capability to filter log events based on these events.',
  },
  {
    'match': ['if the application utilizes a centralized logging system that provides the capability to generate reports based on filtered log events, this requirement is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that utilizes a centralized logging system that provides the capability to generate reports based on filtered log events.',
  },
  {
    'match': ['if the application uses a centralized logging solution that performs the audit reduction (event filtering) functions, the requirement is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that uses a centralized logging solution that performs the audit reduction (event filtering) functions.',
  },
  {
    'match': ['if the application uses a centralized logging solution that provides immediate, customizable audit review and analysis functions, the requirement is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that uses a centralized logging solution that provides immediate, customizable audit review and analysis functions.',
  },
  {
    'match': ['if the application uses a centralized logging solution that provides immediate, customizable, ad-hoc report generation functions, the requirement is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that uses a centralized logging solution that provides immediate, customizable, ad-hoc report generation functions.',
  },
  {
    'match': ['if the application uses a centralized logging solution that performs the report generation functions, the requirement is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that uses a centralized logging solution that performs the report generation functions.',
  },
  {
    'match': ['if the application does not provide a report generation capability, the requirement is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that does not provide a report generation capability.',
  },
  {
    'match': ['if the application utilizes the underlying os system clock, and the system clock is mapped to utc or gmt, this is not a finding'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} is a desktop application that utilizes the underlying os system clock, and the system clock is mapped to utc.',
  },
  {
    'match': ['if the application utilizes the underlying os for time stamping and time synchronization when writing the audit logs, this requirement is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that utilizes the underlying os for time stamping and time synchronization when writing the audit logs.',
  },
  {
    'match': ['if the application does not provide a distinct audit tool oriented functionality that is a separate tool with an ability to view and manipulate log data, this requirement is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that does not provide a distinct audit tool oriented functionality that is a separate tool with an ability to view and manipulate log data.',
  },
  {
    'match': ['if the application does not include a built-in backup capability for backing up its own audit records, this requirement is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that does not include a built-in backup capability for backing up its own audit records.',
  },
  {
    'match': ['if the application is configured to utilize a centralized audit log solution that uses cryptographic methods that meet this requirement such as creating cryptographic hash values or message digests that can be used to validate integrity of audit files, the requirement is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that is configured to utilize a centralized audit log solution that uses cryptographic methods that meet this requirement.',
  },
  {
    'match': ['if the application does not provide a separate tool in the form of a file which provides an ability to view and manipulate application log data, query data, or generate reports, this requirement is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that does not provide a separate tool in the form of a file which provides an ability to view and manipulate application log data, query data, or generate reports.',
  },
  {
    'match': ['if a web-based application delegates session id creation to an application server, this is not a finding'],
    'status': 'not_a_finding', # not_a_finding
    'comments': f'{tool_name} is a desktop application that does not manage sessions. If an active directory domain login constitutes a session, this session is delegated to the active directory domain server.',
  },
  {
    'match': ['if the application generates audit logs by default when session ids are destroyed, and that behavior cannot be disabled, this is not a finding'],
    'status': 'not_a_finding', # not_a_finding
    'comments': f'{tool_name} is a desktop application that generates audit logs by default when closed and this behavior cannot be disabled. Audit logs appear in the list of opened + closed applications from operating system logs.',
  },
  {
    'match': ['if the system hosting the application has a separate file monitoring utility installed that is configured to identify changes to audit tools and alarm on changes to audit tools, this is not applicable'],
    'status': 'not_applicable', # not_a_finding
    'comments': f'{tool_name} is a desktop application that uses the underlying cyber file monitoring utilities to identify changes to system files and alarm on those changes.',
  },
  {
    'match': ['if the application does not provide a separate tool in the form of a file which provides an ability to view and manipulate application log data, query data or generate reports, this requirement is not applicable'],
    'status': 'not_applicable', # not_a_finding
    'comments': f'{tool_name} is a desktop application that does not provide a separate tool in the form of a file which provides an ability to view and manipulate application log data.',
  },
  {
    'match': ['if the application utilizes an approved repository of approved software that has been tested and approved for all application users to install, this is not a finding'],
    'status': 'not_a_finding', # not_a_finding
    'comments': f'{tool_name} is a desktop application that is only executed because it has been approved by JWAC and has been tested by JWAC for use on their systems. Any sub-components are accessed from either an approved network folder or an approved software artifact repository (Artifactory)',
  },
  {
    'match': ['if the policy, terms, or conditions state there are no usage restrictions, this requirement is not applicable'],
    'status': 'not_applicable', # not_a_finding
    'comments': f'{tool_name} is a desktop application that is developed for JWAC use and has no usage restrictions.',
  },
  {
    'match': ['if the application is not a configuration management or similar type of application designed to manage system processes and configurations, this requirement is not applicable'],
    'status': 'not_applicable', # not_a_finding
    'comments': f'{tool_name} is a desktop application that is not a configuration management or similar type of application designed to manage system processes and configurations.',
  },
  {
    'match': ['if the application does not use group or shared accounts, this requirement is not applicable'],
    'status': 'not_applicable', # not_a_finding
    'comments': f'{tool_name} is a desktop application that does not use group or shared accounts.',
  },
  {
    'match': ['if the application is designed to provide end-user, interactive application access only and does not use web services or allow connections from remote devices, this requirement is not applicable'],
    'status': 'not_applicable', # not_a_finding
    'comments': f'{tool_name} is a desktop application that is designed to provide end-user, interactive application access only and does not use web services or allow connections from remote devices.',
  },
  {
    'match': ['this requirement does not apply to individual application user accounts'],
    'status': 'not_applicable', # not_a_finding
    'comments': f'{tool_name} is a desktop application that is used by an individual application user account, therefore this requirement does not apply.',
  },
  {
    'match': ['if the application does not use passwords, the requirement is not applicable'],
    'status': 'not_applicable', # not_a_finding
    'comments': f'{tool_name} is a desktop application that does not use passwords.',
  },
  {
    'match': ['if the application does not perform code signing or other cryptographic tasks requiring a private key, this requirement is not applicable'],
    'status': 'not_applicable', # not_a_finding
    'comments': f'{tool_name} is a desktop application that does not perform code signing or other cryptographic tasks requiring a private key. Any cryptography that occurs (ie user cert authentication to remote servers) happens through the Microsoft System Trust Store and is not handled by {tool_name}.',
  },
  {
    'match': ['if the application does not provide authenticated access to a cryptographic module, the requirement is not applicable'],
    'status': 'not_applicable', # not_a_finding
    'comments': f'{tool_name} is a desktop application that does not provide authenticated access to a cryptographic module beyond what the host operating system has provided access to.',
  },
  {
    'match': ['if the application does not host non-organizational users, this requirement is not applicable'],
    'status': 'not_applicable', # not_a_finding
    'comments': f'{tool_name} is a desktop application that does not host non-organizational users.',
  },
  {
    'match': ['if the application is not intended to be available to federal government (non-dod) partners this requirement is not applicable'],
    'status': 'not_applicable', # not_a_finding
    'comments': f'{tool_name} is a desktop application that not intended to be available to federal government (non-dod) partners.',
  },
  {
    'match': ['if the application does not provide non-local maintenance and diagnostic capability, this requirement is not applicable'],
    'status': 'not_applicable', # not_a_finding
    'comments': f'{tool_name} is a desktop application that does not provide non-local maintenance and diagnostic capability.',
  },
  {
    'match': ['if the application administrator is prevented from accessing the os by policy requirement or separation of duties requirements, this is not a finding'],
    'status': 'not_a_finding', # not_a_finding
    'comments': f'{tool_name} is a desktop application that has no application administrators, and any administrators can only access the one system they are logged in to via a separate user account used for administration.',
  },
  {
    'match': ['if a documented acceptance of risk is provided, this is not a finding'],
    'status': 'not_a_finding', # not_a_finding
    'comments': f'{tool_name} is a desktop application that has a documented acceptance of risk is provided.',
  },
  {
    'match': ['ifREPLACEME'],
    'status': 'not_applicable', # not_a_finding
    'comments': f'{tool_name} is a desktop application that ',
  },
  {
    'match': ['ifREPLACEME'],
    'status': 'not_applicable', # not_a_finding
    'comments': f'{tool_name} is a desktop application that ',
  },
  {
    'match': ['ifREPLACEME'],
    'status': 'not_applicable', # not_a_finding
    'comments': f'{tool_name} is a desktop application that ',
  },
  {
    'match': ['ifREPLACEME'],
    'status': 'not_applicable', # not_a_finding
    'comments': f'{tool_name} is a desktop application that ',
  },
  
  # Fuzzy matches
  {
    'match': ['user', 'session'],
    # valid values are ['open', 'not_a_finding', 'not_reviewed', 'not_applicable']
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that does not manage user sessions.',
  },
  {
    'match': ['cryptography', 'encryption'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} is a desktop application that uses pre-approved Windows cryptography tools.',
  },
  {
    'match': ['exports', 'scrubbed'],
    'status': 'not_applicable',
    'comments': f'{tool_name} does not have exports.',
  },
  {
    'match': ['low', 'resource', 'alert'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} uses the already-existing Windows resource notifications to meet this rule.',
  },
  {
    'match': [' dos ', 'attack', 'prevent'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} is a desktop application, and the only DoS attack vectors are the user typing too quickly on their keyboard.',
  },
  {
    'match': ['activex', 'java applet', 'executed'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} does not download and execute any kind of remote code. Pre-existing local files and programs may be executed but these are not considered mobile code.',
  },
  {
    'match': ['password', 'change'],
    'status': 'not_applicable',
    'comments': f'{tool_name} does not perform any user account or session management because it is a desktop application.',
  },
  {
    'match': ['logout', 'session', 'ensure'],
    'status': 'not_applicable',
    'comments': f'{tool_name} does not perform any user account or session management because it is a desktop application.',
  },
  {
    'match': ['not disclose', 'unecessary', 'information'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} is a desktop application. It can only read or write data that a user already has been given access to by their operating system credentials.',
  },
  {
    'match': ['vulnerability', 'testing', 'performed'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} has been scanned with SonarQube and no critical vulnerabilities were found.',
  },
  {
    'match': ['defect', 'tracking', 'system'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} uses the GitLab issue tracker to track defects.',
  },
  {
    'match': ['code', 'coverage', 'statistics'],
    'status': 'not_a_finding',
    'comments': ' '.join([
        f'{tool_name} cannot be unit-tested in an automatic manner because it derives significant behavior from WPF graphics, buttons of which',
        'cannot be clicked automatically without breaking other cyber policies. The testing process in use is for end-users to perform testing and report defects.',
        'Coverage statistics are tracked at the tool level.'
    ]),
  },
  {
    'match': ['code', 'review', 'conducted'],
    'status': 'not_a_finding',
    'comments': f'Primary developers review {tool_name} code regularly to remove unecessary components, or update components with modern replacements.',
  },
  {
    'match': ['test', 'procedures', 'initialization', 'shutdown', 'aborts'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application and inherrits the initialization, shutdown, and abort behavior of a windows process.',
  },
  {
    'match': ['organization-defined', 'types', 'security', 'attributes', 'data as classified'],
    'status': 'not_a_finding',
    'comments': ' '.join([
        f'{tool_name} carries forward user-specified security attribute metadata in the same format as other data attributes.',
    ]),
  },
  {
    'match': ['SOAP message'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application and does not use SOAP authentication.',
  },
  {
    'match': ['not utilize WS-Security tokens, this check is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application and does not use WS-Security tokens.',
  },
  {
    'match': ['does not utilize WSS or SAML assertions, this requirement is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application and does not use WSS or SAML assertions.',
  },
  {
    'match': ['not utilize SAML assertions, this check is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application and does not use SAML assertions.',
  },
  {
    'match': ['audit', 'account', 'actions'],
    'status': 'not_applicable',
    'comments': ' '.join([
        f'{tool_name} is a desktop application and makes no access-control decisions.',
        f'If a user is restricted from performing a task without {tool_name}, then using {tool_name} will not allow them to perform the task because an access exception will be thrown and logged.',
    ]),
  },
  {
    'match': ['execute', 'without', 'excessive', 'account', 'permissions'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} is a desktop application and uses only the user\'s existing account permissions.',
  },
  {
    'match': ['audit', 'privileged', 'functions'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application does not have any privileged functions.',
  },
  {
    'match': ['review', 'audit', 'periodically'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} is a desktop application running on Windows. Windows operating system logs are reviewed by an operating system team periodically which meets this rule.',
  },
  {
    'match': ['separate', 'network', 'segment'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application and does not have components on different network segments.',
  },
  {
    'match': ['configuration', 'management', 'repository'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} uses the GitLab server to store code and configuration management data.',
  },
  {
    'match': ['backup', 'restoration', 'application'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} is backed up in GitLab.',
  },
  {
    'match': ['supported by', 'vendor', 'development team'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} is supported by the government developers who wrote it.',
  },
  {
    'match': ['application contains classified data'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} does not contain classified data.',
  },
  {
    'match': ['user guide', 'included', 'application'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} contains documentation embedded within the tool suitable for the purposes of a user guide.',
  },
  {
    'match': ['remote', 'access'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application and has no remote access or remote diagnostic or remote maitenence capabilities.',
  },
  {
    'match': ['audit', 'tools', 'audit data'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application and only creates audit events, it does not manage, maintain, modify, delete, or grant any access to the audit systems it sends events to.',
  },
  {
    'match': ['non-organizational users'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} is a desktop application and does not grant any kind of user access to anything. It also does not manage, create, delete, or audit any kind of user account data because it does not perform logon events.',
  },
  {
    'match': ['application', 'decommission'],
    'status': 'not_a_finding',
    'comments': f'The team maintaining {tool_name} will manually reach out to affected users during any decommissioning events.',
  },
  {
    'match': ['threat', 'models'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application, and it\'s threat models are the same as the Windows operating system\'s threat models.',
  },
  {
    'match': ['annual security training'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} developers and users have received organizationally-relevant security training before development even began.',
  },
  {
    'match': ['coding standards'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} developers use their department\'s coding standards for the languages used to build {tool_name}.',
  },
  {
    'match': ['application files', 'cryptographically hashed'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} developers build and deploy it in a single step, which means the integrity of the source code is the integrity of the application files. Source code integrity is maintained by GitLab.',
  },
  {
    'match': ['input', 'vulnerabilities'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} may only be used by one user at a time, so any inputs specified by the user will only ever affect their data which removed the possibility of any system-level vulnerability from being possible no matter how those inputs are utilized.',
  },
  {
    'match': ['certificate', 'authorities'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} is a desktop application and uses the Windows opersting system trust store, making no certificate-related decisions of its own.',
  },
  {
    'match': ['certificate', 'accepted trust anchor'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} is a desktop application and uses the Windows opersting system trust store, making no certificate-related decisions of its own.',
  },
  {
    'match': ['passwords'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} is a desktop application and does not manage, maintain, or use passwords.',
  },
  {
    'match': ['must', 'accept', 'credentials'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} is a desktop application and does not manage, maintain, or use credentials to grant access to itself. {tool_name} re-uses the existing Windows system to handle credentials, logon sessions, and access to data.',
  },
  {
    'match': ['publicly', 'accessible', 'application'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application and is not publicly accessible.',
  },
  {
    'match': ['user', 'accounts'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application and does not manage, create, delete, perform logon events, or in any other way manipulate user accounts of any kind.',
  },
  {
    'match': ['attempt', 'privileges occur'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application and does not manage, create, delete, or in any other way manipulate privileges of any kind.',
  },
  {
    'match': ['attempt', 'security levels'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application and does not manage, create, delete, or in any other way manipulate security levels of any kind.',
  },
  {
    'match': ['attempt', 'security objects'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application and does not manage, create, delete, or in any other way manipulate security objects of any kind.',
  },
  {
    'match': ['must record', 'username', 'event'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} logs the Windows SAM name of the user using the tool when all log messages are created and stored',
  },
  # Below is new stuff! 2024-06-17
  {
    'match': ['if the application does not provide log aggregation services, this requirement is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} does not provide log aggregation services.',
  },
  {
    'match': ['if the application utilizes a centralized logging system that provides the audit processing failure alarms, this requirement is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} utilizes a centralized logging system that provides the audit processing failure alarms (JWAC Logging Framework / JSMS).',
  },
  {
    'match': ['emergency accounts'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop app and has no account management, creation, logon, or any other account-based access capability.',
  },
  {
    'match': ['disable accounts'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop app and has no account management, creation, logon, or any other account-based access capability.',
  },
  {
    'match': ['data protection requirements'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} reads and writes files managed by the Windows operating system environment, which is responsible for protecting application data.',
  },
  {
    'match': ['data mining'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} does not specify protections for data mining because this does not affect a desktop application.',
  },
  {
    'match': ['flow of information', 'organization-defined'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} uses JWAC and customer-defined processes for handling information storage, retrieval, and transmission.',
  },
  {
    'match': ['logon'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop app and has no account management, creation, logon, or any other account-based access capability.',
  },
  {
    'match': ['non-repudiation services', 'not defined'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application and does not require non-repudiation services.',
  },
  {
    'match': ['system clocks', 'record', 'clock' ],
    'status': 'not_a_finding',
    'comments': f'{tool_name} uses the JWAC logging framework which uses the internal OS clock (specifically System.DateTime.Now) for recording timestamps, and system clock is mapped to UTC.',
  },
  {
    'match': ['record time stamps', 'degree of precision'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} records timestamps at the millisecond precision level.',
  },
  {
    'match': ['back up audit records', 'onto a different'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} uses the JWAC logging framework regularly backs up audit logs across the entire network for app applications using the framework.',
  },
  {
    'match': ['system failure', 'preserve', 'information necessary'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} appends global exceptions to any logs generated, including audit logs. These are sent to JWAC framework (which in turn goes to JSMS), and the long description contains exception text which identifies down to the line-of-source-code where something occurred.',
  },
  {
    'match': ['reveal error messages only to the ISSO'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} uses the JWAC logging framework which is responsible for managing who has access to what information. Because {tool_name} is a desktop application there are no security problems with any of the messages logged; at most detail they identify the user using the tool, name of sub-component being used, lines of code where faults occurred, and timestamps of events. No sensitive information is provided to end users because there is no sensitive information that is possible to log, as {tool_name} is a desktop app.',
  },
  {
    'match': ['verify correct operation of security functions'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} performs no security functions.',
  },
  {
    'match': ['The ISSO must ensure'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} runs on a JCCE network where the ISSO performs this task; the desktop application follows JWAC policy to ensure the ISSO has all the information necessary.',
  },
  {
    'match': ['log aggregation'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} uses the JWAC logging framework which aggregates logs according to a policy.',
  },
  {
    'match': ['event occurred'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} uses the JWAC logging framework which does this.',
  },
  {
    'match': ['logs are stored'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} uses the JWAC logging framework which does this.',
  },
  {
    'match': ['accesses to objects'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} logs user data access to JWAC logging framework.',
  },
  {
    'match': ['direct access to the'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} logs user data access to JWAC logging framework.',
  },
  {
    'match': ['events occurred'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} logs user data access to JWAC logging framework.',
  },
  {
    'match': ['include a unique identifier'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} uses unique data in each log entry.',
  },
  {
    'match': ['include an identifier'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} uses unique data in each log entry.',
  },
  {
    'match': ['transaction logging'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} logs user data access to JWAC logging framework.',
  },
  {
    'match': ['session auditing'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that does not manage user sessions. {tool_name} has no administration capability, and therefore no administration or maitenence sessions either.',
  },
  {
    'match': ['application shutdown events'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} is a desktop application, and shutdown events are handled according to the Windows policies already approved and in place.',
  },
  {
    'match': ['IP addresses'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that does not bind to IP addresses, nor does it open and listen to ports.',
  },
  {
    'match': ['ports'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that does not bind to IP addresses, nor does it open and listen to ports.',
  },
  {
    'match': ['logging architecture of the application'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} uses the JWAC logging framework.',
  },
  {
    'match': ['audit records'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} uses the JWAC logging framework.',
  },
  {
    'match': ['application logs'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} uses the JWAC logging framework.',
  },
  {
    'match': ['high impact', 'real-time alert', 'audit failure event'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} is not a high-impact tool and any audit failures will be contained to a single user\'s desk.',
  },
  {
    'match': ['configuration changes', 'access restrictions'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} has no system-level configuration that would present a security problem if modified by a user, and {tool_name} is also a desktop application with no administration capability.',
  },
  {
    'match': ['installation of patches'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is an in-house developed desktop application and has no capability to install patches, nor does the development team have any capability to generate patches for the application.',
  },
  {
    'match': ['file restrictions', 'do not', 'limit write', 'access', 'library files'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} is deployed in a folder with only developer write permissions.',
  },
  {
    'match': ['application must prevent program execution'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} is a desktop application and passes through the operating system\'s policy regarding application execution for the currently logged-in user operating the tool.',
  },
  {
    'match': ['execution of authorized software programs'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} is a desktop application and passes through the operating system\'s policy regarding application execution for the currently logged-in user operating the tool.',
  },
  {
    'match': ['disable non-essential capabilities'],
    'status': 'not_applicable',
    'comments': f'{tool_name} has no non-essential capabilities',
  },
  {
    'match': ['reauthenticate'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application and does not perform any authentication that is not managed by the operating system itself.',
  },
  {
    'match': ['authentication'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application and does not perform any authentication that is not managed by the operating system itself.',
  },
  {
    'match': ['verify', 'credentials'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application and does not perform any authentication that is not managed by the operating system itself.',
  },
  {
    'match': ['network connection'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} is a desktop application and follows the operating system\'s configuration for all network connection creation, management, authorization, and destruction.',
  },
  {
    'match': ['utilize', 'FIPS-validated', 'crypto'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} uses only the cryptographic libraries shipped by the Windows opersting system it runs on top of.',
  },
  {
    'match': ['if the application implements encryption'],
    'status': 'not_applicable',
    'comments': f'{tool_name} does not implement any encryption, key exchange, signature, or hashing functionality.',
  },
  {
    'match': ['SAML'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application and does not use WSS or SAML assertions.',
  },
  {
    'match': ['isolate security functions'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} has no security functions because it is a desktop application.',
  },
  {
    'match': ['separate', 'execution', 'domain'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} uses the pre-existing Windows sandbox for running executables which applies to all desktop applications on the system.',
  },
  {
    'match': ['prevent', 'unauthorized', 'information transfer', ],
    'status': 'not_a_finding',
    'comments': f'{tool_name} reads and writes only to files and these files are subject to the existing Windows security policies regarding where that person may read or write data to/from.',
  },
  {
    'match': ['denial', 'of', 'service'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} does not bind to network IPs or ports and thus cannot be used for any denial-of-service operations.',
  },
  {
    'match': ['web service'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application and has no web service capabilities.',
  },
  {
    'match': ['error messages', 'without revealing information'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} does not generate error messages that would allow exploitation of the tool via information disclosure.',
  },
  {
    'match': ['reveal', 'messages', 'only to', 'ISSO'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} uses the JWAC logging framework which performs this task.',
  },
  {
    'match': ['install'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is a desktop application that has no install or un-install capability. It is a stand-alone tool which is either loaded as a plug-in via another tool or executed directly by analysts without any installation.',
  },
  {
    'match': ['mobile code', 'not be used'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} does not download and execute mobile code.',
  },
  {
    'match': ['ensure', 'audit', 'retained'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} uses the JWAC logging framework which performs this.',
  },
  {
    'match': ['ISSO must report all suspected', 'IA poli'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} follows pre-existing JWAC policy.',
  },
  {
    'match': ['DoD STIG', 'available'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} has a STIG checklist available.',
  },
  {
    'match': ['continuity plan'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} uses the JWAC JP continuity plan for desktop applications.',
  },
  {
    'match': ['recovery is performed'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} uses existing JWAC backup systems for recovery operations.',
  },
  {
    'match': ['Back-up copies'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} uses existing JWAC backup systems for recovery operations.',
  },
  {
    'match': ['application does not implement key exchange, this check is not applicable'],
    'status': 'not_applicable',
    'comments': f'{tool_name} does not implement key exchange.',
  },
  {
    'match': ['tester must be designated', 'security flaws'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} has been tested for security flaws as part of JWAC acceptance criteria for application development.',
  },
  {
    'match': ['If IA impact analysis is not performed, this is a finding'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} has had information assurance impact analysis performed during planning of the tool\'s development.',
  },
  {
    'match': ['Security flaws', 'fix', 'plan'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} has security flaws fixed alongside reliability and performance flaws. This task is done by the original development team which then sends builds back out to users for testing.',
  },
  {
    'match': ['update the Design Document'],
    'status': 'not_a_finding',
    'comments': f'{tool_name}\'s Readme file contains the design information and is tracked and updated alongside the code for {tool_name}.',
  },
  {
    'match': ['administrator must be registered to receive update notifications'],
    'status': 'not_a_finding',
    'comments': f'The JWAC JP ISSO performs this role.',
  },
  {
    'match': ['update', 'patch', 'available'],
    'status': 'not_applicable',
    'comments': f'{tool_name} is an in-house developed desktop application and has no capability to install patches, nor does the development team have any capability to generate patches for the application.',
  },
]

print(f'Using TOOL_NAME = {tool_name}')
print(f'Using POC_NAME = {poc_name}')


test_checklist_file = '/j/downloads/TestChecklist.cklb'
if len(sys.argv) > 1:
  test_checklist_file = sys.argv[1]

print(f'Opening checklist file {test_checklist_file}')

test_checklist = None
with open(test_checklist_file, 'r', encoding='utf-8') as fd:
  test_checklist = json.load(fd)

stigs = test_checklist['stigs']
for i in range(0, len(stigs)):
  name = stigs[i]['display_name']
  print(f'========== {name} ==========')
  stig_rules = stigs[i]['rules']
  num_rules_stiginated = 0
  for j in range(0, len(stig_rules)):
    rule_name = stig_rules[j]['group_title']
    #print(f'Processing: {rule_name}')
    print('.', end='', flush=True)

    rule_text = ' '.join([
      stig_rules[j]['rule_title'].lower(),
      stig_rules[j]['group_title'].lower(),
      stig_rules[j]['check_content'].lower(),
      stig_rules[j]['discussion'].lower(),
    ])

    for auto_stig in auto_stigs:
      if all(needle.lower() in rule_text for needle in auto_stig['match']):
        # This rule is known to be trivial!
        num_rules_stiginated += 1
        stig_rules[j]['finding_details'] = auto_stig['comments']
        stig_rules[j]['status'] = auto_stig['status']
        # Minor fixup from our internal rules
        if stig_rules[j]['status'].strip() == 'not_applicable' and not ('is not applicable' in rule_text):
          # We say it's "not a finding"
          stig_rules[j]['status'] = 'not_a_finding'

        if is_debug_mode:
          matches = ', '.join(auto_stig['match'])
          stig_rules[j]['comments'] = f'Matched "{matches}"'
        else:
          if len(stig_rules[j]['comments']) < 3 or stig_rules[j]['comments'].strip().startswith('Matched "') or stig_rules[j]['comments'].strip().startswith('POC:'):
            stig_rules[j]['comments'] = f'POC: {poc_name}'
        break

  num_open_rules = 0
  num_not_reviewed_rules = 0
  for j in range(0, len(stig_rules)):
    if stig_rules[j]['status'].lower() == 'not_reviewed' or len(stig_rules[j]['status']) < 2:
      num_not_reviewed_rules += 1
    elif stig_rules[j]['status'].lower() == 'open':
      num_open_rules += 1
  percent_complete = (len(stig_rules) - (num_open_rules + num_not_reviewed_rules)) / max(1, len(stig_rules))
  percent_complete *= 100.0
  percent_complete = round(percent_complete, 1)

  stigs[i]['rules'] = stig_rules
  print()
  print(f'{num_rules_stiginated} of {len(stig_rules)} rules matched trivial groups and were automatically filled with the group data.')
  print(f'{num_open_rules} are open, {num_not_reviewed_rules} are not reviewed of {len(stig_rules)} rules')
  print(f'{percent_complete}% complete')
  print()

test_checklist['stigs'] = stigs

output_test_checklist_file = test_checklist_file #+'.auto.cklb'
with open(output_test_checklist_file, 'w', encoding='utf-8') as fd:
  json.dump(test_checklist, fd)
print(f'Wrote to {output_test_checklist_file}')

