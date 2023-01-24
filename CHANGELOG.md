# Changelog

## Version 0.2 (2023-01-XX)

- have a progress bar for long-running commands when possible
- use [gspread](https://docs.gspread.org/) to handle the low-level GoogleAPI
- use [gspread-dataframe](https://gspread-dataframe.readthedocs.io/) to handle converting a worksheet into a dataframe
- timeout of 60s for PretalxAPI as it is really slow which caused a lot of timeout errors
- rename `*API` to `*Client` as it's rather a client for an API
- moved some functionality from `review` to `pretalx.utils`
- GSheetClient allows uploading dataframes to Google Sheets

## Version 0.1.1 (2023-01-16)

- fix typo `sent` -> `send` in MailClient

## Version 0.1 (2023-01-15)

- First alpha version to can be used
- Google client to retrieve Google Sheets implemented
- Pretalx client implement
- A very basic HelpDesk client (minimal functionality) implemented
- Basic e-mail client implemented to send mails via HelpDesk
- Central configuration management for secrets and credentials implemented
