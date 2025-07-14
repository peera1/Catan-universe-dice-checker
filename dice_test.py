# dice_test.py
import os
import time
import random
from pathlib import Path
from playwright.sync_api import sync_playwright

def run_dice_fairness_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch() # Launch a headless browser
        page = browser.new_page()

        # Navigate to the local HTML file
        html_file_path = Path(__file__).parent / 'index.html'
        page.goto(f"file://{html_file_path}")

        # Selectors for the elements we need to interact with
        die1_input = page.locator('#die1')
        die2_input = page.locator('#die2')
        roll_button = page.locator('#rollButton')
        reset_button = page.locator('#resetButton')
        fairness_score_display = page.locator('#fairnessScoreDisplay')

        # Handle the confirmation dialog for the reset button
        def handle_dialog(dialog):
            if dialog.type == 'confirm' and 'לאפס את כל נתוני הזריקות' in dialog.message:
                dialog.accept()
            else:
                dialog.dismiss()
        
        page.on('dialog', handle_dialog)

        def perform_rolls(num_rolls):
            print(f"\n--- מתחיל סימולציה של {num_rolls} זריקות ---")
            for i in range(num_rolls):
                # Generate random dice values (1-6)
                die1 = random.randint(1, 6)
                die2 = random.randint(1, 6)

                # Fill the input fields
                die1_input.fill(str(die1))
                die2_input.fill(str(die2))

                # Wait for the roll button to become enabled (i.e., not disabled)
                page.wait_for_selector('#rollButton:not([disabled])') 
                
                # Now that the button is enabled, click it
                roll_button.click()
            
            # After all rolls, get the fairness score
            time.sleep(0.5) # Give a small moment for UI to update fairness score
            score = fairness_score_display.text_content()
            print(f"ציון הוגנות לאחר {num_rolls} זריקות: {score}")

            # --- NEW: Get and print the distribution of sums ---
            # Execute JavaScript in the browser context to get the rollCounts array
            # We slice from index 2 because rollCounts[0] and rollCounts[1] are unused (for sums 0 and 1)
            roll_counts_from_browser = page.evaluate("() => window.rollCounts.slice(2)")
            
            print("התפלגות סכומים:")
            for i, count in enumerate(roll_counts_from_browser):
                sum_value = i + 2 # Since slice(2) means index 0 here corresponds to sum 2
                print(f"  סכום {sum_value}: {count} פעמים")
            # --- END NEW ---

        # --- Run Tests ---

        # Test 1: 50 rolls
        perform_rolls(50)
        reset_button.click() # Reset data for the next test

        # Test 2: 100 rolls
        perform_rolls(100)
        reset_button.click() # Reset data for the next test

        # Test 3: 1000 rolls
        perform_rolls(1000)
        # No reset needed after the last test
        
        browser.close() # Close the browser

if __name__ == "__main__":
    try:
        run_dice_fairness_tests()
    except Exception as e:
        print(f"An error occurred during the Playwright test: {e}")
        exit(1) # Exit with a non-zero code to indicate failure
