import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Layouts 1.3
import QtQuick.Controls 2.15

Row{
    id: commandForm
    TextField {
        width: 540
        height: parent.height
        font.pixelSize: 16
        selectByMouse: true
    }

    Button{
        id: addBtn
        height: parent.height
        text: "add command"
        onClicked: {
            console.log("add command")
        }
    }

}
