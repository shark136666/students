import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Layouts 1.3
import QtQuick.Controls 2.15

Row{
    id: connectForm
    Rectangle{
        id: ipForm
        width: 180
        height: parent.height
        color: "lightgrey"
        Text{
            id: ipFormLabel
            anchors.left: parent.left
            text: qsTr("IP Address")
            font.pixelSize: 16

        }
        TextField {
            anchors.right: parent.right
            width: 100
            height: parent.height
            font.pixelSize: 16
            selectByMouse: true
        }
    }
    Rectangle{
        id: portForm
        width: 100
        height: parent.height
        color: "lightgrey"
        Text{
            id: portFormLabel
            anchors.left: parent.left
            text: qsTr("PORT")
            font.pixelSize: 16

        }
        TextField {
            anchors.right: parent.right
            width: 60
            height: parent.height
            font.pixelSize: 16
            selectByMouse: true
        }
    }
    Button{
        id: connectBtn
        text: "connect"
        height: parent.height
        onClicked: {
            win.color = Qt.rgba(Math.random(), Math.random(), Math.random())
        }
    }
    Button{
        text: "*QBN?"
        height: parent.height
        onClicked: {
            win.color = "white"
        }
    }
    Button{
        text: "Check errors"
        height: parent.height
        onClicked: {
            win.color = "#FF9999"
        }
    }
}
