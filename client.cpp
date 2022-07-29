#include "client.h"
#include "qdebug.h"

Client::Client(QObject *parent)
    : QObject{parent}
{

}

QString Client::address() const
{
    return mAddress;
}

void Client::setAddress(const QString & str)
{
        mAddress = str;
}

QString Client::port() const
{
    return mPort;
}

void Client::setPort(const QString &str)
{
    mPort = str;
}

void Client::sendCommand(const QString& str)
{
    qDebug() << str;
}

void Client::connect(const QString &str)
{
    qDebug() << str;
}

