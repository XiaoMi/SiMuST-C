#!/usr/bin/env python3 -u
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import re
import os
import time
from tkinter import *
from tkinter import scrolledtext
import tkinter
import tkinter.messagebox
import tkinter.font as tf

def read_file(f):
    results = []
    with open(f, 'r', encoding='utf-8') as f:
        for l in f:
            l = l.strip('\n')
            results.append(l)
    return results

def write_file(file, lines, mod='w'):
    with open(file, mod, encoding='utf-8') as f:
        for l in lines:
            f.write(l+'\n')

def contain_zh(line):
    line_ = re.sub(r"[^\u4e00-\u9fa5]", "", line)
    if len(line_) == 0:
        return False
    else:
        return True

def gui_annotation(source_line, save_text, save_stream, sample_nums, current_id):
    # source_line = "I've been illustrating books since I was 16."
    source_tokens = source_line.split()
    source_stream = [' '.join(source_tokens[:i+1]) for i in range(len(source_tokens))]
    source_stream = iter(source_stream)

    final_annotation = ""
    final_stream = ""

    start_time = time.time()

    font_size = 13

    window = Tk()
    title = "Annotation sample ({}/{})".format(current_id, sample_nums)
    window.title(title)
    window.geometry("1024x840")

    note_text = Label(window, text="Stream Record(Please do not modify.)", anchor='nw', font=('微软雅黑', font_size, 'bold'))
    note_text.pack(ipadx=10,
                ipady=10,
                fill='x')

    stream = scrolledtext.ScrolledText(window, width=50, height=20, font=('微软雅黑', font_size - 1))
    stream.pack(ipadx=10,
                ipady=10,
                fill='x')


    source_prefix = Label(window, text="[  Source  ]:\t", wraplength=1024, anchor='nw',font=('微软雅黑', font_size - 1))
    source_prefix.pack(
                ipadx=10,
                ipady=10,
                fill='x',
    )
    target_prefix = Label(window, text="[Annotation]:\t", wraplength=1024, anchor='nw',font=('微软雅黑', font_size - 1))
    target_prefix.pack(
                ipadx=10,
                ipady=10,
                fill='x'
    )

    note_text1 = Label(window, text="New annotation：", anchor='nw', font=('微软雅黑', font_size - 1, 'bold'))
    note_text1.pack(ipadx=10,
                   ipady=10,
                   fill='x')

    txt = Entry(window, width=60,font=('微软雅黑', font_size - 1))
    txt.pack(
                ipadx=10,
                ipady=10,
                fill='x'
    )

    def Read():
        try:
            stream_input = next(source_stream)
            stream_txt = stream.get('1.0', tkinter.END)
            stream_txt = stream_txt.strip('\n').strip()

            if len(stream_txt) > 0:
                trans_res = "[Annotation]:\t" + txt.get()
                target_prefix['text'] = trans_res
                timestamp = time.time() - start_time
                stream.insert(END, trans_res.split('\t')[-1] + '\t' + "{0:.2f}".format(timestamp) + '\n')
                stream.see(END)

            source_prefix['text'] = "[  Source  ]:\t" + stream_input
            stream.insert(END, stream_input+'\t')
        except StopIteration:
            tkinter.messagebox.showwarning('Note: ', 'Reading finish, please complete the translation and click Finish.')


    def Finish():
        if source_prefix['text'].split('\t')[-1] == source_line:
            if len(txt.get()) > 0:
                trans_res = "[Annotation]:\t" + txt.get()
                target_prefix['text'] = trans_res
                timestamp = time.time() - start_time
                stream.insert(END, trans_res.split('\t')[-1] + '\t' + "{0:.2f}".format(timestamp) + '\n')
                txt.delete(0, 'end')

            global final_stream
            final_stream = stream.get('1.0', tkinter.END)

            finish = True

            stream_lines = final_stream.strip('\n').split('\n')
            stream_lines = [x.split('\t') for x in stream_lines]

            final_trans = target_prefix['text'].split('\t')[-1]
            wrong_ids = []
            for i, s in enumerate(stream_lines):
                print(s)
                s = s[:3]
                if not final_trans.startswith(s[1]):
                    finish=False
                    wrong_ids.append(i)

            if finish == False:
                assert len(wrong_ids) > 0
                print("===error===")
                stream.delete('1.0',END)
                for i, s in enumerate(stream_lines):
                    s = s[:3]
                    if i in wrong_ids:
                        show_line = '\t'.join(s + ['<WRONG>'])
                    else:
                        show_line = '\t'.join(s)
                    print(show_line)
                    stream.insert(END, show_line + '\n')
                tkinter.messagebox.showwarning('Note: ', 'The streaming record is not incremental, '
                                                         'please modify the streaming lines with <WRONG> tags!')

            else:
                with open(save_stream, 'a', encoding='utf-8') as f:
                    stream_lines = final_stream.strip('\n').split('\n')
                    stream_lines = [x.split('\t')[:3] for x in stream_lines]
                    stream_lines = ['\t'.join(x) for x in stream_lines]
                    save_line = '\n'.join(stream_lines)

                    f.write(save_line + '\n')

                global final_annotation
                final_annotation = target_prefix['text'].split('\t')[-1]
                with open(save_text, 'a', encoding='utf-8') as f:
                    f.write(final_annotation + '\n')

                window.destroy()
        else:
            tkinter.messagebox.showwarning('Note: ', 'Source sentence is not finish, please click READ.')


    read_btn = Button(window, text="Read", font=('微软雅黑', font_size - 1, 'bold'), command=Read)
    read_btn.pack(ipadx=5,pady=5)
    finish_btn = Button(window, text="Finish", font=('微软雅黑', font_size - 1, 'bold'), command=Finish)
    finish_btn.pack(ipadx=5,pady=5)
    window.mainloop()

