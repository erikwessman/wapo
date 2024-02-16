import os
import random
import json
import html
import requests
import logging
import asyncio
from fuzzywuzzy import fuzz
import discord
from discord.ui import Button
from discord.ext import commands

from custom_view import CustomView
from helper import get_embed, shuffle_choices


class TriviaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.movie_client = MovieDatabaseClient()
        self.movie_channel_dict = {}  # Maps a channel id to a movie

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
        if isinstance(error, commands.BadArgument):
            await ctx.send(content=f"`trivia` error: {error}")

    @commands.hybrid_command(name="movie", description="Guess the movie!")
    @commands.cooldown(1, 3600, commands.BucketType.channel)
    async def movie_trivia(self, ctx: commands.Context):
        movie = self.movie_client.get_random_movie()
        self.movie_channel_dict[ctx.channel.id] = movie
        embed = get_embed(
            "Movie Trivia!",
            "Starting in 10 seconds...",
            discord.Color.teal(),
        )
        message = await ctx.send(embed=embed)

        await asyncio.sleep(10)

        embed.description = "Guess the movie based on the image"
        embed.set_image(url=movie.backdrop_url)
        await message.edit(embed=embed)

    @movie_trivia.error
    async def movie_trivia_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(content=f"`movie` error: {error}")

    @commands.hybrid_command(name="hint", description="Get a hint for the movie.")
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def hint(self, ctx: commands.Context):
        movie = self.movie_channel_dict.get(ctx.channel.id)
        if movie:
            hint = self.movie_client.get_hint(movie)
            await ctx.send(content=hint)
        else:
            await ctx.send(content="No active movie trivia in this channel.")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.channel.id in self.movie_channel_dict:
            movie = self.movie_channel_dict[message.channel.id]
            player = self.bot.player_service.get_player(message.author.id)
            similarity_score = self.get_similarity_score(
                message.content, movie.name)

            if similarity_score >= 85:
                del self.movie_channel_dict[message.channel.id]
                self.bot.player_service.add_coins(player, 10)
                embed = get_embed(
                    f"Correct! The movie was {movie.name}",
                    f"Release Date: {movie.date}",
                    0x00FF00,
                )
                embed.add_field(
                    name="Reward", value="You get 10 coins!", inline=False)
                embed.set_image(url=movie.poster_url)
                await message.channel.send(embed=embed)

    def get_similarity_score(self, title1: str, title2: str) -> int:
        return fuzz.ratio(title1.lower(), title2.lower())


class Movie:
    def __init__(self, name: str, date: int, poster_url: str, backdrop_url: str, overview: str, vote_average: float, genres: list[str]):
        self.name = name
        self.date = date
        self.poster_url = poster_url
        self.backdrop_url = backdrop_url
        self.overview = overview
        self.vote_average = vote_average
        self.genres = genres

    def __str__(self):
        return (
            f"Movie: {self.name}\n"
            f"Release Date: {self.date}\n"
            f"Poster URL: {self.poster_url}\n"
            f"Backdrop URL: {self.backdrop_url}"
            f"Overview: {self.overview}"
            f"Vote Average: {self.vote_average}"
            f"Genres: {self.genres}"
        )


