#include "client.h"
#include "qdebug.h"
#include <QFile>

Client::Client(QObject *parent)
    : QObject{parent}
{
    mIsConnected = false;
}

QString Client::address() const
{
    return mAddress;
}

void Client::setAddress(const QString & str)
{
    mAddress = str;
    emit addressChanged();
}

int Client::port() const
{
    return mPort;
}

void Client::setPort(const int &str)
{
    mPort = str;
    emit portChanged();
}

bool Client::isConnected() const
{
    return mIsConnected;
}

void Client::setIsConnected(const bool &value)
{
    mIsConnected = value;
    emit isConnectedChanged();
}

int Client::x() const
{
    return mX;
}

void Client::setX(const int &value)
{
    mX = value;
    emit xChanged();
}

int Client::y() const
{
    return mY;
}

void Client::setY(const int &value)
{
    mY = value;
    emit yChanged();
}

void Client::doConnect()
{
    if(mIsConnected){
        socket->close();
        return;
    }
    socket = new QTcpSocket(this);

    if(port() == 0 || address() == 0) return;

    connect(socket, &QAbstractSocket::connected,this, &Client::connected);
    connect(socket, &QAbstractSocket::disconnected,this, &Client::disconnected);
    connect(socket, &QAbstractSocket::readyRead, this, &Client::readyRead);

    socket->connectToHost(address(), port());

    if(!socket->waitForConnected(5000))
    {
        emit error( socket->errorString() );
    }
}

void Client::loadScript(const QString &str)
{
    QString s = str;
    s.replace(0, 8, "");
    QFile file(s);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text))
            return;
    while (!file.atEnd()) {
            QByteArray line = file.readLine();
            sendCommand(line);
        }
}

void Client::sendCommand(const QString& str)
{
    if(!mIsConnected) return;

    QByteArray data = str.toUtf8();
    socket->write(data);
    socket->write("\n");
    emit commandSent(data);
}

void Client::connected()
{
    setIsConnected(true);
    emit wasConnect();
}

void Client::disconnected()
{
    setIsConnected(false);
    emit wasDisconnect();
}

void Client::readyRead()
{
    auto data = socket->readAll();
    emit dataRecieved(data);
}
