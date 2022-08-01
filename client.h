#ifndef CLIENT_H
#define CLIENT_H

#include <QObject>
#include "qtcpsocket.h"

class Client : public QObject
{
    Q_OBJECT
    Q_PROPERTY(QString address READ address WRITE setAddress NOTIFY addressChanged)
    Q_PROPERTY(int port READ port WRITE setPort NOTIFY portChanged)
    Q_PROPERTY(bool isConnected READ isConnected NOTIFY isConnectedChanged)


public:
    explicit Client(QObject *parent = nullptr);

    QString address()const;
    void setAddress(const QString &);

    int port()const;
    void setPort(const int &);

    bool isConnected()const;
    void setIsConnected(const bool &);

    Q_INVOKABLE void sendCommand(const QString& str);
    Q_INVOKABLE void doConnect();
    Q_INVOKABLE void loadScript(const QString& str);


public slots:
    void connected();
    void disconnected();
    void readyRead();

signals:
    void addressChanged();
    void portChanged();
    void isConnectedChanged();

    void commandSent(QString);
    void dataRecieved(QString);
    void error(QString);
    void wasConnect();
    void wasDisconnect();

private:
    QTcpSocket *socket;
    QString mAddress;
    int mPort;
    bool mIsConnected;
    QString logString;
};

#endif // CLIENT_H
