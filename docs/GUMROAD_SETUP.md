# Gumroad Store Setup for Papagaio

This guide explains how to set up your Gumroad store to sell Papagaio licenses.

## 1. Create Gumroad Account

1. Go to https://gumroad.com
2. Sign up with your email (alexandrehsantos@gmail.com)
3. Complete profile setup

## 2. Create Product

1. Click **"New Product"**
2. Select **"Digital Product"**
3. Fill in:
   - **Name**: Papagaio - Voice-to-Text Input
   - **Price**: $29 (or your preferred price)
   - **URL**: `papagaio` (creates bulvee.gumroad.com/l/papagaio)

4. **Description** (copy this):
```
Papagaio - Voice-to-Text Input

Transform your voice into text instantly! Papagaio uses advanced Whisper AI
for accurate speech recognition that works with any application.

✅ Features:
- High-accuracy voice recognition (Whisper AI)
- Works with ANY application
- Configurable hotkey (default: Ctrl+Shift+Alt+V)
- Automatic silence detection
- Multiple languages supported
- System tray integration
- 7-day free trial included

✅ Platforms:
- Linux (DEB, RPM, AppImage, Flatpak)
- Windows (MSI installer)
- macOS (Homebrew)

✅ What you get:
- Lifetime license (one-time payment)
- Free updates
- Email support

After purchase, you'll receive a license key to activate Papagaio.
```

5. **Content/Files**: No files needed (license key is delivered automatically)

## 3. Enable License Keys

This is the most important step!

1. In product settings, go to **"Content"** tab
2. Scroll to **"License key"** section
3. **Enable "Generate a unique license key"**
4. Save changes

Now every purchase automatically generates a license key.

## 4. Get Your Product ID

1. Go to your product page
2. Click **"Share"** or check the URL
3. Your product permalink is: `papagaio`

Update `papagaio_license.py` line 17:
```python
PRODUCT_ID = "papagaio"  # Your Gumroad product permalink
```

## 5. Test the License System

1. Make a test purchase (use Gumroad's test mode or buy your own product)
2. Copy the license key from the confirmation email
3. Run: `python3 papagaio-activate.py`
4. Enter the license key
5. Verify activation works

## 6. Update Purchase URL

In `papagaio-activate.py`, update line 16:
```python
PURCHASE_URL = "https://bulvee.gumroad.com/l/papagaio"
```

Replace `bulvee` with your Gumroad username if different.

## 7. Customize (Optional)

### Change Price
Edit in Gumroad product settings.

### Add Discount Codes
1. Go to product settings
2. Click "Offer codes"
3. Create codes like `LAUNCH50` for 50% off

### Set Up Affiliates
1. Go to Settings > Affiliates
2. Enable affiliate program
3. Set commission rate (e.g., 30%)

## 8. Payment Setup

1. Go to Settings > Payments
2. Connect PayPal or Stripe
3. Add payout method (bank account)

## API Verification

The license verification uses Gumroad's API:
```
POST https://api.gumroad.com/v2/licenses/verify
```

Parameters:
- `product_id`: Your product permalink (papagaio)
- `license_key`: Customer's license key
- `increment_uses_count`: false (for validation only)

Response includes:
- `success`: boolean
- `purchase.email`: buyer's email
- `uses`: number of activations

## Pricing Recommendations

| Market | Price | Notes |
|--------|-------|-------|
| Launch | $19 | Limited time offer |
| Standard | $29 | Regular price |
| Team/Business | $99 | Multiple machines |

## Support

- Email: support@bulvee.com
- GitHub Issues: https://github.com/alexandrehsantos/papagaio/issues

---

## Quick Checklist

- [ ] Gumroad account created
- [ ] Product created with correct details
- [ ] **License key generation ENABLED**
- [ ] Price set ($29 recommended)
- [ ] Description added
- [ ] Product ID updated in code
- [ ] Purchase URL updated in code
- [ ] Payment method connected
- [ ] Test purchase completed
