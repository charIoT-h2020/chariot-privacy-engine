class Engine(object):
    def __init__(self, client):
        self.client = client

    def subscribe_to_southbound(self):
        self.client.subscribe('temperature/#')

    def publish(self, topic, value):
        self.client.publish(topic, value)

    @staticmethod
    def on_message(client, userdata, message):
        print("message received ", str(message.payload.decode("utf-8")))
        print("message topic=", message.topic)
        print("message qos=", message.qos)
        print("message retain flag=", message.retain)

    @staticmethod
    def on_log(client, userdata, level, buf):
        print("log: ", buf)
