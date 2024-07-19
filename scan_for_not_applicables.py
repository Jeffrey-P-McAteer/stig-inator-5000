
import os
import sys
import shutil
import json
import time
import datetime

is_debug_mode = 't' in os.environ.get('DEBUG', '') or '1' in os.environ.get('DEBUG', '')

test_checklist_file = '/j/downloads/TestChecklist.cklb'
if len(sys.argv) > 1:
  test_checklist_file = sys.argv[1]

print(f'Opening checklist file {test_checklist_file}')

test_checklist = None
with open(test_checklist_file, 'r', encoding='utf-8') as fd:
  test_checklist = json.load(fd)

apply_desktop_app_stigs_impl = ''
with open('apply_desktop_app_stigs.py', 'r') as fd:
   apply_desktop_app_stigs_impl = fd.read()
   if not isinstance(apply_desktop_app_stigs_impl, str):
      apply_desktop_app_stigs_impl = apply_desktop_app_stigs_impl.decode('utf-8')

if_end_clauses_to_scan_for = [
  'is not applicable',
  'is not a finding'
]

rule_text_fragments = []

stigs = test_checklist['stigs']
for i in range(0, len(stigs)):
  name = stigs[i]['display_name']
  print(f'========== {name} ==========')
  stig_rules = stigs[i]['rules']
  num_rules_stiginated = 0
  for j in range(0, len(stig_rules)):
    rule_name = stig_rules[j]['group_title']
    #print(f'Processing: {rule_name}')
    #print('.', end='', flush=True)

    rule_text = (' ' * 32)+' '.join([
      stig_rules[j]['rule_title'].lower(),
      stig_rules[j]['group_title'].lower(),
      stig_rules[j]['check_content'].lower(),
      stig_rules[j]['discussion'].lower(),
    ])+(' ' * 32)
    rule_text = rule_text.replace('\r\n', '\n').replace('\n', ' ')

    # Here we parse & print out <if> ... <is not applicable>
    # or <if> ... <is not a finding>
    for end_clause in if_end_clauses_to_scan_for:
        for i in range(0, len(rule_text)-16):
            if rule_text[i : i+len(end_clause)] == end_clause:
                # Back up to the last capital-I 'If' token and print the stuff in between.
                for j in range(i, 0, -1):
                    if rule_text[j:j+3] == ' if':
                        text_fragment = rule_text[j:i+len(end_clause)].strip()
                        if not text_fragment in rule_text_fragments:
                            prefix = ''
                            if text_fragment in apply_desktop_app_stigs_impl:
                               prefix = '[E] '
                            print(prefix+text_fragment)
                            rule_text_fragments.append(text_fragment)
                        break

print(f'============= Generated Desktop-App Match code =============')
if 'y' in input('Generate? ').lower():
    for rule_fragment in rule_text_fragments[:1]:
        if 'is not applicable' in rule_fragment:
            inverted_fragment = rule_fragment.rsplit(',', maxsplit=1)[0].strip()
            inverted_fragment = inverted_fragment.removesuffix('the requirement is not applicable')
            inverted_fragment = inverted_fragment.removesuffix('in this case')
            inverted_fragment = inverted_fragment.removesuffix(' ')
            inverted_fragment = inverted_fragment.removesuffix(' ')
            inverted_fragment = inverted_fragment.removesuffix('.')
            inverted_fragment = inverted_fragment.removeprefix('if ')

            comment_text = inverted_fragment
            if 'the application' in inverted_fragment:
                comment_text = inverted_fragment.replace('the application', '{tool_name}')
                comment_text = comment_text.replace('{tool_name} under review', 'the application under review')
                comment_text = comment_text.replace('{tool_name}s', 'the applications')

            elif '' in inverted_fragment:
                pass

            print(f'{{')
            print(f"  'match': ['{rule_fragment}'],")
            print(f"  'status': 'not_applicable',")
            print(f"  'comments': f'{comment_text}',")
            print(f'}}')

