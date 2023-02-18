
import discord
from discord.ext import commands
import random
import asyncio
import time


class Defaults:

    def __init__(self):
        self.operator_list = ['+', '*', '-', '/']
        self.add_one = [2, 100]
        self.add_two = [2, 100]
        self.multiply_one = [2, 12]
        self.multiply_two = [2, 100]

    def set_add_one(self, add_one):
        self.add_one = add_one

    def set_add_two(self, add_two):
        self.add_two = add_two

    def set_multiply_one(self, multiply_one):
        self.multiply_one = multiply_one

    def set_multiply_two(self, multiply_two):
        self.multiply_two = multiply_two

    def set_operator_list(self, operator_list):
        self.operator_list = operator_list

    def get_add_one(self):
        return self.add_one

    def get_add_two(self):
        return self.add_two

    def get_multiply_one(self):
        return self.multiply_one

    def get_multiply_two(self):
        return self.multiply_two

    def get_operator_list(self):
        return self.operator_list


defaults = Defaults()


def swap(minimum: int, maximum: int):
    minimum += maximum
    maximum = minimum - maximum
    minimum -= maximum
    return minimum, maximum


def generate() -> tuple[int, int, str]:
    first = 0
    second = 0

    operator = random.choice(defaults.get_operator_list())

    if operator == '+' or operator == '-':
        first = random.randint(*defaults.get_add_one())
        second = random.randint(*defaults.get_add_two())
    elif operator == '*' or operator == '/':
        first = random.randint(*defaults.get_multiply_one())
        second = random.randint(*defaults.get_multiply_two())

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
            first, second, operator, answer = (int(square), int(square), '*', int(square) ** 2)
            return first, second, operator, answer
        case 'zeta':
            first, second, operator = generate()
            first, second, answer = generate_q(first, second, operator)
            return first, second, operator, answer


class OperatorSelect(discord.ui.Select):

    def __init__(self):
        default_plus = '+' in defaults.get_operator_list()
        default_minus = '-' in defaults.get_operator_list()
        default_x = '*' in defaults.get_operator_list()
        default_div = '/' in defaults.get_operator_list()

        options = [
            discord.SelectOption(
                label="+",
                description="Addition",
                default=default_plus
            ),
            discord.SelectOption(
                label="-",
                description="Subtraction",
                default=default_minus
            ),
            discord.SelectOption(
                label="*",
                description="Multiplication",
                default=default_x
            ),
            discord.SelectOption(
                label='/',
                description="Division",
                default=default_div
            )
        ]
        super().__init__(placeholder='+ - * /', min_values=1, max_values=4, options=options)

    async def callback(self, interaction):
        defaults.set_operator_list(self.values)
        operator_string = " "
        for operator in self.values:
            operator_string += operator + ' '
        operator_string = operator_string[:-1]
        await interaction.response.send_message(f"You chose {operator_string}.", ephemeral=True)


class OperatorView(discord.ui.View):

    def __init__(self):
        super().__init__()

        self.add_item(OperatorSelect())


class GameFlags(commands.FlagConverter, delimiter=' ', prefix='-'):
    mode: str = 'default'
    points: int = 5
    time: int = 120

