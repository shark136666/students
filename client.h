#ifndef CLIENT_H
#define CLIENT_H

#include <QObject>

class Client : public QObject
{
    Q_OBJECT
    Q_PROPERTY(QString address READ address WRITE setAddress NOTIFY addressChanged)
    Q_PROPERTY(QString port READ port WRITE setPort NOTIFY portChanged)


public:
    explicit Client(QObject *parent = nullptr);

    QString address()const;
    void setAddress(const QString &);
    QString port()const;
    void setPort(const QString &);

    Q_INVOKABLE void sendCommand(const QString& str);
    Q_INVOKABLE void connect(const QString& str);

signals:
    void addressChanged();
    void portChanged();

private:
    QString mAddress;
    QString mPort;
};

#endif // CLIENT_H
