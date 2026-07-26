import os
import asyncio
import logging
import importlib
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

from database.database import init_db, close_db
from utils.logger import setup_logger

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")
ADMIN_ROLE_ID = os.getenv("ADMIN_ROLE_ID")
LOG_CHANNEL_ID = os.getenv("LOG_CHANNEL_ID")

if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN não configurado no .env")

logger = setup_logger()

class CidadeNexusBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        intents.guilds = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

        self.guild_id = int(GUILD_ID) if GUILD_ID else None
        self.admin_role_id = int(ADMIN_ROLE_ID) if ADMIN_ROLE_ID else None
        self.log_channel_id = int(LOG_CHANNEL_ID) if LOG_CHANNEL_ID else None

    async def setup_hook(self):
        await init_db()
        logger.info("Banco de dados conectado.")

        await self.load_cogs()

        if self.guild_id:
            guild = discord.Object(id=self.guild_id)
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            logger.info(f"Slash commands sincronizados no servidor de desenvolvimento: {len(synced)} comandos")
        else:
            synced = await self.tree.sync()
            logger.info(f"Slash commands sincronizados globalmente: {len(synced)} comandos")

    async def load_cogs(self):
        cogs_dir = Path(__file__).parent / "cogs"
        loaded = 0
        failed = 0

        for file in sorted(cogs_dir.glob("*.py")):
            if file.name.startswith("_"):
                continue

            cog_name = f"cogs.{file.stem}"
            try:
                await self.load_extension(cog_name)
                logger.info(f"Cog carregado: {cog_name}")
                loaded += 1
            except Exception as e:
                logger.error(f"Falha ao carregar Cog {cog_name}: {e}")
                failed += 1

        logger.info(f"Cogs carregados: {loaded} | Falhas: {failed}")

    async def on_ready(self):
        logger.info(f"Bot conectado como {self.user} (ID: {self.user.id})")
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="Cidade Nexus 🏙️"
        )
        await self.change_presence(activity=activity)

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        logger.error(f"Erro no comando: {error}")

    async def close(self):
        await close_db()
        await super().close()
        logger.info("Bot desconectado.")

async def start_api():
    """Inicia a API FastAPI em paralelo com o bot."""
    from api.app import app
    import uvicorn
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    bot = CidadeNexusBot()

    # Executa bot e API simultaneamente
    await asyncio.gather(
        bot.start(DISCORD_TOKEN),
        start_api()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Encerramento solicitado pelo usuário.")
    except Exception as e:
        logger.critical(f"Erro fatal: {e}")
