from nextcord import Interaction, Embed, ui, ButtonStyle, SlashOption, Message, InteractionType
from nextcord.ext import commands
import datetime
import os
from typing import Optional
import re

DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")

bot = commands.Bot()

SERVER_ID = int(os.environ.get("SERVER_ID"))
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))

class party_view(ui.View):
    def __init__(self, info: dict):
        super().__init__()
        self.embeds = []
        self.embeds.append(Embed(title="파티찾기",
                                 description=f"<@{info['user_id']}>님이 파티를 찾고있어요!", color=0x00ff00))
        self.embeds[0].add_field(name="카테고리", value=f"<#{info['category_id']}>", inline=False)
        self.embeds[0].add_field(name="채널명", value=f"<#{info['channel_id']}>", inline=True)
        self.embeds[0].add_field(name="", value="", inline=True)
        self.embeds[0].add_field(name="멤버", value=info['channel_user_status'], inline=True)
        self.embeds[0].add_field(name="설명", value=info['message'], inline=False)
        self.embeds[0].set_footer(text="채널명을 클릭시 바로 입장됩니다.")
        self.embeds[0].timestamp = datetime.datetime.now()
        self.add_item(ui.Button(label="둘러보기", style=ButtonStyle.url, url=info['channel_url']))
        self.add_item(ui.Button(label="모집중", style=ButtonStyle.green, custom_id="close"))

class party_end_view(ui.View):
    def __init__(self, user_id):
        super().__init__()
        self.embeds = []
        self.embeds.append(Embed(title="파티찾기",
                                 description=f"<@{user_id}>님이 파티를 찾았어요!"))
        self.embeds[0].set_footer(text="모집 완료 된 파티입니다.")
        self.embeds[0].timestamp = datetime.datetime.now()
        self.add_item(ui.Button(label="모집완료", style=ButtonStyle.gray, custom_id="close", disabled=True))


@bot.event
async def on_ready():
    print("Bot is ready.")

@bot.slash_command(name="파티", description="파티를 구해요", guild_ids=[SERVER_ID])
async def 파티(interaction: Interaction, 메시지: Optional[str] = SlashOption(description='파티 모집과 함께 전송되는 메세지 입니다.', required=False, default='없음')):
    if interaction.channel_id == CHANNEL_ID:
        user = interaction.user
        voice_state = user.voice

        if voice_state is None or voice_state.channel is None:
            await interaction.response.send_message("음성 채널에 입장해주세요.", ephemeral=True)
            return

        channel = voice_state.channel

        info = {
            "category_id" : channel.category_id,
            "channel_id" : channel.id,
            "channel_user_status" : str(len(bot.get_channel(channel.id).members)) + "/" + str(channel.user_limit if channel.user_limit != 0 else "∞"),
            "user_id" : user.id,
            "message" : 메시지,
            "channel_url" : channel.jump_url
        }

        view = party_view(info)
        await interaction.response.send_message(embeds=view.embeds, view=view)
        await interaction.send("파티 모집을 종료하려면, " + view.children[1].label + " 버튼을 눌러주세요.", ephemeral=True)
    else:
        await interaction.response.send_message("이 채널에서는 사용할 수 없습니다.", ephemeral=True)

@bot.listen()
async def on_interaction(interaction: Interaction):
    if interaction.type == InteractionType.component:
        if interaction.data["custom_id"] == "close":
            message_user_id = int(re.search('<@(.+?)>', interaction.message.embeds[0].description).group(1))
            if interaction.user.id == message_user_id:
                view = party_end_view(message_user_id)
                await interaction.message.edit(embeds=view.embeds, view=view)
            else:
                await interaction.send_message("파티를 모집한 사람이 아니에요.", ephemeral=True)


bot.run(DISCORD_BOT_TOKEN)