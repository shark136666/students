QT += quick

QT += qml
QT += widgets
QT += core
QT += network
win32:RC_ICONS += settings.ico

# You can make your code fail to compile if it uses deprecated APIs.
# In order to do so, uncomment the following line.
#DEFINES += QT_DISABLE_DEPRECATED_BEFORE=0x060000    # disables all the APIs deprecated before Qt 6.0.0

SOURCES += \
        client.cpp \
        main.cpp

RESOURCES += qml.qrc

# Additional import path used to resolve QML modules in Qt Creator's code model
QML_IMPORT_PATH =

# Additional import path used to resolve QML modules just for Qt Quick Designer
QML_DESIGNER_IMPORT_PATH =

# Default rules for deployment.
qnx: target.path = /tmp/$${TARGET}/bin
else: unix:!android: target.path = /opt/$${TARGET}/bin
!isEmpty(target.path): INSTALLS += target

# ----------------DEPLOY------------------
isEmpty(TARGET_EXT) {
    win32 {
        TARGET_CUSTOM_EXT = .exe
    }
} else {
    TARGET_CUSTOM_EXT = $${TARGET_EXT}
}

win32 {
    DEPLOY_COMMAND = windeployqt
}

CONFIG( debug, debug|release ) {
    # debug
    DEPLOY_TARGET = $$shell_quote($$shell_path($${OUT_PWD}/debug/$${TARGET}$${TARGET_CUSTOM_EXT}))
} else {
    # release
    DEPLOY_TARGET = $$shell_quote($$shell_path($${OUT_PWD}/release/$${TARGET}$${TARGET_CUSTOM_EXT}))
}
QMAKE_POST_LINK = $${DEPLOY_COMMAND} $${DEPLOY_TARGET}
# --------------END--DEPLOY----------------

HEADERS += \
    client.h

DISTFILES +=
