# PySide6 StyleSheet Guide

This document lists the common `StyleSheet` properties you can use to customize ``` widgets in PySide6 (Qt).

## 1. Background Color (`background-color`)
Define the background color of a ``` widget. ```

``` widget. ```setStyleSheet("background-color: #2E2E2E;")
2. Text Color (color)
Set the color of the text inside the ``` widget. ```



``` widget. ```setStyleSheet("color: white;")
3. Font (font)
Modify the font of the text.


``` widget. ```setStyleSheet("font: 16px Arial;")
4. Border (border)
Set the border of a ``` widget. ```


``` widget. ```setStyleSheet("border: 2px solid black;")
5. Border Radius (border-radius)
Round the corners of the ``` widget. ```


``` widget. ```setStyleSheet("border-radius: 10px;")
6. Box Shadow (box-shadow)
Apply a shadow around the ``` widget. ```


``` widget. ```setStyleSheet("box-shadow: 4px 4px 8px rgba(0, 0, 0, 0.5);")
7. Focus (:focus)
Style the ``` widget when it is focused (e.g., when a text field is selected).


``` widget. ```setStyleSheet("QLineEdit:focus { border: 2px solid blue; }")
8. Hover (:hover)
Style the ``` widget when the mouse hovers over it.


``` widget. ```setStyleSheet("QPushButton:hover { background-color: green; }")
9. Disabled (:disabled)
Style the ``` widget when it is disabled.


``` widget. ```setStyleSheet("QPushButton:disabled { background-color: grey; color: white; }")
10. Padding
Define the internal padding of a ``` widget. ```


``` widget. ```setStyleSheet("padding: 10px;")
11. Margin
Define the margin around the ``` widget. ```


``` widget. ```setStyleSheet("margin: 20px;")
12. Width and Height (width, height)
Set the width and height of the ``` widget. ```


12. Width and Height (width, height)
Set the width and height of the ``` widget. ```


``` widget. ```setStyleSheet("width: 200px; height: 100px;")
13. Background Image (background-image)
Set a background image for the ``` widget. ```


``` widget. ```setStyleSheet("background-image: url('path/to/image.png');")
14. Border Style (border-style)
Define the style of the border (solid, dotted, dashed, etc.).


``` widget. ```setStyleSheet("border-style: dotted;")
15. Border Width (border-width)
Define the width of the border.

``` widget. ```setStyleSheet("border-width: 3px;")
16. Border Color (border-color)
Set the color of the ``` widget's border.


``` widget. ```setStyleSheet("border-color: red;")
17. Border Top (border-top)
Set the style for the top border only.
``` widget. ```setStyleSheet("border-top: 2px solid blue;")


18. Button Style (QPushButton)
Customize the style of a button.

``` widget. ```setStyleSheet("""
QPushButton {
    background-color: blue;
    color: white;
    font: bold 14px;
    border-radius: 5px;
}
QPushButton:hover {
    background-color: darkblue;
}
""")

19. Custom ``` widget Style
Apply a custom style to a specific ``` widget type.

``` widget. ```setStyleSheet("""
QLabel {
    color: #FF5733;
    font-size: 20px;
    font-weight: bold;
}
""")

20. Scrollbar Style (QScrollBar)
Modify the appearance of a scrollbar.

``` widget. ```setStyleSheet("""
QScrollBar:vertical {
    border: 2px solid #999;
    background: #F4F4F4;
    width: 12px;
}
QScrollBar::handle:vertical {
    background: #666;
    border-radius: 6px;
}
""")

21. Title Bar Style (QMainWindow)
Style the title bar of the main window.


``` widget. ```setStyleSheet("""
QMainWindow {
    background-color: #2A2A2A;
}
QMainWindow::title {
    color: white;
    font-size: 18px;
}
""")

22. Scroll Area Style (QScrollArea)
Customize the style of a scroll area.

``` widget. ```setStyleSheet("""
QScrollArea {
    background-color: #EFEFEF;
    border: 1px solid #D1D1D1;
}
""")

23. Line Edit Style (QLineEdit)
Change the appearance of a line edit ``` widget (text input field).


``` widget. ```setStyleSheet("""
QLineEdit {
    border: 1px solid #ccc;
    padding: 5px;
}
QLineEdit:focus {
    border: 1px solid blue;
}
""")

24. Combo Box Style (QComboBox)
Customize the appearance of a combo box (dropdown menu).

``` widget. ```setStyleSheet("""
QComboBox {
    border: 1px solid #ccc;
    padding: 5px;
}
QComboBox:focus {
    border: 1px solid blue;
}
""")

25. Table View Style (QTableView)
Style a table view.


``` widget. ```setStyleSheet("""
QTableView {
    border: 1px solid #ccc;
    background-color: #F9F9F9;
}
QTableView::item {
    padding: 5px;
}
""")


