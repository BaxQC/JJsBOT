import tkinter as tk
from tkinter import ttk, messagebox
import pydirectinput
import pyperclip
import pygetwindow as gw
import threading
import time

pydirectinput.PAUSE = 0.2

is_running = False

def num_to_words(num):
    if num == 0: return "zero"
    ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
            "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
            "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
    if num < 20: return ones[num]
    if num < 100:
        t, o = tens[num // 10], num % 10
        return t if o == 0 else f"{t}-{ones[o]}"
    if num < 1000:
        h, r = ones[num // 100] + " hundred", num % 100
        return h if r == 0 else f"{h} {num_to_words(r)}"
    if num < 1000000:
        t, r = num_to_words(num // 1000) + " thousand", num % 1000
        return t if r == 0 else f"{t} {num_to_words(r)}"
    return str(num)

def log(msg):
    log_text.config(state="normal")
    log_text.insert(tk.END, msg + "\n")
    log_text.see(tk.END)
    log_text.config(state=tk.DISABLED)

def get_roblox_window():
    """Find the Roblox window and return it."""
    for title in ["Roblox", "roblox"]:
        windows = gw.getWindowsWithTitle(title)
        if windows:
            return windows[0]
    return None

def focus_roblox():
    """Force Roblox to be the ACTIVE window. Returns True if OK."""
    win = get_roblox_window()
    if not win:
        log("ERROR: No Roblox window found! Is the game open?")
        return False

    # Try to activate the window
    try:
        if win.isMinimized:
            win.restore()
        win.activate()
    except Exception:
        # Fallback for stubborn windows (Windows quirk)
        win.minimize()
        win.restore()
        win.activate()
    time.sleep(0.5)

    # DOUBLE CHECK: is Roblox actually the active window now?
    try:
        active = gw.getActiveWindow()
        if active and "Roblox" in active.title:
            log("Roblox window is focused. OK!")
            return True
    except Exception:
        pass

    # Second attempt: minimize & restore trick
    try:
        win.minimize()
        time.sleep(0.3)
        win.restore()
        time.sleep(0.3)
        win.activate()
        time.sleep(0.5)
        active = gw.getActiveWindow()
        if active and "Roblox" in active.title:
            log("Roblox focused on 2nd try. OK!")
            return True
    except Exception:
        pass

    log("WARNING: Could not confirm Roblox focus, will still try...")
    return True

def test_connection():
    """Test button: Focus Roblox and open the chat with / """
    def _test():
        log("--- Testing connection to Roblox ---")
        ok = focus_roblox()
        if ok:
            log("Opening chat with '/' ... (look at your game!)")
            time.sleep(0.5)
            pydirectinput.press('/')
            log("DONE! If the chat box opened in Roblox, the bot WILL work.")
            log("Press Esc in game to close the chat box.")
    threading.Thread(target=_test, daemon=True).start()

def start_sequence():
    global is_running
    try:
        start = int(start_entry.get())
        end = int(end_entry.get())
        mode = mode_var.get()
        delay = float(delay_var.get())

        if start >= end:
            messagebox.showerror("Error", "Start must be lower than End.")
            return

        run_btn.config(state="disabled")
        stop_btn.config(state="normal")
        is_running = True
        thread = threading.Thread(target=run_bot, args=(start, end, mode, delay))
        thread.daemon = True
        thread.start()
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numbers.")

def stop_sequence():
    global is_running
    is_running = False
    run_btn.config(state="normal")
    stop_btn.config(state="disabled")
    log("--- Stopped by user ---")

def run_bot(start, end, mode, delay):
    global is_running

    log("--- Starting in 3 seconds... SWITCHING TO ROBLOX ---")
    focus_roblox()
    time.sleep(3)

    for i in range(start, end + 1):
        if not is_running:
            break

        # SELF CHECK every number: make sure Roblox is still focused
        try:
            active = gw.getActiveWindow()
            if not active or "Roblox" not in active.title:
                log("Lost Roblox focus! Re-focusing...")
                focus_roblox()
        except Exception:
            pass

        num_word = num_to_words(i)
        if mode == "Caps":
            text = num_word.upper()
        elif mode == "!":
            text = num_word + "!"
        else:
            text = num_word + "."

        status_label.config(text=f"Saying: {text}")
        log(f"[{i}/{end}] {text}")

        # 1. Copy text to clipboard
        pyperclip.copy(text)
        time.sleep(0.1)

        # 2. Open chat with "/" (real DirectInput key — Roblox listens to this)
        pydirectinput.press('/')
        time.sleep(0.4)

        # 3. Paste (Ctrl+V) — press one key at a time the direct way
        pydirectinput.keyDown('ctrl')
        time.sleep(0.05)
        pydirectinput.press('v')
        time.sleep(0.05)
        pydirectinput.keyUp('ctrl')
        time.sleep(0.4)

        # 4. Send message
        pydirectinput.press('enter')
        time.sleep(0.5)

        # 5. JUMP (real key press)
        pydirectinput.press('space')
        time.sleep(0.2)

        # 6. Wait
        time.sleep(delay)

    if is_running:
        status_label.config(text="Finished!")
        log("--- Finished ---")
    is_running = False
    run_btn.config(state="normal")
    stop_btn.config(state="disabled")

def main():
    global root, start_entry, end_entry, mode_var, delay_var, run_btn, stop_btn, status_label, log_text

    root = tk.Tk()
    root.title("Bax - JJs BOT")
    root.geometry("420x640")
    root.resizable(False, False)
    root.configure(bg="#222")

    tk.Label(root, text="JJs BOT", font=("Arial", 18, "bold"), bg="#222", fg="#00d2d3").pack(pady=10)

    ttk.Button(root, text="TEST CONNECTION", command=test_connection).pack(fill="x", padx=40, pady=5)

    frame = tk.Frame(root, bg="#222")
    frame.pack(fill="x", padx=20, pady=10)
    tk.Label(frame, text="Start:", bg="#222", fg="white").pack(side=tk.LEFT, padx=5)
    start_entry = ttk.Entry(frame, width=6); start_entry.insert(0, "1"); start_entry.pack(side=tk.LEFT, padx=5)
    tk.Label(frame, text="End:", bg="#222", fg="white").pack(side=tk.LEFT, padx=5)
    end_entry = ttk.Entry(frame, width=6); end_entry.insert(0, "10"); end_entry.pack(side=tk.LEFT, padx=5)
    tk.Label(frame, text="Delay:", bg="#222", fg="white").pack(side=tk.LEFT, padx=5)
    delay_var = tk.StringVar(value="1.0")
    ttk.Entry(frame, width=6, textvariable=delay_var).pack(side=tk.LEFT, padx=5)

    mode_frame = tk.LabelFrame(root, text="Style", bg="#222", fg="white", font=("Arial", 10))
    mode_frame.pack(fill="x", padx=20, pady=5)
    mode_var = tk.StringVar(value="Caps")
    ttk.Radiobutton(mode_frame, text="CAPS", variable=mode_var, value="Caps").pack(side=tk.LEFT, padx=10)
    ttk.Radiobutton(mode_frame, text="!", variable=mode_var, value="!").pack(side=tk.LEFT, padx=10)
    ttk.Radiobutton(mode_frame, text="Grammar", variable=mode_var, value="Grammar").pack(side=tk.LEFT, padx=10)

    run_btn = ttk.Button(root, text="START", command=start_sequence)
    run_btn.pack(fill="x", padx=40, pady=10)
    stop_btn = ttk.Button(root, text="STOP", command=stop_sequence, state="disabled")
    stop_btn.pack(fill="x", padx=40, pady=5)

    status_label = tk.Label(root, text="Ready", font=("Arial", 14), bg="#222", fg="#00ff00")
    status_label.pack(pady=5)

    log_text = tk.Text(root, height=10, bg="#333", fg="#ddd", font=("Consolas", 9), bd=0, state=tk.DISABLED)
    log_text.pack(fill="x", padx=20, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()