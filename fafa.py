from pynput import mouse,keyboard
from pynput.keyboard import Key
from pynput.mouse import Button
import time
import sys
class Record:
    def __init__(self,filename):
        self.fp = open(filename,'w')
        print('Press ctrl to start.')
        self.is_record = False
        self.start()
    def on_move(self,x, y):
        if self.is_record is False:
            return
        # print('Pointer moved to {0}'.format(
        #     (x, y)))
        pass

    def on_click(self, x, y, button, pressed):
        if self.is_record is False:return
        this_time = time.time()
        print('{0} at {1}'.format(
            'Pressed' if pressed else 'Released',
            (x, y)),button.name,this_time - self.last_time)
        fs = '{delay:.3f} {x} {y} {button} {pressed}\n'
        command = fs.format(delay=this_time-self.last_time,x=x,y=y,button=button.name,pressed=pressed)

        self.fp.write(command)
        self.last_time = this_time

    def on_scroll(self, x, y, dx, dy):
        if self.is_record is False:
            return
        # print('Scrolled {0} at {1}'.format(
        #     'down' if dy < 0 else 'up',
        #     (x, y)))
        pass
    def on_key_press(self,key):
        if self.is_record is False:
            return
        this_time = time.time()
        print(key,'on press')
        if key == Key.esc:
            self.mouse_listener.stop()
            return False
        fs = '{delay:.3f} {key} True\n' 
        command = fs.format(delay = this_time-self.last_time,key = key)
        self.fp.write(command)
        self.last_time = this_time
    def on_key_release(self,key):
        if key is Key.ctrl and self.is_record is False:
            print('Start to record')
            self.is_record = True
            return
        if self.is_record is False:
            return
        this_time = time.time()
        print(key, 'on release')
        fs = '{delay:.3f} {key} False\n'
        command = fs.format(delay=this_time-self.last_time, key=key)
        self.fp.write(command)
        self.last_time = this_time

    def start(self):
        self.mouse_listener = mouse.Listener(
                on_move=self.on_move,
                on_click=self.on_click,
                on_scroll=self.on_scroll)
        self.mouse_listener.start()
        self.keyboard_listener = keyboard.Listener(
            on_press = self.on_key_press,
            on_release = self.on_key_release
        )
        self.keyboard_listener.start()
        self.last_time = time.time()
        self.keyboard_listener.join()
        self.fp.close()
        print('Successfully finished recording!')
def Play(filename,times):
    mouse_con = mouse.Controller()
    key_con = keyboard.Controller()

    def key_control(arg):
        delay,k,pressed = arg
        time.sleep(float(delay))
        if k.startswith('Key'):
            k = getattr(Key, k.split('.')[1])
        elif k[0] == "'":
            k = k[1:-1]
        if pressed[0] == 'T':
            key_con.press(k)
        else:
            key_con.release(k)
    def mouse_control(arg):
        delay,x,y,button,pressed = arg
        time.sleep(float(delay))
        button = getattr(Button,button)
        mouse_con.position = (int(x),int(y))
        if pressed[0] == 'T':
            mouse_con.press(button)
        else:
            mouse_con.release(button)
    for _ in range(times):
        for i in open(filename,'r'):
            i =i.strip()
            if not i or i[0] == '#':
                continue
            print(i)
            k = i.split()
            if len(k) == 3:
                key_control(k)
            else:
                mouse_control(k)

def parse_command(argvs):
    keys = []
    values = []
    for i,v in enumerate(argvs):
        if v.startswith('--'):
            keys.append(v[2:])
            values.append(True)
        elif v.startswith('-'):
            keys.append(v[1:])
            values.append(argvs[i+1])
    return dict(zip(keys,values))
if __name__=='__main__':
    d = parse_command(sys.argv)

    k = d.get('p',None)
    if d.get('p',None) is not None:
        Play(d['p'], int(d.get('n', '1')))
    elif d.get('r',None) is not None:
        Record(d['r'])

