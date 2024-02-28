import curses
import threading
import queue
import keyboard  # For global key state monitoring

# Global flag for Ctrl key state
ctrl_key_pressed = False

def monitor_ctrl_key():
    global ctrl_key_pressed
    def on_press(event):
        global ctrl_key_pressed
        if event.name == 'ctrl':
            ctrl_key_pressed = True

    def on_release(event):
        global ctrl_key_pressed
        if event.name == 'ctrl':
            ctrl_key_pressed = False

    # Listen for press and release events
    keyboard.on_press(on_press)
    keyboard.on_release(on_release)

def setup_windows(stdscr):
    curses.curs_set(0)  # Hide cursor
    height, width = stdscr.getmaxyx()

    # Calculate window sizes and positions
    thoughts_height = int(height * 0.3)
    command_output_height = height - thoughts_height - 3  # Leave space for input
    input_height = 3

    # Create windows
    thoughts_win = curses.newwin(thoughts_height, width, 0, 0)
    command_output_win = curses.newwin(command_output_height, width, thoughts_height, 0)
    input_win = curses.newwin(input_height, width, thoughts_height + command_output_height, 0)

    thoughts_win.box()
    command_output_win.box()
    input_win.box()

    thoughts_win.addstr(1, 1, "Thoughts")
    command_output_win.addstr(1, 1, "Command Output")
    input_win.addstr(1, 1, "Input: ")

    thoughts_win.refresh()
    command_output_win.refresh()
    input_win.refresh()

    return thoughts_win, command_output_win, input_win

def text_input_handler(input_win, q):
    # Make getch non-blocking
    input_win.nodelay(True)

    input_str = ""
    while True:
        char = input_win.getch()
        if char == ord('\n'):  # Enter key
            q.put(input_str)  # Simulate processing input or commands
            input_str = ""
        elif char == 27:  # ESC key to exit
            break
        elif char != -1:  # Valid character input
            if char == 127 or char == curses.KEY_BACKSPACE:  # Backspace handling
                input_str = input_str[:-1]
            else:
                input_str += chr(char)
            input_win.clear()
            input_win.box()
            input_win.addstr(1, 1, "Input: " + input_str)
            input_win.refresh()

def main(stdscr):
    # Setup windows
    thoughts_win, command_output_win, input_win = setup_windows(stdscr)

    # Create a queue for inter-thread communication
    q = queue.Queue()

    # Start text input handler in a separate thread
    input_thread = threading.Thread(target=text_input_handler, args=(input_win, q), daemon=True)
    input_thread.start()

    # Main loop: Display thoughts or command output
    while True:
        # Update thoughts window with Ctrl key state
        if ctrl_key_pressed:
            thoughts_win.addstr(2, 1, "Ctrl key is pressed!       ", curses.A_REVERSE)
        else:
            thoughts_win.addstr(2, 1, "Ctrl key is not pressed!   ")
        thoughts_win.refresh()

        # Check if there's something new in the queue
        try:
            input_text = q.get_nowait()
            command_output_win.addstr(2, 1, "You said: " + input_text + " " * (width - len(input_text) - 12), curses.A_BOLD)
            command_output_win.refresh()
        except queue.Empty:
            pass
        curses.napms(50)  # Sleep briefly to reduce CPU usage

ctrl_monitor_thread = threading.Thread(target=monitor_ctrl_key, daemon=True)
ctrl_monitor_thread.start()

if __name__ == "__main__":
    curses.wrapper(main)
