from random import randint

# colors
orcolor = '#00ff51'
vicolor = '#bf00ff'
rubcolor = '#e0115f'
darkcolor = '#000'
redcolor = '#ff0000'
brcolor = '#ffffff'
def theme():
    color = [orcolor, vicolor, rubcolor, redcolor, brcolor]
    backcolor = color[randint(0, 4)]
    return backcolor



