import traceback
import json
import sys
import datetime
import concurrent.futures
import awsiot.greengrasscoreipc
from awsiot.greengrasscoreipc.model import (
    QOS,
    PublishToTopicRequest,
    SubscribeToTopicRequest,
    PublishToIoTCoreRequest,
    PublishMessage,
    JsonMessage,
    BinaryMessage,
    UnauthorizedError
    )
from abc import ABC, abstractmethod


# Source code for awsiot lib
# https://github.com/aws/aws-iot-device-sdk-python-v2/blob/main/awsiot/greengrasscoreipc/client.py
# https://github.com/aws/aws-iot-device-sdk-python-v2/blob/f3a0021409161a0adda3b208830abdcfa16d0302/awsiot/eventstreamrpc.py

class MessageQueue(ABC):
    """
    A message queue must have a publish and a subscribe method.
    """

    @abstractmethod
    def publish(self, topic: str, dict_message: dict):
        pass

    @abstractmethod
    def subscribe(self, topic: str, handler):
        pass
    
class Mqtt(MessageQueue):
    def __init__(self):
        self.ipc_client = awsiot.greengrasscoreipc.connect()
        self.TIMEOUT = 10
        self.qos = QOS.AT_MOST_ONCE
    
    def publish(self, topic:str , dict_message: dict):
        message = ''
        try:
            message = json.dumps(dict_message)
            # message = str(dict_message)
        except TypeError as e:
            message_text = f"Failed to serialize the message on Mqtt publish: {dict_message}."
            print(message_text, file=sys.stderr)
            message = {"error": message_text}
        try:
            request = PublishToIoTCoreRequest()
            request.topic_name = topic
            request.qos = self.qos
            request.payload = bytes(message, "utf-8")
            print('=>', request.payload)
            operation = self.ipc_client.new_publish_to_iot_core()
            operation.activate(request)
            future = operation.get_response()
            future.result(self.TIMEOUT)
        except Exception as e:
            print(f'Exception while publishing to Mqtt topic: {topic}. {e}', file=sys.stderr)

    def subscribe(self, topic: str, handler):
        pass

class Ipc(MessageQueue):
    def __init__(self):
        self.ipc_client = awsiot.greengrasscoreipc.connect()
        self.TIMEOUT = 10
        self.qos = QOS.AT_MOST_ONCE
    
    
    def extract_message(self, message:dict) -> tuple:
        """
        Method must receive a dictionary as message and
        return a tuple with message type and message content
        If the dictionary can not be serialized to a Json, it 
        looks for the dict key "image" with a byte sequence value
        and extract its value.

        Returns a tuple (type: str, value: str/bytes)
        """

        try:
            json_message = json.dumps(message)
            return ('json', json_message)

        except TypeError:
            # if message is not serializable, check if there a image key 
            # and extracts it from the dict. If no image, return an error message
            image = message.get('image', b'')
            if image:
                return ('bytes', image)
            else:
                message_text = f"Failed to serialize the message {message}."
                print(message_text, file=sys.stderr)
                message = str({"error": message_text})
                return ('json', message)

    # https://aws.github.io/aws-iot-device-sdk-python-v2/awsiot/greengrasscoreipc.html
    def publish(self, topic: str, dict_message: dict):
        """
        Publish either a json message or a binary message to a specific topic.

        Returns the response of the operation.
        """
        message_type, message_value = self.extract_message(dict_message)
        try:
            publish_message = PublishMessage()
            
            if message_type == 'json':
                publish_message.json_message = JsonMessage()
                publish_message.json_message.message = message_value
                print('@@json', message_value, '-', publish_message.__dict__)
            else: # message_type is binary
                publish_message.binary_message = BinaryMessage()
                publish_message.binary_message.message = message_value
                print('@@binary', message_value[:10], '-', publish_message.__dict__)

            request = PublishToTopicRequest()
            request.topic = topic
            request.qos = self.qos
            request.publish_message = publish_message

            operation = self.ipc_client.new_publish_to_topic()
            operation.activate(request)
            future = operation.get_response()
            future.result(self.TIMEOUT)
        
        except concurrent.futures.TimeoutError as e:
            print(f'Timeout occurred while publishing to Ipc topic: {topic}', file=sys.stderr)

        except UnauthorizedError as e:
            print(f'Unauthorized error while publishing to Ipc topic: {topic}', file=sys.stderr)
        
        except Exception as e:
            print(f'Exception while publishing to Ipc topic: {topic}. {e}', file=sys.stderr)
            traceback.print_exc()

        return future

    def subscribe(self, topic, handler):
        """
        Start the stream.Caller must loop the main thread.
        """
        try:
            request = SubscribeToTopicRequest()
            request.topic = topic
            operation = self.ipc_client.new_subscribe_to_topic(handler)
            future = operation.activate(request)
            try:
                future.result(self.TIMEOUT)
                print(f'Successfully subscribed to topic: {topic}.')
            
            except concurrent.futures.TimeoutError as e:
                print(f'Timeout occurred while subscribing to ipc topic: {topic}. {e}', file=sys.stderr)
            
            except UnauthorizedError as e:
                print(f'Unauthorized error while subscribing to ipc topic: {topic}. {e}', file=sys.stderr)

            except Exception as e:
                print(f'Exception while subscribing to ipc topic: {topic}. {e}', file=sys.stderr)
            
            except InterruptedError as e:
                print(f'Subscribe top ipc interrupted. {e}', file=sys.stderr)
        
        except Exception as e:
            print(f'Exception occurred when subscribing ipc topic {topic}: {e}', file=sys.stderr)
            traceback.print_exc()