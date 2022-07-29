import QtQuick 2.0
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.3

RowLayout{
    width: parent.width
    height: 30

    TextField{
        id: tf
        Layout.fillWidth: true
        Layout.minimumWidth: 300
        Layout.preferredWidth: 300
        Layout.preferredHeight: 30
        text: model.display
        font.pixelSize: 16
        selectByMouse: true
        background: Rectangle {
                anchors.margins: 0
                color: "transparent"
                border.width: 1
            }
        onEditingFinished: {
            model.display = tf.displayText
        }
    }
    Button{
        id: startBtn
        Layout.preferredHeight: 30
        text: "START"
        font.pixelSize: 16
        background: Rectangle {
                implicitWidth: 100
                implicitHeight: 40
                border.width: 1
                radius: 2
            }
        onClicked: {
            client.sendCommand(tf.displayText);
        }
    }
}
