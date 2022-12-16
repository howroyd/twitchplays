from time import sleep, time
from python_twitch_irc import TwitchIrc

# Simple echo bot.
class MyOwnBot(TwitchIrc):
    def on_connect(self):
         self.join('#bepis')

    # Override from base class
    def on_message(self, timestamp, tags, channel, user, message):
        self.message(channel, message)

if __name__ == '__main__':
    client = MyOwnBot('MyBot', 'MyTwitchOAuthToken').start()
    client.handle_forever()