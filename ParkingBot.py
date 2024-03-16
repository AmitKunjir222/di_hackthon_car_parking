import asyncio
import time

from slack_bolt import App
from slackeventsapi import SlackEventAdapter
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from DB_Connection_Util import connect_to_database, close_connection, get_parking_availability, \
    update_parking_status_empty_to_occupied, update_parking_status_occupied_to_empty, fetch_car_details, \
    get_employee_and_car_details
from slack_sdk.web.async_client import AsyncWebClient
import ssl
import logging

logging.basicConfig(level=logging.INFO)
ssl._create_default_https_context = ssl._create_unverified_context

car_no = ''
channel_id_rm = ''
ts_rm = ''

# Our app's Slack Event Adapter for receiving actions via the Events API
slack_signing_secret = "65d0215fbc5c17a1a428a933a8065ec8"
slack_events_adapter = SlackEventAdapter(slack_signing_secret, "/slack/events")
app = App(token="xoxb-6796189247472-6786066632209-68I1JwWRigGmVkPEWV66eHhg", signing_secret=slack_signing_secret)

# Create a SlackClient for your bot to use for Web API requests
slack_bot_token = "xoxb-6796189247472-6786066632209-68I1JwWRigGmVkPEWV66eHhg"

web_client = AsyncWebClient(token=slack_bot_token, timeout=60)  # Set timeout to 5 seconds

# Use the initialized WebClient for making Slack API calls
slack_client = web_client

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
            message = update_parking_status_empty_to_occupied(connection, username, Parking_Slot_Number=arguments[0],
                                                              admin_passed_employee_name=arguments[1])
        else:
            print("No arguments provided")
        print("Inside park")
        # Retrieve available parking slots

        client.chat_postMessage(
            channel=channel_id,  # Specify the channel where you want to post the message
            text="*{}*".format(str(message))
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
            message = update_parking_status_occupied_to_empty(connection, username, Parking_Slot_Number=arguments[0],
                                                              admin_passed_employee_name=arguments[1])
        else:
            print("No arguments provided")
        print("Inside park")
        # Retrieve available parking slots

        client.chat_postMessage(
            channel=channel_id,  # Specify the channel where you want to post the message
            text="*{}*".format(str(message))
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


@app.command("/current_status")
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

    #arguments = command["text"].split()
    # Retrieve username from Slack user ID

    connection = connect_to_database()
    message = ''
    if connection:
        message = get_employee_and_car_details(connection)
        new_message = ''
        for k,v in message.items():
            for k,v in v.items():
                print("\n")
                new_message += "{}: {} |".format(k, v)
                print("\n")


        # Retrieve available parking slots

        client.chat_postMessage(
            channel=channel_id,  # Specify the channel where you want to post the message
            text="{} - {}".format(username, str(new_message))
        )
        close_connection(connection)


@app.message("hi")
def respond_to_hi(message, say):
    # Respond to the "hi" message with a message containing multiple centered buttons
    say({
        "blocks": [
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Welcome to DI :oncoming_automobile: Parking*"
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
                            "text": ":oncoming_automobile: Car Details",
                            "emoji": True
                        },
                        "style": "primary",
                        "action_id": "button_click_1"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": ":factory_worker: Check Current Status",
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


@app.action("plain_text_input-action")
def handle_block_action(ack, body, client):
    global car_no
    global channel_id_rm
    global ts_rm
    # Acknowledge the action
    ack()

    # Extract input text from the action
    input_text = body["actions"][0]["value"]

    car_no = input_text

    channel_id = body["channel"]["id"]
    ts = body["message"]["ts"]

    # Respond by printing the input text
    print("Input text:", input_text)
    #remove_input_text_block(client, channel_id, ts)


@app.action("button_click_1")
def fetch_car_details_action(say, ack, body, respond):
    global car_no
    employee_name, team, floor, mobile = '', '', '', ''
    ack()
    data = ''
    say({
        "blocks": [
            {
                "dispatch_action": True,
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "plain_text_input-action"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Enter Car No",
                    "emoji": True
                }
            }
        ]
    })

    time.sleep(6)

    car_no1 = car_no
    # Fetch data from the database
    connection = connect_to_database()
    print("Connection {}", format(connection))
    if connection:
        print("Inside Connection ava")
        # Retrieve available parking slots
        car_details = fetch_car_details(connection, car_no1)
        details_message = ''
        if type(car_details) is dict:
            for k, v in car_details.items():
                if k == 'team':
                    team = v
                elif k == 'floor':
                    floor = v
                elif k == 'mobile':
                    mobile = v
                elif k == 'employee_name':
                    employee_name = v
            details_message = car_details
        else:
            details_message = car_details

    # Send the data to the user
    respond(
        blocks=[
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": ":oncoming_automobile:" + details_message
                }
            },
            {
                "type": "divider"
            }
        ]
    )


@app.action("button_click_2")
def fetch_current_parking_status(say, ack, body, respond):
    ack()

    # Fetch data from the database
    connection = connect_to_database()
    if connection:
        # Retrieve available parking slots
        e_car_details = get_employee_and_car_details(connection)
        details_message = ''
        say(
            blocks=[
                {
                    "type": "divider"
                }
            ]
        )
        for k, v in e_car_details.items():
            details_message = " *Employee Name* - " + str(e_car_details[k]['employee_name']) + "    *Car No* - " + str(e_car_details[k]['car_no']) + "    *Mobile* - " + str(e_car_details[k]['mobileno']) +"    *Parking Slot Number* - " + str(e_car_details[k]['Parking_Slot_Number'])+"    *Status* - " + str(e_car_details[k]['Status'])

            say(
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": ":oncoming_automobile:" + details_message
                        }
                    }
                ]
            )
        say(
            blocks=[
                {
                    "type": "divider"
                }
            ]
        )


def remove_input_text_block(client, channel_id, timestamp):
    try:
        client.chat_delete(
            channel=channel_id,
            ts=timestamp
        )
    except SlackApiError as e:
        print(f"Error deleting message: {e.response['error']}")


# Once we have our event listeners configured, we can start the
# Flask server with the default `/events` endpoint on port 3000
# slack_events_adapter.start(port=3000)
app.start(port=int(os.environ.get("PORT", 3000)))
