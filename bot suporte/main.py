import discord
from discord import app_commands
from discord.ext import commands

id_do_servidor = 771116948544946216 #Coloque aqui o ID do seu servidor
id_cargo_atendente = 1140669169457704980 #Coloque aqui o ID do cargo de atendente
token_bot = '' #Coloque aqui seu Token do BOT | OBS: Não compartilhe em hipótese alguma o Token

class Dropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(value="dúvida",label="Tirar Dúvida", emoji="👷🏻"),
            discord.SelectOption(value="denúncia",label="Fazer Denúncia", emoji="🚨"),
            discord.SelectOption(value="punição",label="Apelar Punição", emoji="👨🏻‍⚖️"),
            discord.SelectOption(value="bug",label="Reportar Bug", emoji="🔨"),
        ]
        super().__init__(
            placeholder="Selecione uma opção...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="persistent_view:dropdown_help"
        )
    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "dúvida":
            await interaction.response.send_message("Para tirar dúvidas gerais sobre Discord ou Bots use os canais de suporte como <#1013946442429255680> <#857303047775846440> ",ephemeral=True)
        elif self.values[0] == "denúncia":
            await interaction.response.send_message("Se quiser prosseguir com sua denúncia, crie um atendimento abaixo.",ephemeral=True,view=CreateTicket())
        elif self.values[0] == "punição":
            await interaction.response.send_message("Deseja revogar sua punição, crie um atendimento abaixo. ",ephemeral=True,view=CreateTicket())
        elif self.values[0] == "bug":
            await interaction.response.send_message("Ajude a melhorar o servidor, reporte o bug criando um atendimento abaixo. ",ephemeral=True,view=CreateTicket())

class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(Dropdown())

class CreateTicket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.value=None

    @discord.ui.button(label="Abrir Ticket",style=discord.ButtonStyle.blurple,emoji="➕")
    async def confirm(self,interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        self.stop()

        ticket = None
        for thread in interaction.channel.threads:
            if f"{interaction.user.id}" in thread.name:
                if thread.archived:
                    ticket = thread
                else:
                    await interaction.response.send_message(ephemeral=True,content=f"Você já tem um atendimento em andamento!")
                    return

        async for thread in interaction.channel.archived_threads(private=True):
            if f"{interaction.user.id}" in thread.name:
                if thread.archived:
                    ticket = thread
                else:
                    await interaction.edit_original_response(content=f"Você já tem um atendimento em andamento!",view=None)
                    return
        
        if ticket != None:
            await ticket.edit(archived=False,locked=False)
            await ticket.edit(name=f"{interaction.user.name} ({interaction.user.id})",auto_archive_duration=10080,invitable=False)
        else:
            ticket = await interaction.channel.create_thread(name=f"{interaction.user.name} ({interaction.user.id})",auto_archive_duration=10080,type=discord.ChannelType.private_thread) #,type=discord.ChannelType.public_thread)
            await ticket.edit(invitable=False)

        await interaction.response.send_message(ephemeral=True,content=f"Criei um ticket para você! {ticket.mention}")
        await ticket.send(f"📩  **|** {interaction.user.mention} ticket criado! Envie todas as informações possíveis sobre seu caso e aguarde até que um atendente responda.\n\nApós a sua questão ser sanada, você pode usar `/fecharticket` para encerrar o atendimento!\n\n<@&1013153362805526568><@&857369630083383336>")



class client(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.synced = False #Nós usamos isso para o bot não sincronizar os comandos mais de uma vez

    async def setup_hook(self) -> None:
        self.add_view(DropdownView())

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced: #Checar se os comandos slash foram sincronizados 
            await tree.sync(guild = discord.Object(id=id_do_servidor)) # Você também pode deixar o id do servidor em branco para aplicar em todos servidores, mas isso fará com que demore de 1~24 horas para funcionar.
            self.synced = True
        print(f"Entramos como {self.user}.") 

aclient = client()

tree = app_commands.CommandTree(aclient)

@tree.command(guild = discord.Object(id=id_do_servidor), name = 'setup', description='Setup')
@commands.has_permissions(manage_guild=True)
async def setup(interaction: discord.Interaction):
    await interaction.response.send_message("Painel Criado",ephemeral=True) 

    embed = discord.Embed(
        colour=discord.Color.blurple(),
        title="**Central de ajuda do Servidor**",
        description="Nessa seção, você pode entrar em contato com a nossa equipe do servidor"
    )  
    embed.set_image(url="https://i.imgur.com/quBpIIg.png")

    await interaction.channel.send(embed=embed,view=DropdownView())

@tree.command(guild = discord.Object(id=id_do_servidor), name="fecharticket",description='Feche um atendimento atual.')
async def _fecharticket(interaction: discord.Interaction):
    mod = interaction.guild.get_role(771326683214381107)
    if str(interaction.user.id) in interaction.channel.name or mod in interaction.author.roles:
        await interaction.response.send_message(f"O ticket foi arquivado por {interaction.user.mention}, obrigado por entrar em contato!")
        await interaction.channel.edit(archived=True,locked=True)
    else:
        await interaction.response.send_message("Isso não pode ser feito aqui...")

aclient.run(token_bot)