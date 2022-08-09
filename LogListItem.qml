import QtQuick 2.0
import QtQuick.Controls 2.15

Rectangle{
    width: parent.width
    height: 16
    color: "transparent"

    TextInput{
        anchors.fill: parent
        width: parent.width
        height: parent.height
        text: model.display
        font.bold: model.display[9] === ">" ? true : false
        readOnly: true
        selectByMouse: true
        wrapMode: Text.WordWrap
        selectionColor:  "#94DCFA"
    }
}
