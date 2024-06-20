
import os
import sys
import shutil
import json

# asd_stig_xml = '/j/downloads/U_ASD_V5R3_STIG/U_ASD_V5R3_Manual_STIG/U_ASD_STIG_V5R3_Manual-xccdf.xml'

is_debug_mode = 't' in os.environ.get('DEBUG', '') or '1' in os.environ.get('DEBUG', '')

tool_name = os.environ.get('TOOL_NAME', 'The tool')
poc_name = ''
try:
  import win32api
  import win32net
  user_info = win32net.NetUserGetInfo(win32net.NetGetAnyDCName(), win32api.GetUserName(), 2)
  poc_name = user_info['full_name']
except:
  pass
poc_name = os.environ.get('POC_NAME', poc_name)


auto_stigs = [
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
        'If a user is restricted from performing a task without {tool_name}, then using {tool_name} will not allow them to perform the task because an access exception will be thrown and logged.',
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
    'match': ['log aggregation'],
    'status': 'not_a_finding',
    'comments': f'{tool_name} uses the JWAC logging framework which does this.',
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
        if is_debug_mode:
          matches = ', '.join(auto_stig['match'])
          stig_rules[j]['comments'] = f'Matched "{matches}"'
        else:
          if len(stig_rules[j]['comments']) < 2 or stig_rules[j]['comments'].startswith('Matched "') or stig_rules[j]['comments'].startswith('POC: '):
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

