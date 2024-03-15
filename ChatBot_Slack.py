from flask import Flask, request, jsonify
import os
import requests
import ssl

app = Flask(__name__)

# Slack Bot User OAuth Access Token
SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')


# Slack Events API Endpoint
@app.route('/slack/events', methods=['GET', 'POST'])
def slack_events():
    #data = request.json
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()
    if 'challenge' in data:
        return jsonify({'challenge': data['challenge']})

    # Handle events
    if 'event' in data:
        event = data['event']
        if event.get('type') == 'message' and 'subtype' not in event:
            # Handle message events
            user_id = event.get('user')
            text = event.get('text')
            channel = event.get('channel')
            if user_id != 'A06NR8JDLF5':  # Exclude messages from the bot itself
                # Process the message and send a response
                response = process_message(text)
                send_message(channel, response)

    return '', 200


# Function to process incoming messages
def process_message(text):
    # Sample response logic
    if 'hello' in text.lower():
        return "Hello there!"
    elif 'how are you' in text.lower():
        return "I'm just a bot, but I'm doing well, thank you for asking!"
    else:
        return "Sorry, I didn't understand that."


# Function to send a message to Slack channel
def send_message(channel, text):
    url = 'https://slack.com/api/chat.postMessage'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {SLACK_BOT_TOKEN}'
    }
    data = {
        'channel': channel,
        'text': text
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        print(f"Failed to send message to channel {channel}")


if __name__ == '__main__':
    #context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    #context.load_cert_chain('/Users/amitkunjir/cert.pem', '/Users/amitkunjir/key.pem')
    app.run(debug=True)