import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Layouts 1.3
import QtQuick.Controls 2.15

Window {
    id: win
    minimumWidth: connectForm.width + 20
    minimumHeight: 680
    visible: true
    color: "#fff"
    title: qsTr("SocketTester_2.0")

    property int defMargin: 10
    property string outlineColor: "#00A1FA"
    property string btnActiveBg: "#d6d6d6"
    property string btnDisactiveBg: "#f6f6f6"
    property string btnActiveBorder: "#000"
    property string btnDisactiveBorder: "#26282a"
    property string btnText: "#333"
    property string btnTextDown: "#fff"

    Rectangle{
        anchors.fill: parent
        anchors.margins: defMargin
        radius: 5
        color: "transparent"

        ColumnLayout{
            anchors.fill: parent
            id: mainCol
            ConnectForm {
                id: connectForm
                Layout.preferredHeight: 50
                Layout.preferredWidth: 900
            }


            Rectangle{
                id: commandsList
                Layout.topMargin: 20
                Layout.bottomMargin: 20
                Layout.preferredWidth: parent.width
                Layout.preferredHeight: 225
                color: "#ddd"
                radius: 5
                clip: true

                ListView {
                    anchors.fill: parent
                    anchors.margins: 10
                    width: parent.width;
                    height: parent.height
                    spacing: 5
                    clip: true

                    model: commandModel
                    delegate: CommandListItem{}
                }
            }
            Button{
                Layout.preferredHeight: 30
                contentItem: Text {
                        text: "CLEAR"
                        font.pixelSize: 14
                        font.letterSpacing: 1
                        color: parent.down ? "#fff" : "#00A1FA"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        elide: Text.ElideRight
                    }
                background: Rectangle {
                            color: parent.down ? "#00A1FA" : "transparent"
                            border.color: "#00A1FA"
                            border.width: parent.activeFocus ? 2 : 1
                        }
                onClicked: {
                    listModel.clear()
                }
            }
            Rectangle{
                id: logList
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.preferredHeight: 350
                Layout.alignment: Qt.AlignBottom
                color: "#ddd"
                radius: 5

                Connections {
                    target: client
                    function onWasConnect(str) {
                        listModel.clear()
                        listModel.append({display: "<Connected>"})
                    }
                    function onWasDisconnect(str) {
                        listModel.append({display: "<Disconnected>"})
                    }
                    function onCommandSent(str) {
                        listModel.append({display: "> "+str})
                    }
                    function onDataRecieved(str) {
                        listModel.append({display: "< "+str})
                    }
                    function onError(str) {
                        listModel.append({display: "< "+str})
                    }
                }

                Rectangle{
                    anchors.fill: parent
                    anchors.margins: 10
                    color: "transparent"

                    ListView {
                        width: parent.width;
                        height: parent.height
                        ScrollBar.vertical: ScrollBar {
                            policy: ScrollBar.AlwaysOn
                        }
                        spacing: 2
                        model: ListModel {
                            id: listModel
                        }
                        delegate: LogListItem{}
                    }
                }


            }
        }
    }

}
