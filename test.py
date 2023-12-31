import assistant_sdk

# Set up the Google Assistant SDK
credentials = assistant_sdk.get_credentials_from_file('token.pickle')
request = assistant_sdk.Request()
assistant = assistant_sdk.Assistant(credentials=credentials, request=request)

def handle_assistant_response(assistant_response):
    # Check if the response contains the "open blinds" command
    print(assistant_response) 

# Start the Google Assistant conversation
assistant.start()
while True:
    assistant.wait_for_response(handle_assistant_response)
