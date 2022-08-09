import QtQuick 2.0
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.3

RowLayout{
    width: parent.width
    height: 30
    spacing: 20

    TextField{
        id: tf
        Layout.fillWidth: true
        Layout.minimumWidth: 200
        Layout.preferredWidth: 300
        Layout.preferredHeight: 30
        text: model.display
        font.pixelSize: 16
        selectByMouse: true
        selectionColor:  "#94DCFA"
        background: Rectangle {
                color: parent.activeFocus ? "#fff" : "#f6f6f6"
                border.width: parent.activeFocus ? 1 : 0
                border.color: outlineColor
            }
        onEditingFinished: {
            model.display = tf.displayText
        }
    }
    Button{
        id: startBtn
        Layout.preferredHeight: 30
        contentItem: Text {
                text: "START"
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
        onClicked: {
            client.sendCommand(tf.displayText);
        }
    }
}
