import random
import string

import discord
from discord.ext import commands


import os
import json
from datetime import date

config = {
    'token': 'Your token',
    'prefix': '$',
}

intents = discord.Intents.all()

bot = commands.Bot(command_prefix=config['prefix'], intents=intents)
""" 
Создаёт объект класса Bot. 
command_pefix : символ, используемый для обращения к боту.
intents : включенные разрешения для бота
"""


@bot.command()
async def roll(ctx, *arg):
    """
    Отвечает случайным числом от 0 до 100.
    :param ctx: контекст, вызвавший команду.
    :param arg: переданные аргументы.
    """
    await ctx.reply(random.randint(0, 100))


@bot.command()
async def ping(ctx):
    """
    Отвечает на команду сообщением 'pong!'.
    :param ctx: контекст, вызвавший команду.
    """
    await ctx.send('pong!')


@bot.event
async def on_ready():
    """
    При запуске бота выводит в консоль имя, ID, версию Discord, а так же список серверов, на которых присутствует
    бот.
    """
    print('============')
    print('Logged in as')
    print(f'Bot Name: {bot.user.name}')
    print(f'Bot ID: {bot.user.id}')
    print(f'Discord version: {discord.__version__}')
    print('------------')
    print('Connected guild list:')
    for guild in bot.guilds:
        print(guild.name, "\tID:", guild.id)
    print('============')


@bot.event
async def on_guild_join(guild):
    """
    При подключению к серверу, записывает в JSON файл информацию о пригласившем бота пользователе (его ID и имя) и
    информацию о сервере (название, ID сервера, ID владельца сервера).
    :param guild: сервер, к которому подключается бот.
    :return: None.
    """
    # get all server integrations
    integrations = await guild.integrations()

    for integration in integrations:
        if isinstance(integration, discord.BotIntegration):
            if integration.application.user.name == bot.user.name:
                guild = integration.guild
                bot_inviter = integration.user  # возвращает discord.User объект
                log_dict = {'inviter': bot_inviter.name,
                           'inviter_id': bot_inviter.id,
                           'guild': guild.name,
                           'guild_id': guild.id,
                           'guild_owner': guild.owner.name,
                           'guild_owner_id': guild.owner_id,
                           }
                with open(f'{bot_inviter.name}_invite_{date.today()}.json', 'w') as filehandler:
                    json.dump(log_dict, filehandler)

                print('New guild connected. JSON log file created.')


@bot.command()
async def info(ctx, member: discord.Member = None):
    """
    Отправляет в чат информацию о пользователе (Имя, ID, текущую активность, статус, роль, дату создания аккаунта).
    Если был упомянут пользователь, то отправит информацию о нём, если не был, информацию о авторе сообщения.
    :param ctx: контекст, вызвавший команду.
    :param member: упомянутый пользователь, по умолчанию None.
    """
    await ctx.message.delete()
    if member == None:
        emb = discord.Embed(title="Информация о пользователе", color=ctx.message.author.color)
        emb.add_field(name="Имя:", value=ctx.message.author.display_name,inline=False)
        emb.add_field(name="Айди пользователя:", value=ctx.message.author.id,inline=False)
        t = ctx.message.author.status
        if t == discord.Status.online:
            d = " В сети"

        t = ctx.message.author.status
        if t == discord.Status.offline:
            d = "⚪ Не в сети"

        t = ctx.message.author.status
        if t == discord.Status.idle:
            d = " Не активен"

        t = ctx.message.author.status
        if t == discord.Status.dnd:
            d = " Не беспокоить"

        emb.add_field(name="Активность:", value=d, inline=False)
        emb.add_field(name="Статус:", value=ctx.message.author.activity, inline=False)
        emb.add_field(name="Роль на сервере:", value=f"{ctx.message.author.top_role.mention}", inline=False)
        emb.add_field(name="Акаунт был создан:", value=ctx.message.author.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"), inline=False)
        emb.set_thumbnail(url=ctx.message.author.avatar)
        await ctx.send(embed=emb)
    else:
        emb = discord.Embed(title="Информация о пользователе", color=member.color)
        emb.add_field(name="Имя:", value=member.display_name, inline=False)
        emb.add_field(name="Айди пользователя:", value=member.id, inline=False)
        t = member.status
        if t == discord.Status.online:
            d = " В сети"

        t = member.status
        if t == discord.Status.offline:
            d = "⚪ Не в сети"

        t = member.status
        if t == discord.Status.idle:
            d = " Не активен"

        t = member.status
        if t == discord.Status.dnd:
            d = " Не беспокоить"
        emb.add_field(name="Активность:", value=d, inline=False)
        emb.add_field(name="Статус:", value=member.activity, inline=False)
        emb.add_field(name="Роль на сервере:", value=f"{member.top_role.mention}", inline=False)
        emb.add_field(name="Акаунт был создан:", value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"), inline=False)
        emb.set_thumbnail(url=member.avatar)
        await ctx.send(embed=emb)


@bot.event
async def on_message(message):
    """
    Обрабатывает отправленные в чат сообщения на наличие в них запрещенной лексики, указанной в файле censure.json
    :param message: объект сообщения, хранит в себе автора, канал, содержание.
    """
    if {i.lower().translate(str.maketrans('', '', string.punctuation)) for i in message.content.split(' ')}\
            .intersection(set(json.load(open('censure.json')))) != set():
        await message.channel.send(f'{message.author.mention}, недопустимая лексика!')
        await message.delete()
    await bot.process_commands(message)


bot.run(os.getenv('TOKEN'))
"""Запускает бота, в аргументы передаётся токен бота."""


