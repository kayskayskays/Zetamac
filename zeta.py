
import discord
from discord.ext import commands
import gen
from gen import defaults
import time
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents(message_content=True, messages=True, guilds=True)
bot = commands.Bot(intents=intents, command_prefix='%')

token = os.getenv("TOKEN")

# global variables
MODES = ['default', 'square']
is_running = False
bot.current_channels = set()


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")


@bot.command(aliases=['flavor', 'fl'])
async def flavour(ctx):
    view = gen.OperatorView()
    await ctx.send("Choose your operators:", view=view)


@bot.command(name='p')
async def play_zeta(ctx, *, flags: gen.GameFlags):
    if ctx.channel not in bot.current_channels:
        bot.current_channels.add(ctx.channel)
        mode = flags.mode
        points = flags.points

        if mode not in MODES:
            mode = 'default'

        if points > 100:
            points = 100

        score = 0
        answer = 0
        reply_message = 0
        end_message = 'You win!'

        while score < points:

            if score == 0:
                first, second, operator, answer = gen.mode_switch(mode)
                await ctx.channel.send(f"{first} {operator} {second}?")

            timeout = flags.timeout

            while reply_message == 0 or reply_message.content != str(answer):
                try:
                    start_time = time.time()
                    reply_message = await bot.wait_for(
                        'message', timeout=timeout, check=lambda message: ctx.author == message.author)
                    elapsed_time = time.time() - start_time
                    if reply_message.content != str(answer):
                        timeout -= elapsed_time
                    else:
                        timeout = flags.timeout
                    if reply_message.content == "--q":
                        await ctx.channel.send(f"You quit. Points: {score}.")
                        bot.current_channels.remove(ctx.channel)
                        return
                except asyncio.TimeoutError:
                    await ctx.channel.send(f"You ran out of time. Points: {score}.")
                    bot.current_channels.remove(ctx.channel)
                    return

            reply_message = 0
            score += 1

            if score >= 1 and score != points:
                first, second, operator, answer = gen.mode_switch(mode)
                point_string = 'points'
                if score == 1:
                    point_string = 'point'
                await ctx.channel.send(f"Correct! {score} {point_string}. \n {first} {operator} {second}?")
            elif score == points:
                await ctx.channel.send(end_message)
                bot.current_channels.remove(ctx.channel)
                return


@bot.command(name='m')
async def play_multi_zeta(ctx, *, flags: gen.GameFlags):
    if ctx.channel not in bot.current_channels:
        bot.current_channels.add(ctx.channel)

        mode = flags.mode
        points = flags.points

        if mode not in MODES:
            mode = 'default'

        if points > 100:
            points = 100

        scores = {}
        answer = 0
        reply_message = 0

        condition = points not in scores.values()

        while condition:

            if not scores:
                first, second, operator, answer = gen.mode_switch(mode)
                await ctx.channel.send(f"{first} {operator} {second}?")

            timeout = flags.timeout

            while reply_message == 0 or reply_message.content != str(answer):
                try:
                    start_time = time.time()
                    reply_message = await bot.wait_for('message', timeout=timeout)
                    elapsed_time = time.time() - start_time
                    if reply_message.content == "--q":
                        if scores:
                            winner = list(dict(sorted(scores.items(), key=lambda item: item[1])))[-1]
                            point_string = 'points'
                            if scores[winner] == 1:
                                point_string = 'point'
                            await ctx.channel.send(f"You quit. {winner} wins with {scores[winner]} {point_string}.")
                        else:
                            await ctx.channel.send(f"You quit.")
                        bot.current_channels.remove(ctx.channel)
                        return
                    if reply_message.content != str(answer):
                        timeout -= elapsed_time
                    else:
                        timeout = flags.timeout
                except asyncio.TimeoutError:
                    if scores:
                        winner = list(dict(sorted(scores.items(), key=lambda item: item[1])))[-1]
                        point_string = 'points'
                        if scores[winner] == 1:
                            point_string = 'point'
                        await ctx.channel.send(f"You ran out of time. {winner} wins with {scores[winner]} "
                                               f"{point_string}.")
                        bot.current_channels.remove(ctx.channel)
                        return
                    else:
                        await ctx.channel.send(f"You ran out of time.")
                        bot.current_channels.remove(ctx.channel)
                        return

            name = reply_message.author.name
            reply_message = 0

            if name in scores:
                scores[name] += 1
                if scores[name] == points:
                    await ctx.channel.send(f"{name} wins!")
                    bot.current_channels.remove(ctx.channel)
                    return
                first, second, operator, answer = gen.mode_switch(mode)
                await ctx.channel.send(f"{name} is correct. {scores[name]} points."
                                       f" \n{first} {operator} {second}?")
            else:
                scores[name] = 1
                if 1 == points:
                    await ctx.channel.send(f"{name} wins!")
                    bot.current_channels.remove(ctx.channel)
                    return
                first, second, operator, answer = gen.mode_switch(mode)
                await ctx.channel.send(f"{name} is correct. 1 point."
                                       f"\n {first} {operator} {second}?")


