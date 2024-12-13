
# Copyright (C) Jim Moraga, 2024
# https://github.com/ilssear/TelegramManager

# Example api_secrets.json:
# {
#     "api_id": "your_api_id",
#     "api_hash": "your_api_hash",
#     "phone": "your_phone_number"
# }


# import asyncio
import json
import logging
from telethon.sync import TelegramClient
from telethon.errors.rpcerrorlist import (
    FloodWaitError,
    PeerFloodError,
    UserPrivacyRestrictedError,
    ChatWriteForbiddenError,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramConnector:
    def __init__(self, secrets_file: str):
        """
        Initialize the TelegramConnector.

        Args:
            secrets_file (str): Path to the JSON file containing API credentials.
        """
        with open(secrets_file, 'r') as file:
            secrets = json.load(file)
        self.api_id = secrets['api_id']
        self.api_hash = secrets['api_hash']
        self.phone = secrets['phone']
        self.client = TelegramClient('session_name', self.api_id, self.api_hash)
        self._cached_group_types = {}

    async def connect(self) -> None:
        """
        Establish a connection to Telegram.
        """
        await self.client.start(self.phone)
        logger.info("Connected to Telegram.")
        try:
            me = await self.client.get_me()
            self.id = me.id
            user_name = self.get_user_display_name(me)
            logger.info(f"Logged in as {user_name} ({me.id})")
        except Exception as e:
            logger.error(f"Unexpected error with account: {e}")

    async def is_account_operational(self) -> bool:
        """
        Verify if the account is operational and unrestricted.

        Returns:
            bool: True if the account is operational, False if restrictions are detected.
        """
        try:
            await self.client.get_me()
            logger.info("Your account is active and operational.")
            return True
        except FloodWaitError as e:
            logger.warning(f"Flood wait restriction in effect. Wait for {e.seconds} seconds.")
            return False
        except PeerFloodError:
            logger.warning("Too many requests detected. Avoid further actions to prevent a temporary ban.")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while checking account status: {e}")
            return False

    async def has_api_rate_limits(self) -> bool:
        """
        Check if the API is under rate limits.

        Returns:
            bool: True if no rate limits are detected, False otherwise.
        """
        try:
            dialogs = await self.client.get_dialogs()
            logger.info(f"Fetched {len(dialogs)} dialogs successfully.")
            
            for dialog in dialogs:
                if dialog.is_group:
                    print(f"Group Name: {dialog.name}")
                    print(f"Group ID: {dialog.id}")
                    print(f"Group Type: {await self.get_group_type(dialog.id, verbose = False)}")
                    if hasattr(dialog.entity, 'access_hash'):
                        print(f"Access Hash: {dialog.entity.access_hash}")
                    else:
                        print("No Access Hash (likely a basic group)")
                elif dialog.is_channel:
                    print(f"Channel Name: {dialog.name}")
                    print(f"Channel ID: {dialog.id}")
                    print(f"Channel Type: {await self.get_group_type(dialog.id, verbose = False)}")
                    print(f"Access Hash: {dialog.entity.access_hash}")
                else:
                    continue
                print("-" * 40)
            return True
        except FloodWaitError as e:
            logger.warning(f"Flood wait detected. Retry after {e.seconds} seconds.")
            return False
        except PeerFloodError:
            logger.warning("Too many requests detected. Avoid further actions to prevent a temporary ban.")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while checking API limits: {e}")
            return False

    async def can_access_user(self, user_id: int = None) -> bool:
        """
        Check if a specific user can be accessed without restrictions.

        Args:
            user_id (int, optional): The user ID to check. Defaults to the account's ID.

        Returns:
            bool: True if the user is accessible, False otherwise.
        """
        user_id = user_id if user_id else self.id
        try:
            user = await self.client.get_entity(user_id)
            user_name = self.get_user_display_name(user)
            logger.info(f"User Info:\n\tID: {user.id}\n\tUsername: {user_name}")
            logger.info("The user does not appear to have any restrictions.")
            return True
        except UserPrivacyRestrictedError:
            logger.warning(f"User {user_id} has privacy restrictions preventing access.")
            return False
        except Exception as e:
            logger.error(f"Unexpected error with user {user_id}: {e}")
            return False

    async def can_write_to_group(self, group_id: int) -> bool:
        """
        Check if the bot has write permissions in a group or channel.

        Args:
            group_id (int): The group or channel ID to check.

        Returns:
            bool: True if write permissions are available, False otherwise.
        """
        try:
            group = await self.client.get_entity(group_id)
            logger.info(f"Group Info ({group_id}):\n\tID: {group.id}\n\tTitle: {group.title}")
            logger.info("The group does not appear to have any restrictions.")
            return True
        except ChatWriteForbiddenError:
            logger.warning(f"You do not have write permissions in the group {group_id}.")
            return False
        except Exception as e:
            logger.error(f"Unexpected error with group {group_id}: {e}")
            return False

    async def get_group_type(self, group_id: int, verbose: bool = True) -> str:
        """
        Identifies the type of a Telegram group or channel.

        Args:
            group_id (int): Telegram ID or username of the group.
            verbose (bool): Whether to log the group type. Defaults to True.

        Returns:
            str: The type of the group ('basic_group', 'supergroup', 'channel').
        """
        if group_id in self._cached_group_types:
            return self._cached_group_types[group_id]
        entity = await self.client.get_entity(group_id)
        try:
            if entity.megagroup:
                group_type = "supergroup"
            elif entity.broadcast:
                group_type = "channel"
            else:
                group_type = "basic_group"
            self._cached_group_types[group_id] = group_type
        except Exception as e:
            group_type = "chat"
        if verbose:
            logger.info(f"Group {entity.title} is a {group_type}.")
        return group_type

    async def disconnect(self) -> None:
        """
        Disconnect from Telegram.
        """
        await self.client.disconnect()
        logger.info("Disconnected from Telegram.")
    
    @staticmethod
    def get_user_display_name(user) -> str:
        """
        Generate a display name for a user.

        Args:
            user: The user entity from Telegram.

        Returns:
            str: A readable display name for the user.
        """
        return user.username or f"{user.first_name or ''} {user.last_name or ''}".strip() or "Unknown User"



# Example usage
if __name__ == "__main__":
    secrets_file = 'api_secrets.json'
    checker = TelegramConnector(secrets_file)

    async def main():
        await checker.connect()
        await checker.is_account_operational()
        await checker.has_api_rate_limits()
        # Replace with a valid user ID and group ID to check
        await checker.can_access_user(user_id=5724659429)
        await checker.can_write_to_group(group_id=-1002433161186)
        await checker.disconnect()

    import asyncio
    asyncio.run(main())
