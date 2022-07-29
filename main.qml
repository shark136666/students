import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Layouts 1.3
import QtQuick.Controls 2.15

Window {
    id: win
    minimumWidth: 720
    minimumHeight: 480
    visible: true
    title: qsTr("SUPAPP")

    Rectangle{
        height:parent.height
        width:parent.width
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: 20

        ColumnLayout{
            ConnectForm {
                id: connectForm
                height: 30
                spacing: 20
                width: parent.width
            }

//            CommandForm {
//                id: commandForm
//                height: 30
//                spacing: 20
//                width: parent.width
//            }
            Rectangle{
                id: commandsList
                Layout.preferredWidth: parent.width
                Layout.preferredHeight: 200
                color: "#DDD"
                radius: 5

                ListView {
                    width: parent.width;
                    height: parent.height
                    spacing: 2
                    clip: true

                    model: commandModel
                    delegate: CommandListItem{}
                }
            }
            Rectangle{
                id: logList
                Layout.alignment: Qt.AlignBottom
                Layout.preferredWidth: parent.width
                Layout.preferredHeight: 150
                color: "#DDD"
                radius: 5

                ListView {
                    width: parent.width;
                    height: parent.height
                    spacing: 2

                    model: logModel
                    delegate: LogListItem{}
                }
            }
        }
    }

}
