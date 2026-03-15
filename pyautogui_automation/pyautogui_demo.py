import pyautogui
import time

# --- SAFETY SETTINGS ---
pyautogui.FAILSAFE = True  # Move mouse to ANY corner to abort
pyautogui.PAUSE = 0.5  # Add half-second delay between all commands


def run_terminal_commands():
    # 1. Ask for confirmation before starting
    response = pyautogui.confirm(
        text='Ready to send commands to your 5250 terminal?',
        title='Terminal Automation',
        buttons=['OK', 'Cancel']
    )

    if response == 'Cancel':
        print("Automation cancelled.")
        return

    # 2. Countdown to give you time to click into the terminal window
    print("Switch to your terminal window NOW...")
    for i in range(5, 0, -1):
        print(f"Starting in {i}...")
        time.sleep(1)

    try:
        # 3. Send the keystrokes
        # Use 'write' for strings and 'press' for special keys (F-keys, Enter, etc.)
        pyautogui.write('wrksplf', interval=0.1)
        pyautogui.press('enter')

        # Example: Navigate a menu
        # pyautogui.write('1')
        # pyautogui.press('enter')

        # Example: Press F3 to exit a screen
        # pyautogui.press('f3')

        print("Commands sent successfully!")

    except pyautogui.FailSafeException:
        print("\nFAIL-SAFE TRIGGERED: Script stopped because mouse was moved to a corner.")


if __name__ == "__main__":
    run_terminal_commands()
