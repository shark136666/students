import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Layouts 1.3
import QtQuick.Controls 2.15
import QtQuick.Dialogs 1.3


Rectangle{
    color: "#ddd"
    radius: 5
    RowLayout{
        anchors.centerIn: parent

        Rectangle{
            id: ipForm
            Layout.preferredWidth: 80
            color: "lightgrey"
            Text{
                id: ipFormLabel
                anchors.centerIn: parent
                text: qsTr("IP Address")
                font.pixelSize: 14
            }
        }
        TextField {
            id: addressTF
            Layout.preferredWidth: 130
            Layout.rightMargin: 20
            font.pixelSize: 14
            selectByMouse: true
            text: client.address
            onEditingFinished: {
                client.address = addressTF.displayText
            }
            background: Rectangle {
                anchors.centerIn: parent
                implicitWidth: 124
                implicitHeight: 30
                border.width: parent.activeFocus ? 1 : 0
                color: addressTF.activeFocus ? "#fff" : "#ededed"
                border.color: parent.activeFocus ? outlineColor : "#777"
                radius: 5
            }
        }

        Rectangle{
            id: portForm
            Layout.preferredWidth: 40
            Text{
                id: portFormLabel
                anchors.centerIn: parent
                text: qsTr("PORT")
                font.pixelSize: 14

            }
        }
        TextField {
            id: portTF
            Layout.preferredWidth: 120
            Layout.rightMargin: 20
            font.pixelSize: 14
            selectByMouse: true
            text: client.port
            onEditingFinished: {
                client.port = portTF.displayText
            }
            background: Rectangle {
                anchors.centerIn: parent
                implicitWidth: 110
                implicitHeight: 30
                border.width: parent.activeFocus ? 1 : 0
                color: portTF.activeFocus ? "#fff" : "#ededed"
                border.color: parent.activeFocus ? outlineColor : "#777"
                radius: 5
            }
        }

        Rectangle{
            Layout.rightMargin: 20
            width: 10;
            height: width;
            radius: width/2;
            color: client.isConnected ? "#34eb49" : "#e32727";
        }
        Button{
            id: connectBtn
            height: parent.height
            onClicked: {
                client.doConnect()
            }
            contentItem: Text {
                    text: client.isConnected ? "Disconnect" : "Connect";
                    font.pixelSize: 16
                    color: parent.down ? btnTextDown : btnText
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    elide: Text.ElideRight
                }
            background: Rectangle {
                        implicitWidth: 100
                        implicitHeight: 30
                        color: parent.down ? outlineColor : btnDisactiveBg
                        border.color: parent.activeFocus? outlineColor : btnDisactiveBorder
                        border.width: parent.activeFocus ? 1 : 0
                    }
        }
        Button{
            height: parent.height
            onClicked: {
                client.sendCommand("*IDN?")
            }
            contentItem: Text {
                text: "*IDN?"
                    font.pixelSize: 16
                    color: parent.down ? btnTextDown : btnText
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    elide: Text.ElideRight
                }
            background: Rectangle {
                        implicitWidth: 100
                        implicitHeight: 30
                        color: parent.down ? outlineColor : btnDisactiveBg
                        border.color: parent.activeFocus? outlineColor : btnDisactiveBorder
                        border.width: parent.activeFocus ? 1 : 0
                    }
        }
        Button{
            height: parent.height
            onClicked: {
                client.sendCommand("SYST:ERR?")
            }
            contentItem: Text {
                text: "SYST:ERR?"
                    font.pixelSize: 16
                    color: parent.down ? btnTextDown : btnText
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    elide: Text.ElideRight
                }
            background: Rectangle {
                        implicitWidth: 100
                        implicitHeight: 30
                        color: parent.down ? outlineColor : btnDisactiveBg
                        border.color: parent.activeFocus? outlineColor : btnDisactiveBorder

                        border.width: parent.activeFocus ? 1 : 0
                    }
        }

        Item{
            FileDialog {
                id: fileDialog
                title: "Please choose a file"
                folder: shortcuts.desktop
                onAccepted: {
                    client.loadScript(fileDialog.fileUrls)
                }
                onRejected: {
                    console.log("Canceled")
                }
            }
        }


        Button{
            height: parent.height
            onClicked: {
                fileDialog.visible = true
            }
            contentItem: Text {
                text: "Load Script"
                    font.pixelSize: 16
                    color: parent.down ? btnTextDown : btnText
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    elide: Text.ElideRight
                }
            background: Rectangle {
                        implicitWidth: 100
                        implicitHeight: 30
                        color: parent.down ? outlineColor : btnDisactiveBg
                        border.color: parent.activeFocus? outlineColor : btnDisactiveBorder

                        border.width: parent.activeFocus ? 1 : 0
                    }
        }
    }

}
