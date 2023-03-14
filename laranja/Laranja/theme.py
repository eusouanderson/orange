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

def font(model=0, value=0):

    font = dict()
    font['Model'] = ['Calibri'], ['Arial'], ['Courier New'], ['Times New Roman']
    font['Size'] = [10], [18], [15], [25]
    for f in font:
        fmodel = (font['Model'][model])
        fsize = (font['Size'][value])

    return fmodel, fsize