class MovieDatabaseClient:
    def __init__(self):
        self.api_key = os.getenv("TMDB_API_KEY")
        self.image_url_base = "https://image.tmdb.org/t/p/original"

        if not self.api_key:
            raise ValueError("TMDB API key not found in environment variables")

        self.top_movies_cache = []
        self.popular_movies_cache = []
        self.genres_cache = {}

    def fetch_top_movies(self, pages=10):
        """Fetch top movies from TMDB and cache them"""

        self.top_movies_cache = []
        api_url = "https://api.themoviedb.org/3/movie/top_rated?language=en-US"

        for page_nr in range(1, pages + 1):
            response = requests.get(
                f"{api_url}&page={page_nr}",
                headers={
                    "accept": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                },
            )
            if response.ok:
                movies_dict = json.loads(response.content.decode("utf-8"))
                self.top_movies_cache.extend(movies_dict["results"])
            else:
                logging.error("Unable to fetch list of movies")

    def fetch_popular_movies(self, pages=5):
        """Fetch popular movies from TMDB and cache them"""

        self.popular_movies_cache = []
        api_url = "https://api.themoviedb.org/3/movie/popular?language=en-US"

        for page_nr in range(1, pages + 1):
            response = requests.get(
                f"{api_url}&page={page_nr}",
                headers={
                    "accept": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                },
            )
            if response.ok:
                movies_dict = json.loads(response.content.decode("utf-8"))
                self.popular_movies_cache.extend(movies_dict["results"])
            else:
                logging.error("Unable to fetch list of popular movies")

    def fetch_genres(self):
        """Fetch movie genres from TMDB and cache them"""

        self.genres_cache = {}
        api_url = "https://api.themoviedb.org/3/genre/movie/list?language=en"

        response = requests.get(api_url, headers={
            "accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        })

        if response.ok:
            genre_data = response.json()
            self.genres_cache = {genre['id']: genre['name'] for genre in genre_data['genres']}
        else:
            logging.error("Unable to fetch list of genres")

    def get_random_movie(self) -> Movie:
        """Get a random movie from the cached top movies"""
        if not self.top_movies_cache:
            self.fetch_top_movies()

        if not self.popular_movies_cache:
            self.popular_movies_cache = []
            # issue with popular movies, temporarily disabled
            # self.fetch_popular_movies()

        if self.genres_cache == None:
            self.genres_cache = self.fetch_genres()

        combined_movies = self.top_movies_cache + self.popular_movies_cache
        movie_dict = random.choice(combined_movies)

        genre_names = [self.genres_cache.get(id, "Unknown Genre") for id in movie_dict["genre_ids"]]

        return Movie(
            name=movie_dict["title"],
            date=movie_dict["release_date"],
            poster_url=self.image_url_base + movie_dict["poster_path"],
            backdrop_url=self.image_url_base + movie_dict["backdrop_path"],
            overview=movie_dict["overview"],
            vote_average=movie_dict["vote_average"],
            genres=genre_names,
        )

    def get_hint(self, movie: Movie) -> str:
        snarky_hints = [
            "Oh, need a hint, do we? Let's see if this makes it too easy:",
            "I suppose everyone needs a little help sometimes. Here's your 'little help':",
            "Alright, since you asked so nicely... Oh, wait, you didn't.",
            "I'm not saying you're struggling, but here's a hint anyway:",
            "Because everyone deserves a second chance... or a third... or a fourth.",
            "Sure, let me just pull out my crystal ball for this one.",
            "Hints, hints, always with the hints. Fine, here you go:",
            "I was hoping you'd figure it out on your own, but alright...",
            "Digging for clues? Let me throw you a bone.",
            "Wouldn't want you to break a sweat. Here's a little nudge:",
            "In the spirit of generosity, I bestow upon you this clue:",
            "Don't tell anyone I'm making it this easy for you.",
            "If I had a dime for every hint I gave... Well, here's another:",
            "Keep this under your hat, but here's a sneaky clue for you:",
            "Because who doesn't love a bit of insider information?"
        ]

        date_hint = f"Release Year: {str(movie.date)[:4]}"  # Assuming date is in 'YYYY-MM-DD' format
        vote_average_hint = f"Rating: {movie.vote_average}/10"
        genres_hint = f"Genres: {', '.join(movie.genres)}"  # Assuming genres is a list of genre names
        overview_hint = f"Overview: {' '.join(movie.overview.split()[:20])}..."  # First 20 words of the overview

        # Choosing a random hint from the prepared options
        hint = random.choice([date_hint, vote_average_hint, genres_hint, overview_hint])
        return f"{random.choice(snarky_hints)}\n{hint}"

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
