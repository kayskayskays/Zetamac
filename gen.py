
import discord
from discord.ext import commands
import random


class Defaults:

    def __init__(self):
        self.operator_list = ['+', '*', '-', '/']
        self.add = ([2, 100], [2, 100])
        self.multiply = ([2, 12], [2, 100])

    def set_add(self, add: tuple[list[int, int], list[int, int]]):
        self.add = add

    def set_multiply(self, multiply: tuple[list[int, int], list[int, int]]):
        self.multiply = multiply

    def set_operator_list(self, operator_list: list[str]):
        self.operator_list = operator_list


defaults = Defaults()


def swap(minimum: int, maximum: int):
    minimum += maximum
    maximum = minimum - maximum
    minimum -= maximum
    return minimum, maximum


def generate() -> tuple[int, int, str]:
    first = 0
    second = 0

    operator = random.choice(defaults.operator_list)

    if operator == '+' or operator == '-':
        first = random.randint(*defaults.add[0])
        second = random.randint(*defaults.add[1])
    elif operator == '*' or operator == '/':
        first = random.randint(*defaults.multiply[0])
        second = random.randint(*defaults.multiply[1])

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

        options = [
            discord.SelectOption(
                label="+",
                description="Addition",
                default='+' in defaults.operator_list
            ),
            discord.SelectOption(
                label="-",
                description="Subtraction",
                default='-' in defaults.operator_list
            ),
            discord.SelectOption(
                label="*",
                description="Multiplication",
                default='*' in defaults.operator_list
            ),
            discord.SelectOption(
                label='/',
                description="Division",
                default='/' in defaults.operator_list
            )
        ]
        super().__init__(placeholder='+ - * /', min_values=1, max_values=4, options=options)

    async def callback(self, interaction):
        defaults.set_operator_list(self.values)
        operator_string = " "
        for operator in self.values:
            operator_string += operator + ' '
        operator_string = operator_string[:-1]
        await interaction.response.send_message(f'{interaction.user.name} chose {operator_string}', ephemeral=False)


class OperatorView(discord.ui.View):

    def __init__(self):
        super().__init__()

        self.add_item(OperatorSelect())


class GameFlags(commands.FlagConverter, delimiter=' ', prefix='-'):
    mode: str = 'default'
    points: int = 5
    time: int = 120
    timeout: int = 15
