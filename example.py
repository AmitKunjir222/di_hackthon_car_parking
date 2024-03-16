import asyncio
from slack_bolt import App
from slackeventsapi import SlackEventAdapter
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from connection import connect_to_database, close_connection, get_parking_availability, \
    update_parking_status_empty_to_occupied, update_parking_status_occupied_to_empty, fetch_car_details
from slack_sdk.web.async_client import AsyncWebClient
import ssl
import logging

logging.basicConfig(level=logging.INFO)
ssl._create_default_https_context = ssl._create_unverified_context

# Our app's Slack Event Adapter for receiving actions via the Events API
slack_signing_secret = "65d0215fbc5c17a1a428a933a8065ec8"
slack_events_adapter = SlackEventAdapter(slack_signing_secret, "/slack/events")
app = App(token="xoxb-6796189247472-6786066632209-SD3g8UmVtOXRwnoJOX08U767", signing_secret=slack_signing_secret)

# Create a SlackClient for your bot to use for Web API requests
slack_bot_token = "xoxb-6796189247472-6786066632209-SD3g8UmVtOXRwnoJOX08U767"

web_client = AsyncWebClient(token=slack_bot_token, timeout=60)  # Set timeout to 5 seconds

# Use the initialized WebClient for making Slack API calls
slack_client = web_client
# slack_client = WebClient(slack_bot_token)


@app.message("hi")
def respond_to_hi(message, say):
    # Respond to the "hi" message with a message containing multiple centered buttons
    say({
	"blocks": [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": " "
			}
		},
		{
			"type": "actions",
			"block_id": "centered_buttons",
			"elements": [
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Available Slots",
						"emoji": True
					},
                    "style": "primary",
					"action_id": "button_click_1"
				},
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Car Details",
						"emoji": True
					},
                    "style": "primary",
					"action_id": "button_click_2"
				}
			]
		},
		{
			"type": "divider"
		}
	]
})


@app.action("button_click")
def handle_button_click(ack, body, client):
    # Acknowledge the button click
    ack()

    # Get information about the button click
    user_id = body["user"]["id"]
    channel_id = body["channel"]["id"]
    action_id = body["actions"][0]["action_id"]

    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")

    # If button 1 is clicked, fetch data from the database and display corresponding buttons
    if action_id == "button_click_1":
        # Fetch data from the database asynchronously
        print("Fetching data from the database...")


@app.action("button_click_1")  # Listener function for button_click_1 action
async def handle_button_click_1(ack, body, client):
    try:
         await asyncio.wait_for(ack(), timeout=20)  # Set acknowledgment timeout to 3 seconds
    except asyncio.TimeoutError:
        print("Acknowledgment timed out")

    #await ack()  # Acknowledge the button click
    user_id = body["user"]["id"]
    channel_id = body["channel"]["id"]
    action_id = body["actions"][0]["action_id"]
    data_from_db = await get_parking_availability(client)
    await send_buttons_based_on_db_data(channel_id, data_from_db, client)


async def send_buttons_based_on_db_data(channel_id, data_from_db, client):
    # Create buttons based on the data from the database
    button_elements = [
        {
            "type": "button",
            "text": {
                "type": "plain_text",
                "text": option,
                "emoji": True
            },
            "action_id": f"selected_option_{index+1}"  # Unique action ID for each button
        } for index, option in enumerate(data_from_db)
    ]

    # Send a message with the buttons
    try:
        response = await client.chat_postMessage(
            channel=channel_id,
            text="Please select an option:",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Please select an option:"
                    },
                    "accessory": {
                        "type": "actions",
                        "block_id": "dynamic_buttons",
                        "elements": button_elements
                    }
                }
            ]
        )
    except SlackApiError as e:
        # Handle errors if message sending fails
        print(f"Error sending message: {e.response['error']}")

# Function to fetch data from the database asynchronously
async def fetch_data_from_db():
    # Your code to fetch data from the database goes here
    # For example, you might use an async database client like AsyncIO
    # Replace this with your actual database query
    await asyncio.sleep(1)  # Simulating asynchronous database query
    data_from_db = ["Option 1", "Option 2", "Option 3"]
    return data_from_db

# Example responder to bot mentions
@slack_events_adapter.on("app_mention")
def handle_mentions(event_data):
    event = event_data["event"]
    slack_client.chat_postMessage(
        channel=event["channel"],
        text=f"You said:\n>{event['text']}",
    )


# Example responder to greetings
# @slack_events_adapter.on("message")
# def handle_message(event_data):
#     message = event_data["event"]
#     # If the incoming message contains "hi", then respond with a "Hello" message
#     if message.get("subtype") is None and "hi" in message.get('text'):
#         channel = message["channel"]
#         message = "Hello <@%s>! :tada:" % message["user"]
#         slack_client.chat_postMessage(channel=channel, text=message)
@app.event("message")
def handle_message(event, say):
    # Extract relevant information from the event
    channel_id = event["channel"]
    user_id = event["user"]
    text = event.get("text", "")

    # Check if the message contains "hello"
    if "hello" in text.lower():
        # Respond to the message with a greeting
        say(f"Hello <@{user_id}>! :wave:")

