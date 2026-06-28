# TravelEase - Online Bus & Flight Ticket Booking System

TravelEase is a Django-based web application for booking bus and flight tickets online. It includes user registration with email OTP verification and booking confirmations.

## Email Configuration Setup

The email system is configured to send OTP codes and booking confirmations. For local development, if credentials are not configured, Django automatically falls back to the **console backend** (printing emails in the terminal) to prevent development interruption.

To enable live email sending via Gmail SMTP, follow these steps:

### 1. Generate a Gmail App Password

Standard Gmail passwords do not work with SMTP/apps. You must create an **App Password**:

1. Go to your [Google Account settings](https://myaccount.google.com/).
2. Enable **2-Step Verification** (required to generate App Passwords).
3. Search for **App passwords** in the search bar or go to Security > 2-Step Verification > App Passwords (at the bottom).
4. Create a new App Password (e.g., name it "TravelEase").
5. Copy the generated 16-character code (e.g., `xxxx xxxx xxxx xxxx`).

### 2. Configure Environment Variables

You can configure the email settings using local environment variables, Replit secrets, or a `.env` file.

#### Option A: Local Development (`.env` file)
Create a file named `.env` in the root of the project (next to `manage.py`) and add the following lines:

```env
# Email Configuration
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=your_email@gmail.com
```

> [!NOTE]
> The `.env` file is automatically ignored by Git (configured in `.gitignore`) to protect your credentials.
> Both the 16-character string with spaces (e.g. `abcd efgh ijkl mnop`) and without spaces (`abcdefghijklmnop`) are accepted; TravelEase will automatically sanitize and strip any whitespace.

#### Option B: Replit Deployment (Replit Secrets)
If you are running the project on Replit, do **not** use a `.env` file. Instead, use the Replit **Secrets** tool:
1. Open the **Secrets** pane on Replit.
2. Add the following key-value pairs:
   - `EMAIL_HOST_USER`: Your Gmail address (e.g., `your_email@gmail.com`)
   - `EMAIL_HOST_PASSWORD`: Your 16-character App Password (e.g., `abcd efgh ijkl mnop`)
   - `DEFAULT_FROM_EMAIL`: (Optional) Your Gmail address or custom from address

### 3. Verify Email Configuration

You can use the built-in diagnostic management command to verify if email configuration works:

```bash
# Replace with the email address you want to receive the test email at
python manage.py test_email recipient@example.com
```

This command will:
- Display the active email backend, host, port, TLS settings, and masked password for troubleshooting.
- Attempt to send a real test email to the recipient.
- Provide troubleshooting recommendations in case of errors.

## Development Features

- **Debug Fallback**: When `DEBUG = True` (in development), if `EMAIL_HOST_USER` or `EMAIL_HOST_PASSWORD` are missing, emails are printed directly to the terminal.
- **Robust Error Handling**: Real-time logging catches SMTP errors, so if email sending fails, the system logs the issue and allows users to proceed without causing application crashes.
