import os
import psutil
import tkinter as tk
from tkinter import ttk
import subprocess
import platform

def get_drives():
    partitions = psutil.disk_partitions()
    drives = [partition.device for partition in partitions]
    return drives

def populate_tree(tree, parent, path):
    try:
        for item in os.listdir(path):
            abs_path = os.path.join(path, item)
            node = tree.insert(parent, 'end', text=item, open=False)
            if os.path.isdir(abs_path):
                tree.insert(node, 'end', text='Loading...')
    except PermissionError:
        pass

def on_open_folder(event):
    node_id = event.widget.focus()
    path = build_path_from_node(event.widget, node_id)

    children = event.widget.get_children(node_id)
    if len(children) == 1 and event.widget.item(children[0], 'text') == 'Loading...':
        event.widget.delete(children[0])

        populate_tree(event.widget, node_id, path)

def build_path_from_node(tree, node_id):
    path = []
    while node_id:
        path.insert(0, tree.item(node_id, 'text'))
        node_id = tree.parent(node_id)
    return os.path.join(*path)

def open_in_explorer(event):
    node_id = event.widget.focus()
    path = build_path_from_node(event.widget, node_id)
    
    if os.path.exists(path):
        if platform.system() == 'Windows':
            os.startfile(path)
        elif platform.system() == 'Darwin':
            subprocess.Popen(['open', path])
        else:
            subprocess.Popen(['xdg-open', path])
    
    return "break"

root = tk.Tk()
root.title("Dynamic File Explorer (Dark Mode)")

bg_color = "#2E2E2E"
fg_color = "#FFFFFF"
highlight_color = "#666666"

root.configure(bg=bg_color)

style = ttk.Style(root)
style.theme_use("clam")
style.configure("Treeview",
                background=bg_color,
                foreground=fg_color,
                fieldbackground=bg_color,
                rowheight=25,
                font=('Helvetica', 12))
style.map("Treeview",
          background=[("selected", highlight_color)],
          foreground=[("selected", fg_color)])

tree_frame = tk.Frame(root, bg=bg_color, padx=10, pady=10)
tree_frame.pack(fill='both', expand=True)
tree = ttk.Treeview(tree_frame)
tree.pack(fill='both', expand=True)

for drive in get_drives():
    root_node = tree.insert('', 'end', text=drive, open=False)
    populate_tree(tree, root_node, drive)

tree.bind("<<TreeviewOpen>>", on_open_folder)
tree.bind("<Return>", open_in_explorer)  

root.mainloop()
