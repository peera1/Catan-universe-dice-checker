// diceTest.js
const { chromium } = require('playwright');
const path = require('path');

async function runDiceFairnessTests() {
    let browser;
    try {
        browser = await chromium.launch(); // Launch a headless browser
        const page = await browser.newPage();

        // Navigate to the local HTML file
        // Make sure the path is correct relative to where the script runs
        const htmlFilePath = path.resolve(__dirname, 'index.html'); // Assuming your HTML file is named index.html
        await page.goto(`file://${htmlFilePath}`);

        // Selectors for the elements we need to interact with
        const die1Input = page.locator('#die1');
        const die2Input = page.locator('#die2');
        const rollButton = page.locator('#rollButton');
        const resetButton = page.locator('#resetButton');
        const fairnessScoreDisplay = page.locator('#fairnessScoreDisplay');

        // Handle the confirmation dialog for the reset button
        page.on('dialog', async dialog => {
            if (dialog.type() === 'confirm' && dialog.message().includes('לאפס את כל נתוני הזריקות')) {
                await dialog.accept(); // Accept the confirmation
            } else {
                await dialog.dismiss(); // Dismiss other dialogs
            }
        });

        async function performRolls(numRolls) {
            console.log(`\n--- מתחיל סימולציה של ${numRolls} זריקות ---`);
            for (let i = 0; i < numRolls; i++) {
                // Generate random dice values (1-6)
                const die1 = Math.floor(Math.random() * 6) + 1;
                const die2 = Math.floor(Math.random() * 6) + 1;

                // Fill the input fields
                await die1Input.fill(die1.toString());
                await die2Input.fill(die2.toString());

                // Wait for the button to become enabled (due to validation) and then click it
                // FIX: Use locator.waitFor({ state: 'enabled' }) instead of locator.waitForSelector()
                await rollButton.waitFor({ state: 'enabled' }); 
                await rollButton.click();
            }

            // After all rolls, get the fairness score
            // Add a small delay to ensure the UI updates the fairness score
            await page.waitForTimeout(500); 
            const score = await fairnessScoreDisplay.textContent();
            console.log(`ציון הוגנות לאחר ${numRolls} זריקות: ${score}`);
        }

        // --- Run Tests ---

        // Test 1: 50 rolls
        await performRolls(50);
        await resetButton.click(); // Reset data for the next test

        // Test 2: 100 rolls
        await performRolls(100);
        await resetButton.click(); // Reset data for the next test

        // Test 3: 1000 rolls
        await performRolls(1000);
        // No reset needed after the last test
        
    } catch (error) {
        console.error('An error occurred during the Playwright test:', error);
        process.exit(1); // Exit with a non-zero code to indicate failure
    } finally {
        if (browser) {
            await browser.close(); // Close the browser
        }
    }
}

runDiceFairnessTests();
