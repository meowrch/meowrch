import QtQuick 2.12
import QtQuick.Controls 2.12

TextField {
    id: passwordField

    focus: true
    selectByMouse: true
    placeholderText: "Password"
    echoMode: TextInput.Password
    passwordCharacter: "•"
    passwordMaskDelay: 1000
    selectionColor: config.TextFieldHighlightColor
    
    renderType: Text.NativeRendering
    font.family: config.Font
    font.pointSize: config.GeneralFontSize
    font.bold: true
    color: config.TextFieldHighlightColor
    horizontalAlignment: TextInput.AlignHCenter
    
    background: Rectangle {
        id: passFieldBg

        color: config.TextFieldColor
        border.color: config.TextFieldHighlightColor
        border.width: 0
        radius: config.CornerRadius
    }

    states: [
        State {
            name: "focused"
            when: passwordField.activeFocus
            PropertyChanges {
                target: passFieldBg
                color: Qt.darker(config.TextFieldColor, 1.2)
                border.width: 3
            }
        },
        State {
            name: "hovered"
            when: passwordField.hovered
            PropertyChanges {
                target: passFieldBg
                color: Qt.darker(config.TextFieldColor, 1.2)
            }
        },
        State {
            name: "error"
            when: false
            PropertyChanges {
                target: passFieldBg
                border.color: Qt.darker(config.TextFieldErrorColor, 1.2)
                border.width: 3
            }
        }
    ]

    transitions: Transition {
        PropertyAnimation {
            properties: "color, border.width"
            duration: 150
        }
    }
}
