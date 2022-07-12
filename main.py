import discord
from dotenv import load_dotenv
import subprocess
import tempfile
import traceback
import os

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()
temp_dir = tempfile.mkdtemp()

@client.event
async def on_ready():
    print(client.guilds)
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if len(message.attachments) > 0:
        if message.attachments[0].url.endswith('webm'):
            try:
                await message.channel.send("One moment please...")
                await message.attachments[0].save(f"{temp_dir}/attachment.webm")
                # NOTE: Important part here is just 800k. This is to try and get the output mp4 to hit a taget bitrate of 800k so it's not too much larger than the webm.
                #       This seemed to happen occasionally with the default ffmpeg settings
                subprocess.call(f"ffmpeg -y -i {temp_dir}/attachment.webm -c:v libx264 -b:v 800k -preset slower {temp_dir}/attachment.mp4", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
                await message.channel.send("", file=discord.File(f"{temp_dir}/attachment.mp4"))
            except Exception as err:
                tb_str = traceback.format_exc()
                message = f"Failed to convert. Reason: {tb_str}"
                await message.channel.send(message)
            finally:
                if os.path.exists(f"{temp_dir}/attachment.webm"):
                    os.remove(f"{temp_dir}/attachment.webm")
                if os.path.exists(f"{temp_dir}/attachment.mp4"):
                    os.remove(f"{temp_dir}/attachment.mp4")


client.run(TOKEN)