# Example reaction emoji echo
@slack_events_adapter.on("reaction_added")
def reaction_added(event_data):
    event = event_data["event"]
    emoji = event["reaction"]
    channel = event["item"]["channel"]
    text = ":%s:" % emoji
    slack_client.chat_postMessage(channel=channel, text=text)


# Error events
@slack_events_adapter.on("error")
def error_handler(err):
    print("ERROR: " + str(err))


# Check-in command
@app.command("/available_slots")
def checkin_command(ack, client, command, body):
    ack()
    user_id = body["user_id"]
    channel_id = body["channel_id"]
    username = ''
    # Retrieve username from Slack user ID
    try:
        user_info = client.users_info(user=user_id)
        username = user_info["user"]["real_name"]
        print("username", username)
    except SlackApiError as e:
        print("Error retrieving user info:", e)
        return
    connection = connect_to_database()
    print("Connection {}", format(connection))
    if connection:
        print("Inside Connection")
        # Retrieve available parking slots
        parking_slots = get_parking_availability(connection)

        print("Inside Connection {}".format(str(parking_slots)))
        # if parking_slots:
        #     # Display available slots to the user
        #     # message = f"Hello {username}, please select an empty slot to park your vehicle:"
        #     # options = []
        #     # for slot in parking_slots:
        client.chat_postMessage(
                channel=channel_id,  # Specify the channel where you want to post the message
                text="<@{}> - Available slots are {}".format(user_id, str(parking_slots))
        )
        close_connection(connection)


@app.command("/park")
def park_command(ack, client, command, body):
    ack()
    user_id = body["user_id"]
    channel_id = body["channel_id"]
    username = ''

    try:
        user_info = client.users_info(user=user_id)
        username = user_info["user"]["real_name"]
        print("username", username)
    except SlackApiError as e:
        print("Error retrieving user info:", e)

    arguments = command["text"].split()
    # Retrieve username from Slack user ID

    connection = connect_to_database()
    print("Connection {}", format(connection))
    message = ''
    if connection:
        if len(arguments) == 1:
            message = update_parking_status_empty_to_occupied(connection, username, Parking_Slot_Number=arguments[0])
        elif len(arguments) == 2:
            message = update_parking_status_empty_to_occupied(connection, username, Parking_Slot_Number=arguments[0], admin_passed_employee_name=arguments[1])
        else:
            print("No arguments provided")
        print("Inside park")
        # Retrieve available parking slots

        client.chat_postMessage(
                channel=channel_id,  # Specify the channel where you want to post the message
                text="{} - {}".format(username, str(message))
            )
        close_connection(connection)


@app.command("/unpark")
def unpark_command(ack, client, command, body):
    ack()
    user_id = body["user_id"]
    channel_id = body["channel_id"]
    username = ''
    print("user_id", user_id)

    try:
        user_info = client.users_info(user=user_id)
        username = user_info["user"]["real_name"]
        print("username", username)
    except SlackApiError as e:
        print("Error retrieving user info:", e)

    arguments = command["text"].split()
    # Retrieve username from Slack user ID

    connection = connect_to_database()
    print("Connection {}", format(connection))
    message = ''
    if connection:
        if len(arguments) == 1:
            message = update_parking_status_occupied_to_empty(connection, username, Parking_Slot_Number=arguments[0])
        elif len(arguments) == 2:
            message = update_parking_status_occupied_to_empty(connection, username, Parking_Slot_Number=arguments[0], admin_passed_employee_name=arguments[1])
        else:
            print("No arguments provided")
        print("Inside park")
        # Retrieve available parking slots

        client.chat_postMessage(
                channel=channel_id,  # Specify the channel where you want to post the message
                text="{} - {}".format(username, str(message))
            )
        close_connection(connection)


@app.command("/car_details")
def car_details_command(ack, client, command, body):
    ack()
    user_id = body["user_id"]
    channel_id = body["channel_id"]
    username = ''
    print("user_id", user_id)

    try:
        user_info = client.users_info(user=user_id)
        username = user_info["user"]["real_name"]
        print("username", username)
    except SlackApiError as e:
        print("Error retrieving user info:", e)

    arguments = command["text"].split()
    # Retrieve username from Slack user ID

    connection = connect_to_database()
    message = ''
    if connection:
        if arguments:
            message = fetch_car_details(connection, arguments[0])
        else:
            print("No arguments provided")
        print("Inside park")
        # Retrieve available parking slots

        client.chat_postMessage(
                channel=channel_id,  # Specify the channel where you want to post the message
                text="{} - {}".format(username, str(message))
            )
        close_connection(connection)


# Once we have our event listeners configured, we can start the
# Flask server with the default `/events` endpoint on port 3000
#slack_events_adapter.start(port=3000)
app.start(port=int(os.environ.get("PORT", 3000)))
