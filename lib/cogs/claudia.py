import re

import discord
from discord.ext.commands import Cog, command, Context
from lib.utils import llm
from pathlib import Path

from lib.bot import Bot


class Claudia(Cog):
    def __init__(self, bot):
        self.bot: Bot = bot
        self.role_desc = Path("res/claudia_prompt.txt") \
            .read_text() \
            .replace("\n", " ") \
            .strip()

    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("Claudia enabled!")

    @command()
    async def claudia(self, ctx: Context, *, prompt):

        file_paths = []
        for a in ctx.message.attachments:
            if a.content_type not in ["application/pdf", "text/plain"]:
                return await ctx.reply("Please only upload PDF or TXT files.", mention_author=False)
            file_path = f"/tmp/{a.filename}"
            await a.save(file_path)
            file_paths.append(file_path)

        response, costs = llm.claude(self.bot).get_response(self.role_desc, prompt, file_paths)
        if len(response) > 1000:
            with open("/tmp/claudia.txt", "w") as f:
                f.write(response)
            message = f"||Diese Nachricht hat {costs:.2f}ct gekostet||"
            return await ctx.reply(message, file=discord.File("/tmp/claudia.txt"), mention_author=False)
        else:
            message = f"{response}\n\n||Diese Nachricht hat {costs:.2f}ct gekostet||"
            return await ctx.reply(message, mention_author=False)


def setup(bot):
    bot.add_cog(Claudia(bot))
