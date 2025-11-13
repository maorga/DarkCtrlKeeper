# Google Analytics 4 Setup Guide for DarkCtrlKeeper

This guide explains how to set up optional Google Analytics 4 tracking for DarkCtrlKeeper.

## ⚠️ Important: Analytics is Completely Optional

DarkCtrlKeeper works perfectly fine WITHOUT analytics. Analytics is only for developers who want to understand how their application is being used.

**To disable analytics:** Simply don't create a `.env` file, or leave the GA4 fields empty.

---

## Why Add Analytics?

Analytics helps you understand:
- How many users are actively using the application
- Which features are most popular
- Whether users prefer hotkeys or buttons
- Application stability (how often it's opened/closed properly)

**Privacy Note:** DarkCtrlKeeper collects ZERO personal information. All data is anonymous.

---

## Step 1: Create a Google Analytics 4 Property

1. Go to [Google Analytics](https://analytics.google.com)

2. Sign in with your Google account

3. Click **Admin** (gear icon in bottom-left)

4. Under the **Property** column, click **Create Property**

5. Fill in property details:
   - **Property name:** DarkCtrlKeeper
   - **Reporting time zone:** Your timezone
   - **Currency:** Your currency (for future e-commerce if needed)

6. Click **Next**

7. Select business details:
   - **Industry:** Gaming or Software
   - **Business size:** Choose appropriate size
   - Click **Next**

8. Select objectives (optional), then click **Create**

9. Accept the Terms of Service

---

## Step 2: Create a Data Stream

1. After creating the property, you'll see "Add a data stream"

2. Click **Web** (even though this is a desktop app, we use web stream for Measurement Protocol)

3. Enter stream details:
   - **Website URL:** `https://github.com/maorga/DarkCtrlKeeper`
   - **Stream name:** DarkCtrlKeeper Desktop App

4. Click **Create stream**

5. **IMPORTANT:** Copy your **Measurement ID**
   - Format: `G-XXXXXXXXXX`
   - You'll need this for your `.env` file

---

## Step 3: Generate Measurement Protocol API Secret

1. On the Data Stream details page, scroll down to **Measurement Protocol API secrets**

2. Click **Create** (or **+ Create** button)

3. Enter a nickname: `DarkCtrlKeeper API`

4. Click **Create**

5. **IMPORTANT:** Copy the **Secret Value**
   - This is shown only once!
   - Format: A long alphanumeric string
   - You'll need this for your `.env` file

6. Click **Done**

---

## Step 4: Configure DarkCtrlKeeper

1. Navigate to your DarkCtrlKeeper project folder

2. Copy the example environment file:
   ```powershell
   Copy-Item .env.example .env
   ```

3. Open `.env` in a text editor

4. Fill in your credentials:
   ```bash
   GA4_MEASUREMENT_ID=G-XXXXXXXXXX
   GA4_API_SECRET=your_secret_value_here
   ```

5. Save the file

6. **CRITICAL:** Ensure `.env` is in your `.gitignore` (it should be by default)

---

## Step 5: Verify Analytics is Working

1. Run DarkCtrlKeeper:
   ```powershell
   python src/main.py
   ```

2. Check the console output. You should see:
   ```
   ✓ Loaded environment from .env
   ✓ Analytics initialized (Client ID: xxxxxxxx...)
   ```

3. Use the app (lock CTRL, release CTRL, use hotkeys)

4. Wait 5-10 minutes for data to appear in Google Analytics

5. In Google Analytics:
   - Go to **Reports** → **Realtime**
   - You should see recent events like `app_opened`, `ctrl_locked`, etc.

---

## Events Tracked by DarkCtrlKeeper

| Event Name | Description | Parameters |
|------------|-------------|------------|
| `app_opened` | Application started | `version`, `platform` |
| `app_closed` | Application shut down normally | None |
| `ctrl_locked` | User locked CTRL key | None |
| `ctrl_released` | User released CTRL key | None |

---

## Privacy & Data Collection

### What is Collected:
- **Anonymous Client ID:** A randomly generated UUID stored in `user_config.json`
- **Event names:** Which features you use (lock, release, hotkeys)
- **Timestamps:** When events occur
- **App version:** Which version of DarkCtrlKeeper you're running
- **Platform:** Operating system (Windows, etc.)

### What is NOT Collected:
- ❌ Your name, email, or any personal information
- ❌ Your IP address (anonymized by GA4)
- ❌ File paths or system information
- ❌ Screenshots or window titles
- ❌ Keystrokes or user input data
- ❌ MU Online game data or account information

---

## Troubleshooting

### "Analytics disabled (missing credentials or requests library)"

**Cause:** Either `.env` file is missing, credentials are empty, or `requests` library is not installed.

**Solution:**
```powershell
# Install requests
pip install requests

# Verify .env exists and has correct values
cat .env
```

---

### Events not showing in Google Analytics

**Possible causes:**

1. **Data delay:** GA4 can take 5-30 minutes to show data. Check the **Realtime** report.

2. **Wrong credentials:** Verify your Measurement ID and API Secret are correct.

3. **Network issues:** Check your internet connection. Analytics fails silently.

4. **Firewall:** Ensure `https://www.google-analytics.com` is not blocked.

---

### "Could not load user_config.json"

**Cause:** Permission issues or file corruption.

**Solution:**
```powershell
# Delete the file to regenerate it
Remove-Item user_config.json -Force

# Restart DarkCtrlKeeper
python src/main.py
```

---

## Disabling Analytics

To completely disable analytics:

### Option 1: Don't create .env file
Simply don't copy `.env.example` to `.env`. Analytics will be disabled automatically.

### Option 2: Delete .env file
```powershell
Remove-Item .env -Force
```

### Option 3: Empty the credentials
Open `.env` and remove the values:
```bash
GA4_MEASUREMENT_ID=
GA4_API_SECRET=
```

---

## Security Best Practices

1. **NEVER commit `.env` to Git:**
   - The `.gitignore` already excludes it
   - Double-check before pushing: `git status`

2. **Treat API Secret like a password:**
   - Don't share it publicly
   - Don't put it in screenshots or documentation
   - Regenerate if compromised

3. **Review what's tracked:**
   - Check `src/analytics_manager.py` to see exactly what's sent
   - All tracking is transparent and documented

4. **Use separate properties:**
   - Development: One GA4 property for testing
   - Production: Another for released builds

---

## Advanced: Custom Events

If you want to track additional events, edit `src/main.py`:

```python
# Example: Track timer resets
self.analytics.track_event('timer_reset', {
    'countdown_remaining': self.countdown_milliseconds / 1000.0
})
```

Then check the event in GA4 after 5-10 minutes.

---

## Resources

- [Google Analytics 4 Documentation](https://support.google.com/analytics/answer/9304153)
- [Measurement Protocol Guide](https://developers.google.com/analytics/devguides/collection/protocol/ga4)
- [GA4 Event Reference](https://support.google.com/analytics/answer/9267735)

---

## Questions?

If you have questions about analytics setup, please open an issue on GitHub:
[https://github.com/maorga/DarkCtrlKeeper/issues](https://github.com/maorga/DarkCtrlKeeper/issues)

---

**Remember:** Analytics is completely optional. DarkCtrlKeeper works perfectly without it! 🎮