def gui_get_path(tmp_path='./path.tmp'):
    window = Tk()
    window.title("Annotation begin.")
    window.geometry("512x256")
    font_size = 13
    note_text = Label(window, text="Input English file", anchor='nw', font=('微软雅黑', font_size, 'bold'))
    note_text.pack(ipadx=10,
                   ipady=10,
                   fill='x')
    input_path = Entry(window, width=60)
    input_path.pack(
        ipadx=10,
        ipady=10,
        fill='x'
    )

    note_text1 = Label(window, text="Output Chinese file", anchor='nw', font=('微软雅黑', font_size, 'bold'))
    note_text1.pack(ipadx=10,
                   ipady=10,
                   fill='x')
    output_path = Entry(window, width=60)
    output_path.pack(
        ipadx=10,
        ipady=10,
        fill='x'
    )

    def CheckPath():
        input_file = input_path.get()
        output_file = output_path.get()
        if not os.path.exists(input_file):
            tkinter.messagebox.showwarning('Error: ', 'File not found: {}'.format(input_file))
        else:
            path_info = {"input_path": input_file,
                         "output_path": output_file}
            with open(tmp_path, 'w', encoding='utf-8') as f:
                save_info = json.dumps(path_info)
                f.write(save_info)
            window.destroy()


    begin_btn = Button(window, text="Begin", font=('微软雅黑', font_size - 1, 'bold'), command=CheckPath)
    begin_btn.pack(ipadx=5, pady=5)

    window.mainloop()

if __name__ == '__main__':
    tmp_path = './path.tmp'
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
    gui_get_path(tmp_path)
    with open(tmp_path, encoding='utf-8') as f:
        info = f.read()
        info = json.loads(info)
    input_file = info['input_path']
    output_file = info['output_path']
    output_stream_file = output_file + '.stream'

    write_mode = 'w'
    annotated_nums = 0
    if os.path.exists(output_file):
        write_mode = 'a'
        annotated_lines = read_file(output_file)
        annotated_nums = len(annotated_lines)
        # os.remove(output_file)
    # if os.path.exists(output_stream_file):
        # os.remove(output_stream_file)


    input_lines = read_file(input_file)

    output_lines = []
    output_streams = []


    for i, line in enumerate(input_lines):
        if i < annotated_nums:
            continue
        else:
            gui_annotation(line, save_text=output_file, save_stream=output_stream_file,
                           sample_nums=len(input_lines), current_id=i+1)


