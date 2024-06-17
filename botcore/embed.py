import discord

def instructions() -> discord.Embed:
    """
    Construct an ```Embed``` object that lists and explains the commands for a Sudoku game bot.
    """
    title = "Commands Instructions"
    description = "Here are all the commands and the functions of them."
    value_start_sudoku = "Continue the game you have started.  It won\'t create a new game if the user has not started a game."
    value_new_sudoku = "Create a new game.  The user must set difficulty level, which have 4 options:  Easy (0), Medium (1), Hard (2), and Expert (3).  It will delete existing game data after warning the user."
    value_cheat = "Show the answer of teh game.  The user must create a new game before using this function.  A new game will not be created if the user has not already started one.  This function will over write existing game data."
    
    embed=discord.Embed(title=title, description=description, color=0x75b8ff)
    embed.set_author(name="すど君")
    embed.add_field(name="/start_sudoku", value=value_start_sudoku, inline=False)
    embed.add_field(name="/new_sudoku", value=value_new_sudoku, inline=False)
    embed.add_field(name="/cheat", value=value_cheat, inline=False)
    
    return embed
