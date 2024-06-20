
import time

try:
    import win32api, win32con
except:
    import subprocess, sys
    subprocess.run([
        sys.executable, '-m', 'pip', 'install', '--user', 'pywin32'
    ])
    import win32api, win32con
    
def click(x,y):
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)


x = input('Move mouse to pos 1 and strike enter ')
pos1_x, pos1_y = win32api.GetCursorPos()

x = input('Move mouse to pos 2 and strike enter ')
pos2_x, pos2_y = win32api.GetCursorPos()

iterations = int(input('Type number of iterations: '))

def is_cursor_at(x, y):
    current_x, current_y = win32api.GetCursorPos()
    return abs(x - current_x) <= 4 and abs(y - current_y) <= 4

for i in range(0,iterations):
    print('.', end='', flush=True)

    click(pos1_x, pos1_y)
    time.sleep(0.45)
    if not is_cursor_at(pos1_x, pos1_y):
        print(f'Exiting on movement!')
        break

    click(pos2_x, pos2_y)
    if not is_cursor_at(pos2_x, pos2_y):
        print(f'Exiting on movement!')
        break

    time.sleep(0.45)

print()
print('Done!')

