
import os
import sys
import shutil
import json

# asd_stig_xml = '/j/downloads/U_ASD_V5R3_STIG/U_ASD_V5R3_Manual_STIG/U_ASD_STIG_V5R3_Manual-xccdf.xml'

is_debug_mode = 't' in os.environ.get('DEBUG', '') or '1' in os.environ.get('DEBUG', '')

tool_name = os.environ.get('TOOL_NAME', 'The tool')

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

]

# ' '.join([
#     f'{tool_name} is a desktop application and makes no access-control decisions.',
#     'If a user is restricted from performing a task without {tool_name}, then using {tool_name} will not allow them to perform the task because an access exception will be thrown and logged.',
# ]),


test_checklist_file = '/j/downloads/TestChecklist.cklb'
if len(sys.argv) > 1:
  test_checklist_file = sys.argv[1]

test_checklist = None
with open(test_checklist_file, 'r') as fd:
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

    rule_text = stig_rules[j]['group_title'].lower() +'\n'+stig_rules[j]['check_content'].lower() +'\n'+ stig_rules[j]['discussion'].lower()

    for auto_stig in auto_stigs:
      if all(needle.lower() in rule_text for needle in auto_stig['match']):
        # This rule is known to be trivial!
        num_rules_stiginated += 1
        stig_rules[j]['comments'] = auto_stig['comments']
        stig_rules[j]['status'] = auto_stig['status']
        if is_debug_mode:
          matches = ', '.join(auto_stig['match'])
          stig_rules[j]['finding_details'] = f'Matched "{matches}"'
        else:
          if stig_rules[j]['finding_details'].startswith('Matched "'):
            stig_rules[j]['finding_details'] = ''
        break


  stigs[i]['rules'] = stig_rules
  print()
  print(f'{num_rules_stiginated} of {len(stig_rules)} rules matched trivial groups and were automatically filled with the group data.')

test_checklist['stigs'] = stigs

output_test_checklist_file = test_checklist_file #+'.auto.cklb'
with open(output_test_checklist_file, 'w') as fd:
  json.dump(test_checklist, fd)
print(f'Wrote to {output_test_checklist_file}')

