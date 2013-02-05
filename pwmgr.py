#!/usr/bin/env python2
import os.path

from time import time, sleep
from ConfigParser import ConfigParser
from subprocess import Popen, PIPE

import gtk, gtk.gdk, glib


APP = 'pwmgr'

def join_to_settings_dir(*args):
    config_dir = os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
    return os.path.join(config_dir, *args)

def get_conf(path_to_config, is_plain):
    conf = ConfigParser()
    if is_plain:
        conf.read(path_to_config)
    else:
        p = Popen(['gpg'], stdin=PIPE, stdout=PIPE)
        p.stdin.write(open(path_to_config).read())
        p.stdin.close()
        conf.readfp(p.stdout)

    return conf

def quit():
    gtk.main_quit()
    return False

def on_text_request(clipboard, selection, info, data):
    if info == 1:
        idx = data[0][0]
        if data[1][0] and time() - data[1][0] < 0.1:
            idx -= 1

        selection.set_text(data[idx], -1)

        if idx >= 3:
            glib.timeout_add(1000, quit)

        data[0][0] = idx + 1
        data[1][0] = time()

def on_text_request_clear(*args):
    print args

def on_btn_click(widget, cmd, user, password):
    Popen(cmd, shell=True).poll()
    clipboard = gtk.clipboard_get('CLIPBOARD')
    clipboard.set_with_data([('STRING', 0, 1)], on_text_request, None,
        ([2], [None], user, password))

def show_ui(conf):
    win = gtk.Window()
    win.connect("delete-event", gtk.main_quit)
    win.set_title('pwmgr')
    win.set_border_width(5)
    win.set_position(gtk.WIN_POS_CENTER)

    box = gtk.VBox(True, 5)
    for section in conf.sections():
        btn = gtk.Button(section)
        btn.connect('clicked', on_btn_click, conf.get(section, 'run'),
            conf.get(section, 'user'), conf.get(section, 'password'))
        box.pack_start(btn, True, True, 0)

    win.add(box)

    win.show_all()
    gtk.main()

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-c', '--config', dest='config',
        default=join_to_settings_dir(APP + '.ini.gpg'), help='Path to config (%(default)s)')
    parser.add_argument('-p', '--plain', dest='is_plain', default=False,
        action='store_true', help='Indicates that a config is not encoded')

    args = parser.parse_args()

    show_ui(get_conf(args.config, args.is_plain))