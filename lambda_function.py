### Required Libraries ###
from datetime import datetime
from dateutil.relativedelta import relativedelta

### Functionality Helper Functions ###
def parse_int(n):
    """
    Securely converts a non-integer value to integer.
    """
    try:
        return int(n)
    except ValueError:
        return float("nan")


def build_validation_result(is_valid, violated_slot, message_content):
    """
    Define a result message structured as Lex response.
    """
    if message_content is None:
        return {"isValid": is_valid, "violatedSlot": violated_slot}

    return {
        "isValid": is_valid,
        "violatedSlot": violated_slot,
        "message": {"contentType": "PlainText", "content": message_content},
    }


### Dialog Actions Helper Functions ###
def get_slots(intent_request):
    """
    Fetch all the slots and their values from the current intent.
    """
    return intent_request["currentIntent"]["slots"]


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    """
    Defines an elicit slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "ElicitSlot",
            "intentName": intent_name,
            "slots": slots,
            "slotToElicit": slot_to_elicit,
            "message": message,
        },
    }


def delegate(session_attributes, slots):
    """
    Defines a delegate slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {"type": "Delegate", "slots": slots},
    }


def close(session_attributes, fulfillment_state, message):
    """
    Defines a close slot type response.
    """

    response = {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": fulfillment_state,
            "message": message,
        },
    }

    return response

### NEED A FUNCTION FOR LIMITING USERS TO AGE 0-64 
### AND KEEPING INVESTMENT AMOUNT 5000 OR MORE
### YOUR DATA VALIDATION CODE STARTS HERE ###
def validate_userdata(age, investment_amount,intent_request):
#validate input of age 
    # Validate that the user is over between 0-64 years old
    if age is not None:
        if age <=0:
            return build_validation_result(
                False,
                "age",
                "You must be at least 0 years old to use this service, "
                "please provide your age between 0-64.",
            )
        elif age>=65:
            return build_validation_result(
                False,
                "age",
                "You must be younger than 65 years old to use this service, "
                "please provide your age between 0-64.",
            )
    else:
        return build_validation_result(True, None, None)    
    #validate input of investment amount 
    # Validate that the user is investing over $5000
    if investment_amount is not None:
        if investment_amount <5000:
            return build_validation_result(
                False,
                "investment_amount",
                "You must invest at least $5000 to use this service, "
                "please provide an higher investment amount.",
            )
    #if the user age and investment amount are in the desired valid range
    # return a true validation result        
    else:
        return build_validation_result(True, None, None)

        ### YOUR DATA VALIDATION CODE ENDS HERE ###

### NEED A FUNCTION FOR INITIAL INVESTMENT RECOMMENDATIONS
### YOUR FINAL INVESTMENT RECOMMENDATION CODE STARTS HERE ###
def get_investment(riskLevel):
    if riskLevel=='None':
        investment="100 percent bonds (AGG), 0 percent equities (SPY)"
    elif riskLevel =='Very Low':
        investment="80 percent bonds (AGG), 20 percent equities (SPY)"
    elif riskLevel== 'Low': 
        investment= "60 percent bonds (AGG), 40 percent equities (SPY)"
    elif riskLevel=='Medium':
        investment="40 percent bonds (AGG), 60 percent equities (SPY)"
    elif riskLevel=='High':
        investment="20 percent bonds (AGG), 80 percent equities (SPY)"
    elif riskLevel=='Very High':
        investment="0 percent bonds (AGG), 100 percent equities (SPY)"
    return investment 
### YOUR FINAL INVESTMENT RECOMMENDATION CODE ENDS HERE ###


### Intents Handlers ###
def recommend_portfolio(intent_request):
    """
    Performs dialog management and fulfillment for recommending a portfolio.
    """

    first_name = get_slots(intent_request)["firstName"]
    age = get_slots(intent_request)["age"]
    investment_amount = get_slots(intent_request)["investmentAmount"]
    risk_level = get_slots(intent_request)["riskLevel"]
    source = intent_request["invocationSource"]

    if source == "DialogCodeHook":
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt
        # for the first violation detected.
        
        #make value for all slots intents
        slots=get_slots(intent_request)
        ### YOUR DATA VALIDATION CODE STARTS HERE ###
        # Validates user's input using the validate_userdata function above
        validation_result = validate_userdata(age, investment_amount, intent_request)
    
        # If the result of the data validation is false and the 
        # user input data is invalid
        # call the elicitSlot function to re-prompt for new input for invalid slots.
        if not validation_result["isValid"]:
            slots[validation_result["violatedSlot"]] = None  # Cleans invalid slot

            # Returns an elicitSlot dialog to request new data for the invalid slot
            return elicit_slot(
                intent_request["sessionAttributes"],
                intent_request["currentIntent"]["name"],
                slots,
                validation_result["violatedSlot"],
                validation_result["message"],
            )


        ### YOUR DATA VALIDATION CODE ENDS HERE ###

        # Fetch current session attibutes
        output_session_attributes = intent_request["sessionAttributes"]

        return delegate(output_session_attributes, get_slots(intent_request))

    # Get the initial investment recommendation
    ### YOUR FINAL INVESTMENT RECOMMENDATION CODE STARTS HERE ###
    initial_recommendation=get_investment(risk_level)
    ### YOUR FINAL INVESTMENT RECOMMENDATION CODE ENDS HERE ###

    # Return a message with the initial recommendation based on the risk level.
    return close(
        intent_request["sessionAttributes"],
        "Fulfilled",
        {
            "contentType": "PlainText",
            "content": """{} thank you for your information;
            based on the risk level you defined, my recommendation is to choose an investment portfolio with {}
            """.format(
                first_name, initial_recommendation
            ),
        },
    )


### Intents Dispatcher ###
def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    intent_name = intent_request["currentIntent"]["name"]

    # Dispatch to bot's intent handlers
    if intent_name == "RecommendPortfolio":
        return recommend_portfolio(intent_request)

    raise Exception("Intent with name " + intent_name + " not supported")


### Main Handler ###
def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """

    return dispatch(event)