@bot.command(name='z')  # might be able to make this a mode
async def play_timed_zeta(ctx, *, flags: gen.GameFlags):
    if ctx.channel not in bot.current_channels:
        bot.current_channels.add(ctx.channel)

        elapsed_time = 0

        mode = flags.mode
        max_time = flags.time

        if mode not in MODES:
            mode = 'default'

        score = 0
        answer = 0
        reply_message = 0

        while elapsed_time < max_time:

            if score == 0:
                first, second, operator, answer = gen.mode_switch(mode)
                await ctx.channel.send(f"{first} {operator} {second}?")

            while reply_message == 0 or reply_message.content != str(answer):
                if elapsed_time >= max_time:
                    await ctx.channel.send(f"You ran out of time. Points: {score}.")
                    bot.current_channels.remove(ctx.channel)
                    return
                try:
                    start_time = time.time()
                    reply_message = await bot.wait_for(
                        'message', timeout=max_time - elapsed_time, check=lambda message: ctx.author == message.author)
                    elapsed_time += time.time() - start_time
                    if reply_message.content == "--q":
                        await ctx.channel.send(f"You quit. Points: {score}.")
                        bot.current_channels.remove(ctx.channel)
                        return
                except asyncio.TimeoutError:
                    await ctx.channel.send(f"You ran out of time. Points: {score}.")
                    bot.current_channels.remove(ctx.channel)
                    return

            reply_message = 0
            score += 1

            if score == 1:
                first, second, operator, answer = gen.mode_switch(mode)
                await ctx.channel.send(f"Correct! 1 point. \n {first} {operator} {second}?")
            else:
                first, second, operator, answer = gen.mode_switch(mode)
                await ctx.channel.send(f"Correct! {score} points. \n{first} {operator} {second}?")

        await ctx.channel.send(f"You ran out of time. Points: {score}.")
        bot.current_channels.remove(ctx.channel)


@bot.command(name='zm')
async def multiplayer_timed_zeta(ctx, *, flags: gen.GameFlags):
    if ctx.channel not in bot.current_channels:
        bot.current_channels.add(ctx.channel)

        elapsed_time = 0

        mode = flags.mode
        max_time = flags.time

        if mode not in MODES:
            mode = 'default'

        scores = {}
        answer = 0
        reply_message = 0

        while elapsed_time < max_time:

            if not scores:
                first, second, operator, answer = gen.mode_switch(mode)
                await ctx.channel.send(f"{first} {operator} {second}?")

            while reply_message == 0 or reply_message.content != str(answer):
                if elapsed_time >= max_time:
                    if scores:
                        winner = list(dict(sorted(scores.items(), key=lambda item: item[1])))[-1]
                        await ctx.channel.send(f'You ran out of time. {winner} wins with {scores[winner]} points.')
                    else:
                        await ctx.channel.send(f'You ran out of time.')
                    bot.current_channels.remove(ctx.channel)
                    return
                try:
                    start_time = time.time()
                    reply_message = await bot.wait_for(
                        'message', timeout=max_time - elapsed_time)
                    elapsed_time += time.time() - start_time
                    if reply_message.content == "--q":
                        if scores:
                            winner = list(dict(sorted(scores.items(), key=lambda item: item[1])))[-1]
                            await ctx.channel.send(f'You quit. {winner} wins with {scores[winner]} points.')
                        else:
                            await ctx.channel.send(f'You quit.')
                        bot.current_channels.remove(ctx.channel)
                        return
                except asyncio.TimeoutError:
                    if scores:
                        winner = list(dict(sorted(scores.items(), key=lambda item: item[1])))[-1]
                        await ctx.channel.send(f'You ran out of time. {winner} wins with {scores[winner]} points.')
                    else:
                        await ctx.channel.send(f'You ran out of time.')
                    bot.current_channels.remove(ctx.channel)
                    return

            name = reply_message.author.name
            if name in scores:
                scores[name] += 1
            else:
                scores[name] = 1

            if scores[name] == 1:
                first, second, operator, answer = gen.mode_switch(mode)
                await ctx.channel.send(f"{name} is correct. 1 point. \n {first} {operator} {second}?")
            else:
                first, second, operator, answer = gen.mode_switch(mode)
                await ctx.channel.send(f"{name} is correct. {scores[name]} points. \n{first} {operator} {second}?")

        if scores:
            winner = list(dict(sorted(scores.items(), key=lambda item: item[1])))[-1]
            await ctx.channel.send(f'You ran out of time. {winner} wins with {scores[winner]} points.')
        else:
            await ctx.channel.send(f'You ran out of time.')
        bot.current_channels.remove(ctx.channel)
        return


@bot.tree.command()
async def add(interaction: discord.Interaction, min_one: int = 2, max_one: int = 100, min_two: int = 2,
              max_two: int = 100):
    if interaction.channel not in bot.current_channels:
        bot.current_channels.add(interaction.channel)
        if min_one > max_one:
            min_one, max_one = gen.swap(min_one, max_one)
        if min_two > max_two:
            min_two, max_two = gen.swap(min_two, max_two)
        defaults.set_add_one((min_one, max_one))
        defaults.set_add_two((min_two, max_two))
        await interaction.response.send_message(f'+Range: ({defaults.get_add_one()[0]} to {defaults.get_add_one()[1]}) '
                                                f'+ ({defaults.get_add_two()[0]} to {defaults.get_add_two()[1]})',
                                                ephemeral=False)
        bot.current_channels.remove(interaction.channel)


@bot.tree.command()
async def multiply(interaction: discord.Interaction, min_one: int = 2, max_one: int = 12, min_two: int = 2,
                   max_two: int = 100):
    if interaction.channel not in bot.current_channels:
        bot.current_channels.add(interaction.channel)
        if min_one > max_one:
            min_one, max_one = gen.swap(min_one, max_one)
        if min_two > max_two:
            min_two, max_two = gen.swap(min_two, max_two)
        defaults.set_multiply_one((min_one, max_one))
        defaults.set_multiply_two((min_two, max_two))
        await interaction.response.send_message(f'\*Range: ({defaults.get_multiply_one()[0]} to '
                                                f'{defaults.get_multiply_one()[1]}) * '
                                                f'({defaults.get_multiply_two()[0]} to '
                                                f'{defaults.get_multiply_two()[1]})', ephemeral=False)
        bot.current_channels.remove(interaction.channel)

if __name__ == '__main__':
    bot.run(token)
