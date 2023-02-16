
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import random
import asyncio
import time


def generate() -> tuple[int, int, str]:
    first = 0
    second = 0

    operator_list = ['+', '*', '-', '/']
    operator = random.choice(operator_list)

    if operator == '+' or operator == '-':
        first = random.randint(2, 100)
        second = random.randint(2, 100)
    elif operator == '*' or operator == '/':
        first = random.randint(2, 12)
        second = random.randint(2, 12)

    return int(first), int(second), operator


def generate_q(first: int, second: int, operator: str) -> tuple[int, int, int]:
    match operator:
        case '+':
            answer = first + second
            return first, second, answer
        case '-':
            answer = first + second
            second = random.choice([first, second])
            first = answer
            answer = first - second
            return first, second, answer
        case '*':
            answer = first * second
            return first, second, answer
        case '/':
            answer = first * second
            if second > 12:
                second = first
            elif first > 12:
                pass
            else:
                second = random.choice([first, second])
            first = answer
            answer = first // second
            return first, second, answer


def mode_switch(mode: str):
    match mode:
        case 'default':
            first, second, operator = generate()
            first, second, answer = generate_q(first, second, operator)
            return first, second, operator, answer
        case 'square':
            square = random.randint(2, 100)
            first, second, operator, answer = (int(square), int(square), '*', int(square)**2)
            return first, second, operator, answer


load_dotenv()

intents = discord.Intents(message_content=True, messages=True, guilds=True)
bot = commands.Bot(intents=intents, command_prefix='%')

token = os.getenv("TOKEN")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


modes = ['default', 'square']
is_running = False


@bot.command(name='p')
async def play_zeta(ctx, *args):
    global is_running
    if not is_running:
        is_running = True
        mode = 'default'
        points = 5

        for arg in args:
            if arg.isdigit():
                points = int(arg)
            else:
                mode = arg

        if mode not in modes:
            mode = 'default'

        if points > 100:
            points = 100

        score = 0
        answer = 0
        reply_message = 0

        while score < points:

            if score == 0:
                first, second, operator, answer = mode_switch(mode)
                await ctx.channel.send(f"{first} {operator} {second}?")

            remaining_time = 15.0

            while reply_message == 0 or reply_message.content != str(answer):
                try:
                    start_time = time.time()
                    reply_message = await bot.wait_for(
                        'message', timeout=remaining_time, check=lambda message: ctx.author == message.author)
                    elapsed_time = time.time() - start_time
                    if reply_message.content != str(answer):
                        remaining_time -= elapsed_time
                    else:
                        remaining_time = 15.0
                    if reply_message.content == "--q":
                        await ctx.channel.send(f"You quit. Points: {score}.")
                        is_running = False
                        return
                except asyncio.TimeoutError:
                    await ctx.channel.send(f"You ran out of time. Points: {score}.")
                    is_running = False
                    return

            score += 1

            if score >= 1 and score != points:
                first, second, operator, answer = mode_switch(mode)
                point_string = 'points'
                if score == 1:
                    point_string = 'point'
                await ctx.channel.send(f"Correct! {score} {point_string}. \n {first} {operator} {second}?")
            elif score == points:
                await ctx.channel.send("You win!")
                is_running = False
                return


@bot.command(name='m')
async def play_multi_zeta(ctx, *args):
    global is_running
    if not is_running:
        is_running = True
        mode = 'default'
        points = 5
    
        for arg in args:
            if arg.isdigit():
                points = int(arg)
            else:
                mode = arg
    
        if mode not in modes:
            mode = 'default'
    
        if points > 100:
            points = 100
    
        scores = {}
        answer = 0
        reply_message = 0
    
        while points not in scores.values():
    
            if not scores:
                first, second, operator, answer = mode_switch(mode)
                await ctx.channel.send(f"{first} {operator} {second}?")
    
            remaining_time = 15.0
    
            while reply_message == 0 or reply_message.content != str(answer):
                try:
                    start_time = time.time()
                    reply_message = await bot.wait_for('message', timeout=remaining_time)
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
                        is_running = False
                        return
                    if reply_message.content != str(answer):
                        remaining_time -= elapsed_time
                    else:
                        remaining_time = 15.0
                except asyncio.TimeoutError:
                    if scores:
                        winner = list(dict(sorted(scores.items(), key=lambda item: item[1])))[-1]
                        point_string = 'points'
                        if scores[winner] == 1:
                            point_string = 'point'
                        await ctx.channel.send(f"You ran out of time. {winner} wins with {scores[winner]} {point_string}.")
                        is_running = False
                        return
                    else:
                        await ctx.channel.send(f"You ran out of time.")
                        is_running = False
                        return
    
            name = reply_message.author.name
    
            if name in scores:
                scores[name] += 1
                if scores[name] == points:
                    await ctx.channel.send(f"{name} wins!")
                    is_running = False
                    return
                first, second, operator, answer = mode_switch(mode)
                await ctx.channel.send(f"{name} is correct. {scores[name]} points."
                                       f" \n{first} {operator} {second}?")
            else:
                scores[name] = 1
                if 1 == points:
                    await ctx.channel.send(f"{name} wins!")
                    is_running = False
                    return
                first, second, operator, answer = mode_switch(mode)
                await ctx.channel.send(f"{name} is correct. 1 point."
                                       f"\n {first} {operator} {second}?")


@bot.command(name='z')
async def play_timed_zeta(ctx, *args):
    global is_running
    if not is_running:
        is_running = True
        
        mode = 'default'
        elapsed_time = 0
        max_time = 120
    
        for arg in args:
            if arg.isdigit():
                max_time = int(arg)
            else:
                mode = arg
    
        if mode not in modes:
            mode = 'default'
    
        score = 0
        answer = 0
        reply_message = 0
    
        while elapsed_time < max_time:
    
            if score == 0:
                first, second, operator, answer = mode_switch(mode)
                await ctx.channel.send(f"{first} {operator} {second}?")
    
            while reply_message == 0 or reply_message.content != str(answer):
                if elapsed_time >= max_time:
                    await ctx.channel.send(f"You ran out of time. Points: {score}.")
                    is_running = False
                    return
                try:
                    start_time = time.time()
                    reply_message = await bot.wait_for(
                        'message', timeout=max_time - elapsed_time, check=lambda message: ctx.author == message.author)
                    elapsed_time += time.time() - start_time
                    if reply_message.content == "--q":
                        await ctx.channel.send(f"You quit. Points: {score}.")
                        is_running = False
                        return
                except asyncio.TimeoutError:
                    await ctx.channel.send(f"You ran out of time. Points: {score}.")
                    is_running = False
                    return
    
            score += 1
    
            if score == 1:
                first, second, operator, answer = mode_switch(mode)
                await ctx.channel.send(f"Correct! 1 point. \n {first} {operator} {second}?")
            else:
                first, second, operator, answer = mode_switch(mode)
                await ctx.channel.send(f"Correct! {score} points. \n{first} {operator} {second}?")
    
        await ctx.channel.send(f"You ran out of time. Points: {score}.")
        is_running = False
    

if __name__ == '__main__':
    bot.run(token)
