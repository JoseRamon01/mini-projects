import discord
from discord.ext import commands
import youtube_dl
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from youtube_search import YoutubeSearch
import requests
import secrets_1
import clienteID
import clienteS



intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents)

SPOTIFY_CLIENT_ID = clienteID.TOKEN_ID
SPOTIFY_CLIENT_SECRET = clienteS.TOKEN_SECRET

spotify = spotipy.Spotify(auth_manager = SpotifyClientCredentials (
    client_id = SPOTIFY_CLIENT_ID, 
    client_secret = SPOTIFY_CLIENT_SECRET
    )
)

# Configuración de Youtube_dl

youtube_dl.utils.bug_reports_message = lambda: ""

ytdl_format_options = {
    'format' : 'bestaudio/best',
    'postprocessors' : [{
        'key' : 'FFmpegExtractAudio',
        'preferredcodec' : 'mp3',
        'preferredquality' : '192',
        }],
    'noplaylist' : True,
}

ffmpeg_options = {
    'options' : '-vn'
    
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

#Comando para unirse al canal de voz
@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send('Me he unico al canal de voz')
    else:
        await ctx.send('Debes estar conectado a un canal de voz, por favor.')

@bot.command()
async def playlist(ctx, url):
    try:
        results = spotify.playlist_tracks(url)
        tracks = [
            f"{track['track']['name']} {track['track']['artists'][0]['name']}"
            for track in results['items']
        ]
        vc = ctx.voice_client
        if not vc:
            await ctx.send('Primero necesito unirme a un canal de voz')
            return
        
        for track in tracks:
            yt_results = YoutubeSearch(track, max_result=1).to_dict()
            if yt_results:
                yt_url = f'https://www.youtube.com{yt_results[0]['url_suffix']}'
                info = ytdl.extract_info(yt_url, download=False)
                vc.play(discord.FFmpegPCMAudio(info['url'], **ffmpeg_options))
                await ctx.send(f'Reproduciendo:   {track}')
                while vc.is_playing():
                    await discord.utils.sleep_until(vc.source)
            else:
                await ctx.send('No se pudo encontrar la canción')
    except Exception as e:
        print(e)
        await ctx.send('Hubo un problema al encontrar la lista')
        
#Comando para salir del canal de voz

@bot.command()
async def leave (ctx):
    vc = ctx.voice_client
    if vc:
        await vc.disconnect()
        await ctx.send('Me he salido del canal de voz')
    else:
        await ctx.send('No estoy en un canal de voz')


# Mensajes de inicio
@bot.event
async def on_message(msg):
    if msg.author == bot.user:
        return
    if msg.content.lower().startswith("hola"):
        await msg.reply("Hola a ti también")


#Comando para buscar un pokemon
@bot.command()
async def poke(ctx, *args):
    try: 
        pokemon = args[0].lower()
        is_shiny = len(args) > 1 and args[1].lower() == "shiny"
        result = requests.get("https://pokeapi.co/api/v2/pokemon/"+ pokemon)
        if result.text == "Not Found":
            await ctx.send("Pokemon no encontrado")
        else:
            data = result.json()
            imagen_url = data['sprites']['front_default'] 
            if is_shiny == True:
                imagen_shiny_url = data['sprites']['front_shiny']
                print(imagen_shiny_url)
                await ctx.send(imagen_shiny_url)
            else:
                print(imagen_url)
                await ctx.send(imagen_url)
                     
    except Exception as e:
        print("Error: ", e)

@poke.error 
async def error_type(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send("Tienes que pasarme un pokemon")
    
@bot.event
async def on_ready():
    print(f'Estamos dentro! {bot.user}')
    
bot.run(secrets_1.TOKEN)