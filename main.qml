import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Layouts 1.3
import QtQuick.Controls 2.15

ApplicationWindow  {
    id: win
    width: client.width
    height: client.height

    visible: true
    color: "#fff"
    title: qsTr("SocketTester_2.0")
    x: client.x
    y: client.y

    Connections {
          target: Qt.application

          onAboutToQuit: {
              client.x = win.x
              client.y = win.y
              client.width = win.width
              client.height = win.height
          }
    }

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
                Layout.preferredWidth: 860
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
                Layout.preferredWidth: parent.width
                Layout.fillHeight: true
                color: "#ddd"
                radius: 5
                Connections {
                    target: client
                    function getTime(){
                        var date = new Date()
                        var hours = date.getHours() > 9 ? date.getHours() : "0"+date.getHours()
                        var minutes = date.getMinutes() > 9 ? date.getMinutes() : "0"+date.getMinutes()
                        var seconds = date.getSeconds() > 9 ? date.getSeconds() : "0"+date.getSeconds()
                        return `${hours}:${minutes}:${seconds}`
                    }

                    function onWasConnect(str) {
                        listModel.clear()
                        listModel.append({display: `${getTime()} <Connected>`})
                    }
                    function onWasDisconnect(str) {
                        listModel.append({display: `${getTime()} <Disconnected>`})
                    }
                    function onCommandSent(str) {
                        listModel.append({display: `${getTime()} > `+str})
                    }
                    function onDataRecieved(str) {
                        listModel.append({display: `${getTime()} < `+str})
                    }
                    function onError(str) {
                        listModel.append({display: `${getTime()} < `+str})
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
                        spacing: 4
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
