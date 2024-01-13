import json
import html
import requests
import discord
from discord.ui import Button
from discord.ext import commands

from custom_view import CustomView
from helper import get_embed, shuffle_choices


class TriviaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="trivia",
        description="Get a trivia question for 5 coins, answer correctly and win.",
    )
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def trivia(self, ctx: commands.Context):
        player = self.bot.player_service.get_player(ctx.author.id)
        self.bot.player_service.remove_coins(player, 5)

        trivia = get_trivia()

        time_to_complete = 30
        question = trivia["question"]
        incorrect_answers = trivia["incorrect_answers"]
        correct_answer = trivia["correct_answer"]
        category = trivia["category"]
        difficulty = trivia["difficulty"]

        difficulty_colors_map = {
            "easy": discord.Color.green(),
            "medium": discord.Color.orange(),
            "hard": discord.Color.red(),
        }

        difficulty_coins_map = {"easy": 10, "medium": 15, "hard": 20}

        answers = shuffle_choices(incorrect_answers + [correct_answer])
        answers_numbered = [f"{i+1}. {a}" for i, a in enumerate(answers)]
        answers_string = "\n".join(answers_numbered)

        embed = get_embed(
            question,
            (
                f"Time: {time_to_complete} seconds\n"
                f"Category: {category}\n"
                f"Difficulty: {difficulty}\n\n"
                f"{answers_string}"
            ),
            difficulty_colors_map.get(difficulty, 0xFFFFFF),
        )

        view = CustomView(time_to_complete)

        async def button_callback(interaction: discord.Interaction):
            if interaction.user.id != ctx.author.id:
                return

            player = self.bot.player_service.get_player(ctx.author.id)

            selected_answer = interaction.data["custom_id"]

            if selected_answer == correct_answer:
                for button in view.children:
                    if button.custom_id == correct_answer:
                        button.style = discord.ButtonStyle.success
                    button.disabled = True

                nr_coins = difficulty_coins_map.get(difficulty, 0)
                response = f"Correct! You get {nr_coins} coins"
                self.bot.player_service.add_coins(player, nr_coins)

            else:
                for button in view.children:
                    if button.custom_id == selected_answer:
                        button.style = discord.ButtonStyle.danger
                    button.disabled = True
                response = "Wrong. The correct answer was " + correct_answer

            await interaction.response.edit_message(view=view)
            await ctx.send(content=response)

        for index, answer in enumerate(answers):
            row = index // 2
            button = Button(label=index + 1, custom_id=answer, row=row)
            button.callback = button_callback
            view.add_item(button)

        view.message = await ctx.send(embed=embed, view=view)

    @trivia.error
    async def trivia_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(content=f"`trivia` error: {error}")


def decode_html_entities(obj):
    if isinstance(obj, str):
        return html.unescape(obj)
    elif isinstance(obj, dict):
        return {key: decode_html_entities(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [decode_html_entities(element) for element in obj]
    else:
        return obj


def get_trivia():
    trivia_api = "https://opentdb.com/api.php?amount=1&type=multiple"
    trivia_response = requests.get(trivia_api)
    trivia_dict = json.loads(trivia_response.content.decode("utf-8"))
    decoded_trivia = decode_html_entities(trivia_dict)
    return decoded_trivia["results"][0]
