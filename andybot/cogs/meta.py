import math
import time
from typing import Tuple

import psutil
import discord
from discord.ext import commands

from andybot.utils.math import celsius_to_fahreinheit


class Meta(commands.Cog):
    """Cog for sending metadata about the bot, such as uptime."""

    def __init__(self, bot: discord.Client) -> None:
        self.bot = bot
        self.process = psutil.Process()

    @commands.Cog.listener()
    async def on_ready(self):
        print('andybot meta info displayer is ready.')

    @commands.command()
    async def uptime(self, ctx: commands.Context) -> None:
        """Sends the uptime of the bot in days, hours, minutes, and seconds."""
        seconds, minutes, hours, days = self._get_uptime()
        await ctx.send(
            f'I have been alive for {days} days, {hours % 24} hours,'
            f' {minutes % 60} minutes, and {seconds % 60} seconds.'
        )

    @commands.command(alias=['temp'])
    async def temperature(self, ctx: commands.Context) -> None:
        """Sends the temperature of the bot."""
        try:
            celsius, fahrenheit = self._get_temperature()
            msg = f'I am currently {celsius:.2f}°C, or {fahrenheit:.2f}°F.'
            if 41 <= celsius:
                msg += (
                    ' At that temperature, proteins denature. If I was a human,'
                    ' I would be dying! :)'
                )
            await ctx.send(msg)
        except (AttributeError, KeyError, IndexError):
            await ctx.send('Cannot get temperature info.')

    def _get_uptime(self) -> Tuple[int, int, int, int]:
        """Gets the uptime of the bot in days, hours, minutes, and seconds."""
        seconds = math.floor(time.time() - self.process.create_time())
        minutes = seconds // 60
        hours = seconds // 60
        days = seconds // 24
        return seconds, minutes, hours, days

    def _get_temperature(self) -> Tuple[int, int]:
        """Gets the temperature of the raspberry pi."""
        temp_info = psutil.sensors_temperatures()
        celsius = temp_info['cpu_thermal'][0].current
        return celsius, celsius_to_fahreinheit(celsius)


def setup(client: discord.Client) -> None:
    client.add_cog(Meta(client))
