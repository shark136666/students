#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QStringListModel>
#include <QQuickView>
#include <QQmlContext>
#include <QSettings>
#include <iostream>
#include <client.h>

using namespace std;


int main(int argc, char *argv[])
{

#if QT_VERSION < QT_VERSION_CHECK(6, 0, 0)
    QCoreApplication::setAttribute(Qt::AA_EnableHighDpiScaling);
#endif
    QGuiApplication app(argc, argv);
    app.setWindowIcon(QIcon("favicon.png"));
    //были предупреждения, эти строчки исправили
    app.setOrganizationName("Planar");
    app.setOrganizationDomain("planarchel.ru");
    app.setApplicationName("SocketTester_2.0");

    //считывание команд из конфига
    QSettings settings("config.ini", QSettings::IniFormat);
    QStringList commandList = settings.value("commandList").toStringList();

    //добавление пустых ячеек если < 6
    while(commandList.size() < 6)
        commandList << "";

    //считывание адресса и порта из конфига
    QString address = settings.value("address").toString();
    int port = settings.value("port").toInt();


    QQmlApplicationEngine engine;
    const QUrl url(QStringLiteral("qrc:/main.qml"));
    QObject::connect(&engine, &QQmlApplicationEngine::objectCreated,
                     &app, [url](QObject *obj, const QUrl &objUrl) {
        if (!obj && url == objUrl)
            QCoreApplication::exit(-1);
    }, Qt::QueuedConnection);

    //добавление клиента в контекст
    Client client;
    client.setPort(port);
    client.setAddress(address);
    engine.rootContext()->setContextProperty("client", &client);

    //создание модели комманд
    QStringListModel commandModel;
    commandModel.setStringList(commandList);
    engine.rootContext()->setContextProperty("commandModel", &commandModel);

    engine.load(url);

    int res = app.exec();
    //сериализация команд
    settings.setValue("port", client.port());
    settings.setValue("address", client.address());
    settings.setValue("commandList", commandModel.stringList());
    return res;
}
