import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timezone, timedelta
import dc_token

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="*",intents=intents)
tree = bot.tree

class shiftView(discord.ui.View):
    def __init__(self, shift_embed):
        super().__init__(timeout=None)
        self.declined = set()
        self.attendee = set()
        self.tentative = set()
        self.shift_embed = shift_embed
        
    def build_embed(self):
        embed = discord.Embed(title=self.shift_embed.title, description=self.shift_embed.description, color=65345)
        attend_text = "\n".join(self.attendee) if self.attendee else "-"
        tentative_text = "\n".join(self.tentative) if self.tentative else "-"
        declined_text = "\n".join(self.declined) if self.declined else "-"
        
        embed.add_field(name="✅ Attending", value=f'{attend_text}', inline=True)
        embed.add_field(name='🟦 Tentative', value=f'{tentative_text}', inline=True)
        embed.add_field(name='❌ Declined', value=f'{declined_text}', inline=True)
        return embed
        
    @discord.ui.button(label=" ", style=discord.ButtonStyle.gray, emoji='✅')
    async def attend(self, interaction: discord.Interaction, button: discord.ui.Button):
        names = interaction.user.display_name
        # attendee list check
        if names in self.attendee:
            self.attendee.remove(names)
        elif names in self.tentative:
            self.tentative.remove(names)
            self.attendee.add(names)
        elif names in self.declined:
            self.declined.remove(names)
            self.attendee.add(names)
        else:
            self.attendee.add(names)
            
        await interaction.response.edit_message(embed=self.build_embed())
    
    @discord.ui.button(label=" ", style=discord.ButtonStyle.gray, emoji='🟦')
    async def tentative(self, interaction: discord.Interaction, button: discord.ui.Button):
        names = interaction.user.display_name
        # tentative lists check
        if names in self.tentative:
            self.tentative.remove(names)
        elif names in self.attendee:
            self.attendee.remove(names)
            self.tentative.add(names)
        elif names in self.declined:
            self.declined.remove(names)
            self.tentative.add(names)
        else:
            self.tentative.add(names)
            
        await interaction.response.edit_message(embed=self.build_embed())

    @discord.ui.button(label=" ", style=discord.ButtonStyle.gray, emoji='❌')
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        names = interaction.user.display_name
        if names in self.declined:
            self.declined.remove(names)
        elif names in self.attendee:
            self.attendee.remove(names)
            self.declined.add(names)
        elif names in self.tentative:
            self.tentative.remove(names)
            self.declined.add(names)
        else:
            self.declined.add(names)
            
        await interaction.response.edit_message(embed=self.build_embed())
    
@bot.command()
async def shift_create(ctx:commands.Context, title, desc, *,co_host):
    await ctx.message.delete()
    host = ctx.author.mention
    
    shift_embed = discord.Embed(title=title, description=f"{desc}\n\n Host: {host} \nCo-Host: {co_host}\n", color=65345)
    shift_embed.add_field(name='✅ Attendees', value='-')
    shift_embed.add_field(name='🟦 Tentative', value='-')
    shift_embed.add_field(name='❌ Declined', value='-')
    message = await ctx.send(embed=shift_embed, view=shiftView(shift_embed))
    
@bot.tree.command()
@app_commands.describe(type='type of event (@ the ping)', title='title of the event', desc='description for the event', co_host='co-host if exists', days='days until the event (null=0)', hours='hours until the event (null=0)', minute='minutes until the event (null=0)')
async def shift(interaction:discord.Interaction, type:str, title:str, desc:str, co_host:str, days:int, hours:int, minute:int) -> None:
    host = interaction.user.mention
    event_time = datetime.now(timezone.utc) + timedelta(hours=hours, days=days, minutes=minute)
    short_date = discord.utils.format_dt(event_time, style="s")
    relative_time = discord.utils.format_dt(event_time, style="R")
    short_time = discord.utils.format_dt(event_time, style="t")
    
    if days==0:
        shift_embed = discord.Embed(title=title, description=f"**{desc}**\n\n Host: {host} \nCo-Host: {co_host}\n\nEvent in: {short_time} {relative_time}", color=65345)
        shift_embed.add_field(name='✅ Attendees', value='-')
        shift_embed.add_field(name='🟦 Tentative', value='-')
        shift_embed.add_field(name='❌ Declined', value='-')
        message = await interaction.response.send_message(content=type, embed=shift_embed, view=shiftView(shift_embed))
    else:
        shift_embed = discord.Embed(title=title, description=f"**{desc}**\n\n Host: {host} \nCo-Host: {co_host}\n\nEvent in: {short_date} {relative_time}", color=65345)
        shift_embed.add_field(name='✅ Attendees', value='-')
        shift_embed.add_field(name='🟦 Tentative', value='-')
        shift_embed.add_field(name='❌ Declined', value='-')
        message = await interaction.response.send_message(content=type, embed=shift_embed, view=shiftView(shift_embed))

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Bot is ONLINE.")
    
token = dc_token.token
bot.run(token)