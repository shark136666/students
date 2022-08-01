import QtQuick 2.0
import QtQuick.Controls 2.15

Rectangle{
    height: 16
    color: "transparent"

    Text{
        width: parent.width
        height: parent.height
        text: model.display
        font.bold: model.display[0] === ">" ? true : false
    }
}
