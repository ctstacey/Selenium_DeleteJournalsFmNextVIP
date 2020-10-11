# What does this Python script do?

Uses Selenium (in Python) to:
- login<sup>1</sup> to the [_NextVIP_](https://www.concilio.app/nextvip) Application/webpage
- delete the specified _NextVIP_ Journal IDs one by one via the webpage interface
- log the entire process to the console<sup>2</sup> (Includes failures and reasons; like timeouts etc.)

<sup>1</sup> Users must enter their username and password. These are not stored.
<sup>2</sup> Script designed such that output may be _piped_ to a file.

# Usage

- Edit the `NextVIP()` function (in the script) to include the list of Journal IDs you want to delete.
- Comment out the `sys.exit()` failsafe in the `login()` method
- Run the script the same way you run other python scripts
  (ie. `python Selenium_DeleteJournalsFmNextVIP.py` - or similar - at the command prompt)

If the script fails to get a _webdriver_ you may have to download a newer driver version.
See the _webdriver_ folder for instructions.

# Why was this script written?

I was asked to delete several thousand Journal IDs by hand.
(ie. login and manually search for and delete each Journal ID)

This was estimated to take around **two weeks full-time**.

Instead I got permission to automate the process.

# Why isn't the code perfectly cleaned up?

The code was only intended to be used once.

Hence it's not perfectly cleaned up, named, re-factored etc.

# Why is this script archived here?

As a useful starting point for future Selenium work (a quick refresher of Selenium etc)
