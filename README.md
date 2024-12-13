# TelegramManager

TelegramManager is a Python-based tool for managing Telegram groups and users using the Telethon library. This project aims to simplify tasks such as connecting to Telegram accounts, managing groups, and adding users.

## Features

- **Connect to Telegram**: Establish a secure connection using your Telegram API credentials.
- **Manage Groups**: Add or manage users in Telegram groups.
- **Asynchronous Operations**: Leverages Python's asynchronous capabilities for better performance.

## Prerequisites

1. **Python**: Make sure you have Python 3.8 or later installed.
2. **Telegram API Credentials**: You need a `api_id` and `api_hash`, which can be obtained from [Telegram's API Development Tools](https://my.telegram.org/apps).
3. **Dependencies**: Install required Python libraries (see below).

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/ilssear/TelegramManager.git
   cd TelegramManager
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure credentials:

   Replace the placeholders in the configuration JSON file (`config.json`) with your actual `api_id`, `api_hash`, and `phone` values. This file is not included in the repository to protect your credentials, but an example template is provided.

   ```txt # Example api_secrets.json:
   {
       "api_id": "your_api_id",
       "api_hash": "your_api_hash",
       "phone": "your_phone_number"
   }
   ```

## Usage

### Connecting to Telegram

Use the `t_connector.py` script to establish a connection to your Telegram account.

```bash
python t_connector.py
```

### Adding Users to a Group

Use the `t_addusers.py` script to add users to a specific Telegram group.

1. Open the script and configure the `source_group` and `target_group` variables with the appropriate Telegram group IDs.
2. Run the script:

   ```bash
   python t_addusers.py
   ```

### Notes

- Ensure the account used has the necessary permissions to add users to the target group.
- Handle Telegram's rate limits by spacing out operations to avoid bans or restrictions.

## Error Handling

- **Rate Limit Errors**: The script includes basic handling for `PeerFloodError`. If encountered, wait before retrying operations.
- **Invalid Input**: Validate group and user IDs to ensure they meet Telegram's expected formats.

## Contribution Guidelines

Contributions are welcome! If you'd like to contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes and push them to your fork.
4. Open a pull request with a detailed description of your changes.

## License

This project is licensed under a license that complies with Telegram's API terms. Ensure you review and follow Telegram's [Terms of Service](https://core.telegram.org/terms) when using this project.

## Acknowledgments

- Built with the [Telethon](https://github.com/LonamiWebs/Telethon) library.
- Inspired by the need to simplify Telegram group management.

## Troubleshooting

If you encounter any issues, feel free to open an issue in the repository or contact the maintainer.
