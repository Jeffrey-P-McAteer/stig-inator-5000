
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
]



test_checklist_file = '/j/downloads/TestChecklist.cklb'
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
        break


  stigs[i]['rules'] = stig_rules
  print()
  print(f'{num_rules_stiginated} of {len(stig_rules)} rules matched trivial groups and were automatically filled with the group data.')

test_checklist['stigs'] = stigs

output_test_checklist_file = test_checklist_file #+'.auto.cklb'
with open(output_test_checklist_file, 'w') as fd:
  json.dump(test_checklist, fd)
print(f'Wrote to {output_test_checklist_file}')

