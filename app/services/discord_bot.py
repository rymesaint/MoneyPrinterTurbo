import os
import asyncio
import discord
from loguru import logger
from app.config import config
from app.models.schema import VideoParams
from app.services import state as sm
from app.services import task as tm
from app.utils import utils

class HermesDiscordBot(discord.Client):
    def __init__(self, *args, **kwargs):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents, *args, **kwargs)
        
        # Safely parse channel_id
        channel_id_val = config.discord.get("channel_id", "")
        try:
            self.channel_id = int(channel_id_val) if channel_id_val else None
        except ValueError:
            logger.error(f"Invalid channel_id in config.toml: {channel_id_val}")
            self.channel_id = None

    async def on_ready(self):
        logger.info(f"🤖 Hermes Discord Bot logged in as {self.user}")
        if self.channel_id:
            channel = self.get_channel(self.channel_id)
            if channel:
                try:
                    await channel.send("🤖 **Hermes Video Generator Bot is online!**\nSend a message here to generate a video, or use `!generate <prompt>` in other channels.")
                except Exception as e:
                    logger.error(f"Failed to send welcome message: {e}")

    async def on_message(self, message):
        # Don't respond to ourselves
        if message.author == self.user:
            return

        is_dm = isinstance(message.channel, discord.DMChannel)
        
        # If channel_id is specified, only respond in that channel or in DMs (unless using explicit command prefix)
        content = message.content.strip()
        is_trigger = False
        prompt = ""

        if content.startswith("!generate "):
            prompt = content[len("!generate "):].strip()
            is_trigger = True
        elif self.channel_id and message.channel.id == self.channel_id:
            # Dedicated channel: any message is a prompt (unless starts with !)
            if not content.startswith("!"):
                prompt = content
                is_trigger = True

        if not is_trigger:
            return

        if not prompt:
            await message.reply("❌ Please provide a prompt/subject for the video.")
            return

        # Support format: !generate <prompt> [| voice: <voice>] [| aspect: <aspect>]
        voice_name = config.ui.get("voice_name", "")
        if not voice_name:
            voice_name = "en-US-AriaNeural-Female" # Fallback if config value is empty
        aspect = "9:16"
        
        parsed_prompt = prompt
        if "|" in prompt:
            parts = prompt.split("|")
            parsed_prompt = parts[0].strip()
            for part in parts[1:]:
                part = part.strip()
                if part.lower().startswith("voice:"):
                    voice_name = part[len("voice:"):].strip()
                elif part.lower().startswith("aspect:"):
                    aspect = part[len("aspect:"):].strip()

        await message.reply(f"🎬 **Triggering Hermes video generation** for: *\"{parsed_prompt}\"* (aspect: `{aspect}`, voice: `{voice_name}`)...\nConfiguring pipeline...")

        # Create parameters
        params = VideoParams(
            video_subject=parsed_prompt,
            video_aspect=aspect,
            voice_name=voice_name,
            bgm_type="random",
            subtitle_enabled=True
        )

        task_id = utils.get_uuid()
        sm.state.update_task(task_id)

        try:
            # Dynamic import to prevent circular dependency
            from app.controllers.v1.video import task_manager
            
            task_manager.add_task(tm.start, task_id=task_id, params=params, stop_at="video")
            await message.channel.send(f"⏳ **Task created successfully!**\nTask ID: `{task_id}`\nStarting generation process...")
            
            # Start a background task to monitor progress
            asyncio.create_task(self.monitor_task(message.channel, task_id))
        except Exception as e:
            logger.error(f"Failed to start task via Discord: {e}")
            await message.channel.send(f"❌ **Error starting task:** {str(e)}")

    async def monitor_task(self, channel, task_id):
        last_progress = -1
        progress_message = None
        
        while True:
            await asyncio.sleep(3)
            task = sm.state.get_task(task_id)
            if not task:
                if progress_message:
                    await progress_message.edit(content=f"❌ Task `{task_id}` was lost or deleted.")
                else:
                    await channel.send(f"❌ Task `{task_id}` was lost or deleted.")
                break

            state = task.get("state")
            progress = int(task.get("progress", 0))
            
            # Map progress percentage to human-friendly stages
            stage_desc = "Initializing..."
            if progress >= 50:
                stage_desc = "Rendering and combining final video..."
            elif progress >= 40:
                stage_desc = "Gathering video materials..."
            elif progress >= 30:
                stage_desc = "Generating subtitles..."
            elif progress >= 20:
                stage_desc = "Generating voice audio..."
            elif progress >= 10:
                stage_desc = "Generating search keywords..."
            elif progress >= 5:
                stage_desc = "Generating video script..."

            if progress != last_progress:
                last_progress = progress
                # Create a simple visual progress bar
                bar_length = 10
                filled = int(progress / 10)
                bar = "█" * filled + "░" * (bar_length - filled)
                status_text = f"⏳ **Generating Video**\nProgress: `{progress}%` | [{bar}]\nStage: *{stage_desc}*"
                
                try:
                    if not progress_message:
                        progress_message = await channel.send(status_text)
                    else:
                        await progress_message.edit(content=status_text)
                except Exception as e:
                    logger.error(f"Failed to update Discord progress message: {e}")

            if state == "complete":
                videos = task.get("videos", [])
                youtube_results = task.get("youtube_results", [])
                
                # Delete the progress message
                if progress_message:
                    try:
                        await progress_message.delete()
                    except Exception:
                        pass

                msg = f"✅ **Video Generation Complete!**\nTask ID: `{task_id}`\n"
                
                if youtube_results:
                    for yt_res in youtube_results:
                        if yt_res.get("success"):
                            msg += f"📺 **Uploaded to YouTube Shorts:** https://youtube.com/shorts/{yt_res.get('video_id')}\n"
                        else:
                            msg += f"⚠️ **YouTube Upload Failed:** {yt_res.get('error')}\n"
                
                if videos:
                    endpoint = config.app.get("endpoint", "")
                    if endpoint:
                        video_path = videos[0]
                        relative_path = os.path.relpath(video_path, utils.task_dir()).replace("\\", "/")
                        download_url = f"{endpoint.rstrip('/')}/tasks/{relative_path}"
                        msg += f"🔗 **Download link:** {download_url}\n"
                
                await channel.send(msg)
                break

            elif state == "failed":
                if progress_message:
                    try:
                        await progress_message.delete()
                    except Exception:
                        pass
                await channel.send(f"❌ **Video Generation Failed** for Task `{task_id}`. Please check logs.")
                break


discord_client = None

async def start_discord_bot():
    global discord_client
    bot_token = config.discord.get("bot_token", "").strip()
    if not bot_token:
        logger.error("Discord Bot token is not configured in config.toml!")
        return

    logger.info("Initializing Hermes Discord Bot client...")
    discord_client = HermesDiscordBot()
    try:
        await discord_client.start(bot_token)
    except Exception as e:
        logger.error(f"Failed to run Hermes Discord Bot: {e}")
