# Copyright (C) Jim Moraga, 2024
# https://github.com/ilssear/TelegramManager

# Example api_secrets.json:
# {
#     "api_id": "your_api_id",
#     "api_hash": "your_api_hash",
#     "phone": "your_phone_number"
# }

import json
import asyncio
import random
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import AddChatUserRequest
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.errors import UserPrivacyRestrictedError, PeerFloodError, FloodWaitError
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramGroupManager:
    def __init__(self, secrets_file: str):
        """
        Initialize the TelegramGroupManager with API credentials from a secrets file.

        Args:
            secrets_file (str): Path to the JSON file containing Telegram API credentials.
        """
        try:
            # Load credentials from JSON file
            with open(secrets_file, 'r') as file:
                secrets = json.load(file)
            self._cached_group_types = {}
            self.api_id = secrets['api_id']
            self.api_hash = secrets['api_hash']
            self.phone = secrets['phone']
            self.client = TelegramClient('session_name', self.api_id, self.api_hash)
            # Start the client synchronously
            self.client.start(self.phone)
            logger.info("Telegram client started successfully.")
        except FileNotFoundError:
            logger.error(f"Secrets file not found: {secrets_file}")
            raise
        except KeyError as e:
            logger.error(f"Missing key in secrets file: {e}")
            raise
        except RPCError as e:
            logger.error(f"Failed to initialize Telegram client: {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred during initialization: {e}")
            raise

    async def get_group_type(self, group_id: int, verbose: bool = True) -> str:
        """
        Identifies the type of a Telegram group or channel.

        Args:
            group_id (int): Telegram ID or username of the group.
            verbose (bool): Whether to log the group type. Defaults to True.

        Returns:
            str: String representing the group type ('basic_group', 'supergroup', 'channel').
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

    async def add_users_from_group(self, source_group_id: int, target_group_id: int, users_to_skip: list[int] = None) -> None:
        """
        Adds users from a source group to a target group.

        Args:
            source_group_id (int): Telegram ID of the source group.
            target_group_id (int): Telegram ID of the target group.
            users_to_skip (list[int], optional): List of user IDs to exclude from the operation.
        """
        users_to_skip = set(users_to_skip or [])
        logger.info("Fetching members from source group...")
        source_members = await self.client.get_participants(source_group_id)
        logger.info(f"Source group members: {len(source_members)}")

        logger.info("Fetching members from target group...")
        target_members = await self.client.get_participants(target_group_id)
        logger.info(f"Target group members: {len(target_members)}")

        # Create a set of user IDs in the target group
        target_member_ids = {member.id for member in target_members}
        group_entity = await self.client.get_entity(target_group_id)
        group_name = group_entity.title

        # Filter members not in the target group and not in the skip list
        # Combine target members and users to skip into one set
        skip_ids = set(target_member_ids).union(users_to_skip)
        users_to_add = [
            member for member in source_members
            if member.id not in skip_ids
        ]
        logger.info(f"Users to add: {len(users_to_add)}")
        for member in users_to_add:
            user_name = member.username or f"{member.first_name or ''} {member.last_name or ''}".strip() or "Unknown User"
            print(f"User: {member.id}, Name: {user_name}")

        # Randomize the list of users to add
        random.shuffle(users_to_add)
        print("\n\nList of users shuffled.")

        # Identify the type of the target group
        target_group_type = await self.get_group_type(target_group_id, verbose=False)

        # Add users to the target group using the appropriate API
        for user in users_to_add:
            user_name = user.username or f"{user.first_name or ''} {user.last_name or ''}".strip() or "Unknown User"
            try:
                if target_group_type in ["basic_group", "chat"]:
                    logger.info(f"Adding {user_name} ({user.id}) to basic group ({group_name})...")
                    await self.client(AddChatUserRequest(chat_id=target_group_id, user_id=user.id, fwd_limit=0))
                else:  # supergroup or channel
                    logger.info(f"Inviting {user_name} ({user.id}) to {target_group_type} ({group_name})...")
                    await self.client(InviteToChannelRequest(channel=target_group_id, users=[user.id]))
            except UserPrivacyRestrictedError:
                logger.warning(f"Cannot add {user_name} ({user.id}): Privacy settings restricted.")
            except PeerFloodError:
                logger.error("Rate limit exceeded. Stopping to avoid ban.")
                break
            except FloodWaitError as e:
                logger.warning(f"Flood wait error: Sleeping for {e.seconds} seconds.")
                await asyncio.sleep(e.seconds)
            except Exception as e:
                logger.error(f"Error adding {user_name} ({user.id}): {e}")
            # Avoid hitting Telegram rate limits
            logger.info("Waiting (to mimic a human)....")
            await asyncio.sleep(random.uniform(60, 180))  # Sleep between 60 to 180 seconds
        logger.info("Process completed successfully.")

    def run(self, source_group_id: int, target_group_id: int, users_to_skip: list[int] = None) -> None:
        """
        Runs the async function to add users from one group to another.

        Args:
            source_group_id (int): Telegram ID of the source group.
            target_group_id (int): Telegram ID of the target group.
            users_to_skip (list[int], optional): List of user IDs to exclude from the operation.
        """
        self.client.loop.run_until_complete(
            self.add_users_from_group(source_group_id, target_group_id, users_to_skip)
        )

if __name__ == "__main__":
    secrets_file = "api_secrets.json"
    source_group_id = -1002433161186  # Source group ID (Old Quantum Wizards)
    target_group_id = -1002429973404  # Target group ID (New Quantum Wizards)
    users_to_skip = []  # User ID to skip (optional)

    manager = TelegramGroupManager(secrets_file)
    manager.run(source_group_id, target_group_id, users_to_skip)
