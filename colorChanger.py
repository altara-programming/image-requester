import sys
import tkinter as tk


# add less polorizing colors for http protocol theme change
def change(delay, frame, sequence, index):
    index = (index + 1) % len(sequence)
    frame.configure(background=sequence[index])
    frame.after(delay, lambda: change(delay, frame, sequence, index))

def main(argv=None):
    sequence = ['black', 'grey40', 'grey60', 'grey80', 'white', 'grey80', 'grey60', 'grey40']
    root = tk.Tk()
    frame = tk.Frame(root, width=200, height=200, background="red")
    frame.pack(fill=tk.BOTH, expand=True)
    change(100, frame, sequence, -1)
    root.mainloop()
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
