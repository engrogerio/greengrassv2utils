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



# https://github.com/aws/aws-iot-device-sdk-python-v2/blob/main/awsiot/greengrasscoreipc/client.py

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
        self.qos = QOS.AT_LEAST_ONCE
    
    def publish(self, topic:str , dict_message: dict):
        message = json.loads(str({}))
        try:
            message = json.dumps(dict_message)
        except TypeError as e:
            message_text = f"Failed to serialize the message {dict_message}."
            print(message_text)
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
            print(f'Exception while publishing to topic: {topic}. {e}', file=sys.stderr)
        return future

    def subscribe(self, topic: str, handler):
        pass

class Ipc(MessageQueue):
    def __init__(self):
        self.ipc_client = awsiot.greengrasscoreipc.connect()
        self.TIMEOUT = 10
        self.qos = QOS.AT_LEAST_ONCE
    
    
    def extract_message(self, message:dict) -> tuple:
        """
        Method must receive a dictionary as message and
        return the json version of the if.
        If the dictionary can not be serialized to a Json, it 
        looks for the dict key "image" with a byte sequence value
        and extract its value.

        Returns a tuple (type: str, value: str/bytes)
        """

        try:
            json_message = json.dumps(message)
            return ('json', message)

        except TypeError:
            # message is not serializable, so if an image was send, 
            # check if there a image key and extracts it from the dict:
            image = message.get('image', b'')
            if image:
                return ('bytes', image)
            else:
                message_text = f"Failed to serialize the message {message}."
                print(message_text)
                message = str({"error": message_text})
                return ('json', message)

    # https://aws.github.io/aws-iot-device-sdk-python-v2/awsiot/greengrasscoreipc.html
    def publish(self, topic: str, dict_message: dict):
        """
        Publish either a json message or a binary message to a specific topic.

        Returns the response of the operation.
        """
        message_type, message_value = self.extract_message(dict_message)
        print("@@@", message_type, message_value) 
        try:
            publish_message = PublishMessage()
            
            if message_type == 'json':
                publish_message.json_message = JsonMessage()
                publish_message.json_message.message = message_value
                print('@@json', message_value, '-', publish_message.__dict__)
            else: # message_type is binary
                publish_message.binary_message = BinaryMessage()
                publish_message.binary_message.message = message_value #bytes(message_value, "utf-8")
                print('@@binary', message_value)

            request = PublishToTopicRequest()
            request.topic = topic
            request.qos = self.qos
            request.publish_message = publish_message

            operation = self.ipc_client.new_publish_to_topic()
            operation.activate(request)
            future = operation.get_response()
            future.result(self.TIMEOUT)
        
        except concurrent.futures.TimeoutError as e:
            print(f'Timeout occurred while publishing to topic: {topic}', file=sys.stderr)

        except UnauthorizedError as e:
            print(f'Unauthorized error while publishing to topic: {topic}', file=sys.stderr)
        
        except Exception as e:
            print(f'Exception while publishing to topic: {topic}. {e}', file=sys.stderr)
            traceback.print_exc()

        return future

    def subscribe(self, topic, handler):
        """
        Start the stream and locks the main thread.
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
                print(f'Timeout occurred while subscribing to topic: {topic}. {e}')
            
            except UnauthorizedError as e:
                print(f'Unauthorized error while subscribing to topic: {topic}. {e}')

            except Exception as e:
                print(f'Exception while subscribing to topic: {topic}. {e}')
            
            except InterruptedError as e:
                print(f'Subscribe interrupted. {e}')
        
        except Exception as e:
            print('Exception occurred when using IPC.')
            traceback.print_exc()


