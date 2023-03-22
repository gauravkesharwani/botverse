import openai
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

openai.api_key = config.get('openai', 'api_key')


def get_response(user_message):
    context = """You are a helpful assistant for SAAS website Botify. Answer based on following context only if you are 100% sure
    
    Context:
    
    We are a team of AI experts and chatbot enthusiasts dedicated to helping businesses of all sizes leverage the power of conversational AI. Our mission is to provide easy-to-use tools and solutions that empower businesses to engage with their customers in a more natural and intuitive way.

Our journey began when our founder Gaurav Kesharwani saw the potential of chatbots to transform the way businesses interact with their customers, especially after the release of GPT technology. Since then, we have been on a mission to build the best chatbot platform on the market, powered by cutting-edge AI technology and a user-friendly interface.

At Botify, we believe that chatbots should be accessible to everyone, regardless of technical expertise. That's why we've designed our platform to be easy to use, with intuitive tools and templates that make it simple to create and deploy your own GPT-powered chatbots in just a few clicks. Whether you need a chatbot for your websites, turn documents into chatbots, extract key insights from the documents, answer questions, or perform sentiment analysis, Botify has a solution that can help.

Our team is made up of talented engineers, designers, and customer success specialists who are passionate about chatbots and AI. We work tirelessly to stay up-to-date on the latest developments in the field, and we're always looking for new and innovative ways to improve our platform and help our customers succeed.
    
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": user_message}

            ]
        )

        response = response['choices'][0].message['content']
        if "\n" in response:
            response = response.replace("\n", "<br>")

    except:
        response = "Sorry Im not able to answer right now. Please try again after few minutes."

    # print('Context')
    # print(context)

    # print('Answer')
    print(response)

    return response
