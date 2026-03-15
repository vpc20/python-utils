import subprocess
import time


def send_to_acs():
    # 1. Define the window title (usually starts with 'Access Client Solutions')
    # Use 'xdotool getwindowfocus getwindowname' in a terminal to find your exact title
    win_title = "A - pub400"

    try:
        print(f"Searching for window: {win_title}...")

        # 2. Find the window ID and activate it (bring to front)
        # --sync waits for the window to be found before proceeding
        subprocess.run(["xdotool", "search", "--sync", "--name", win_title, "windowactivate"], check=True)

        # 3. Small pause to ensure the window has focus
        time.sleep(1.5)

        # 4. Type the command and press Enter
        print(f"ACS automation in 5250 terminal in progress... ")
        subprocess.run(["xdotool", "type", "--delay", "100", "wrksplf"])
        subprocess.run(["xdotool", "key", "Return"])
        print(f"Process finished.")

    except subprocess.CalledProcessError:
        print(f"Error: Could not find a window named '{win_title}'.")


if __name__ == "__main__":
    # Example: Call a program once you are signed in
    send_to_acs()
