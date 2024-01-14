import random
import asyncio
import discord
from discord.ext import commands
from enum import Enum
from typing import List

from helper import get_embed
from schemas.player import Player


class DuelState(Enum):
    PENDING = 1
    ACCEPTED = 2
    COMPLETED = 3


class MoveType(Enum):
    ATTACK = "attack"
    DEFEND = "defend"
    HEAL = "heal"


class Duelist:
    max_health = 100

    def __init__(self, name: str, player_id: int, avatar: str = None):
        self.name = name
        self.id = player_id
        self.health = self.max_health
        self.avatar = avatar or "\U0001F476"
        self.is_shielded = False

    def take_damage(self, amount: int):
        if self.is_shielded:
            self.is_shielded = False
            return

        self.health -= amount
        if self.health < 0:
            self.health = 0

    def heal(self, amount: int):
        self.health = min(self.max_health, self.health + amount)

    def shield(self):
        self.is_shielded = True

    def is_defeated(self):
        return self.health <= 0


class DuelMove:
    def __init__(self, name: str, symbol: str, move_type: str, value: int, weight: int):
        self.name = name
        self.symbol = symbol
        self.move_type = move_type
        self.value = value
        self.weight = weight


class Duel:
    moves = [
        DuelMove("Sword", "⚔️", MoveType.ATTACK, 15, 10),
        DuelMove("Magic", "🔮", MoveType.ATTACK, 20, 8),
        DuelMove("Arrow", "🏹", MoveType.ATTACK, 12, 9),
        DuelMove("Fire", "🔥", MoveType.ATTACK, 25, 7),
        DuelMove("Ice", "❄️", MoveType.ATTACK, 18, 7),
        DuelMove("Poison", "☠️", MoveType.ATTACK, 22, 6),
        DuelMove("Lightning", "⚡", MoveType.ATTACK, 20, 8),
        DuelMove("Explosive", "💣", MoveType.ATTACK, 30, 5),
        DuelMove("Punch", "🥊", MoveType.ATTACK, 10, 12),
        DuelMove("Shield", "🛡️", MoveType.DEFEND, 0, 15),
        DuelMove("Psychic", "🌀", MoveType.ATTACK, 17, 9),
        DuelMove("Nature", "🌿", MoveType.ATTACK, 15, 10),
        DuelMove("Wind", "💨", MoveType.ATTACK, 13, 11),
        DuelMove("Water", "🌊", MoveType.ATTACK, 19, 8),
        DuelMove("Stealth", "🥷", MoveType.ATTACK, 25, 6),
        DuelMove("Robot", "🤖", MoveType.ATTACK, 20, 7),
        DuelMove("Heal", "💖", MoveType.HEAL, 20, 7),
    ]

    def __init__(self, challenger: Duelist, challengee: Duelist, wager: int):
        self.challenger = challenger
        self.challengee = challengee
        self.wager = wager
        self.state = DuelState.PENDING

    def accept(self):
        if self.state == DuelState.PENDING:
            self.state = DuelState.ACCEPTED

    def simulate(self):
        if self.state != DuelState.ACCEPTED:
            return ValueError("Duel has not been accepted")

        while not self.is_complete():
            yield self.do_round()

        self.state = DuelState.COMPLETED

    def do_round(self) -> str:
        attacker = random.choice([self.challenger, self.challengee])
        defender = self.challengee if attacker == self.challenger else self.challenger

        move = self.get_random_move(self.moves)
        shielded = defender.is_shielded

        if move.move_type == MoveType.ATTACK:
            defender.take_damage(move.value)
        elif move.move_type == MoveType.DEFEND:
            defender.shield()
        elif move.move_type == MoveType.HEAL:
            defender.heal(move.value)

        return self.generate_attack_message(attacker, defender, move, shielded)

    def generate_attack_message(
        self, attacker: Duelist, defender: Duelist, move: DuelMove, shielded: bool
    ) -> str:
        if move.move_type == MoveType.ATTACK:
            if shielded:
                move_details = f"{attacker.name} used {move.name} {move.symbol} for no damage because the attack was shielded!"
            else:
                move_details = f"{attacker.name} used {move.name} {move.symbol} for {move.value} damage!"
        elif move.move_type == MoveType.DEFEND:
            move_details = (
                f"{attacker.name} used {move.name} {move.symbol} to protect themselves!"
            )
        elif move.move_type == MoveType.HEAL:
            move_details = f"{attacker.name} used {move.name} {move.symbol} to heal for {move.value}!"

        arena = (
            f"{self.challenger.health}/{self.challenger.max_health} "
            f"{self.challenger.avatar}{'🛡️' if self.challenger.is_shielded else ''}"
            f"{'-' * 5} {move.symbol} {'-' * 5}"
            f" {'🛡️' if self.challengee.is_shielded else ''}{self.challengee.avatar} "
            f"{self.challengee.health}/{self.challengee.max_health}"
        )

        return "\n\n".join([move_details, arena])

    def generate_initial_message(self) -> str:
        details = (
            f"{self.challenger.health}/{self.challenger.max_health} {self.challenger.avatar}"
            f"{'-' * 11}"
            f"{self.challengee.avatar} {self.challengee.health}/{self.challengee.max_health}"
        )

        return details

    def is_complete(self) -> bool:
        return self.challenger.is_defeated() or self.challengee.is_defeated()

    def has_player(self, player_id: int) -> bool:
        return self.challenger.id == player_id or self.challengee.id == player_id

    def get_winner(self) -> Duelist:
        if self.challenger.is_defeated():
            return self.challenger
        elif self.challengee.is_defeated():
            return self.challengee
        else:
            return None

    def get_random_move(self, moves: List[DuelMove]):
        weights = [move.weight for move in moves]
        selected_move = random.choices(moves, weights, k=1)[0]
        return selected_move


class DuelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.duels = []

    @commands.hybrid_group(name="duel", description="Group of duel commands")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def duel(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            raise commands.CommandError("No subcommand invoked")

    @duel.error
    async def duel_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(f"`duel` error: {error}")

    @duel.command(name="start")
    async def duel_start(self, ctx: commands.Context, user: discord.User, amount: int):
        #if ctx.author.id == user.id:
        #    raise commands.CommandError("Can't challenge yourself")

        if amount < 1:
            raise commands.CommandError("Must wager at least 1 coin")

        for duel in self.duels:
            if duel.has_player(user.id) and duel.state != DuelState.COMPLETED:
                raise commands.CommandError(
                    "You have an active challenge with this user"
                )

        p1 = self.bot.player_service.get_player(ctx.author.id)
        p2 = self.bot.player_service.get_player(user.id)

        if p2.coins < amount:
            raise commands.CommandError(f"{user.name} doesn't have enough coins")

        self.bot.player_service.remove_coins(p1, amount)

        challenger = Duelist(ctx.author.name, ctx.author.id, p1.active_avatar)
        challengee = Duelist(user.name, user.id, p2.active_avatar)
        duel = Duel(challenger, challengee, amount)
        self.duels.append(duel)

        embed = get_embed(
            "\U0001F4A5 Duel Request \U0001F4A5",
            f"{ctx.author.name} challenged {user.name} to a duel for {amount} coins!",
            discord.Color.red(),
        )
        embed.add_field(name="Information", value="Ending in 1 minute", inline=False)
        await ctx.send(embed=embed)

        await asyncio.sleep(60)

        # Duel never got accepted
        if duel.state == DuelState.PENDING:
            p1 = self.bot.player_service.get_player(
                ctx.author.id
            )  # Prevent race condition
            self.bot.player_service.add_coins(p1, amount)
            self.duels.remove(duel)
            await ctx.send(content="Duel request expired, refunded coins")

    @duel_start.error
    async def duel_start_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(f"`duel start` error: {error}")

    @duel.command(name="accept")
    async def duel_accept(self, ctx: commands.Context, user: discord.User = None):
        if user and ctx.author.id == user.id:
            raise commands.CommandError("Can't accept a duel from yourself")

        player = self.bot.player_service.get_player(ctx.author.id)

        pending_duels = []

        for duel in self.duels:
            if duel.has_player(ctx.author.id) and duel.state == DuelState.PENDING:
                pending_duels.append(duel)

        if not pending_duels:
            raise commands.CommandError("No pending duels")

        if user:
            for duel in pending_duels:
                if duel.has_player(user.id):
                    await self.handle_accept_duel(player, ctx, duel)
        else:
            if len(pending_duels) > 1:
                raise commands.CommandError("You have more than one pending duel")

            duel = pending_duels.pop()
            await self.handle_accept_duel(player, ctx, duel)

    @duel_accept.error
    async def duel_accept_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(f"`duel accept` error: {error}")

    async def handle_accept_duel(
        self, player: Player, ctx: commands.Context, duel: Duel
    ):
        self.bot.player_service.remove_coins(player, duel.wager)
        duel.accept()
        await self.simulate_duel(ctx, duel)

    async def simulate_duel(self, ctx: commands.Command, duel: Duel):
        embed = get_embed(
            f"Duel: {duel.challenger.name} vs. {duel.challengee.name}",
            f"```{duel.generate_initial_message()}```",
            discord.Color.red(),
        )
        message = await ctx.send(embed=embed)

        await asyncio.sleep(3)

        for duel_string in duel.simulate():
            embed.description = f"```{duel_string}```"
            await message.edit(embed=embed)
            await asyncio.sleep(3)

        winner = duel.get_winner()

        player = self.bot.player_service.get_player(winner.id)
        self.bot.player_service.add_coins(player, duel.wager * 2)

        embed.description = f"{winner.name} won {duel.wager} coin(s)!"
        await ctx.send(embed=embed)
