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
#qnx: target.path = /tmp/$${TARGET}/bin
#else: unix:!android: target.path = /opt/$${TARGET}/bin
#!isEmpty(target.path): INSTALLS += target

# ----------------DEPLOY------------------

CONFIG(release, debug|release) {
    DESTDIR = $$PWD/../SocketTester_2.0
}

RETURN = $$escape_expand(\n\t)
#QMAKE_POST_LINK += $$RETURN command1

defineTest(windeployqtInDESTDIR) {
    ARGS = --qmldir $$PWD/../test
    RETURN = $$escape_expand(\n\t)
    QMAKE_POST_LINK += $$RETURN windeployqt $$ARGS $$quote($$shell_path($$DESTDIR))
    export(QMAKE_POST_LINK)
}
PACKAGES = "--compiler-runtime"
for(package,QT){
    PACKAGES += "--$${package} "
}
PACKAGES += --no-svg --no-system-d3d-compiler --no-translations --no-opengl-sw --no-angle
windeployqtInDESTDIR($$PACKAGES)

# --------------END--DEPLOY----------------

HEADERS += \
    client.h

DISTFILES +=
