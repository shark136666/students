import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Layouts 1.3
import QtQuick.Controls 2.15



Row{
    id: connectForm
    Rectangle{
        id: ipForm
        width: 200
        height: parent.height
        color: "lightgrey"
        Text{
            id: ipFormLabel
            anchors.left: parent.left
            text: qsTr("IP Address")
            font.pixelSize: 16

        }

        TextField {
            id: addressTF
            anchors.right: parent.right
            width: 120
            height: parent.height
            font.pixelSize: 16
            selectByMouse: true
            text: client.address
            onEditingFinished: {
                client.address = addressTF.displayText
            }
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
            id: portTF
            anchors.right: parent.right
            width: 60
            height: parent.height
            font.pixelSize: 16
            selectByMouse: true
            text: client.port
            onEditingFinished: {
                client.port = portTF.displayText
            }
        }
    }
    Button{
        id: connectBtn
        text: "connect"
        height: parent.height
        onClicked: {
            if(client.address && client.port)
                client.connect("connect ADDRESS: " + client.address +
                               " PORT: " + client.port)
        }
    }
    Button{
        text: "*QBN?"
        height: parent.height
        onClicked: {
            client.sendCommand("*QBN?")
        }
    }
    Button{
        text: "Check errors"
        height: parent.height
        onClicked: {
            client.sendCommand("check errors")
        }
    }
}
