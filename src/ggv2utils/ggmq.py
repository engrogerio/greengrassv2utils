import traceback
import json
import sys
import concurrent.futures
import awsiot.greengrasscoreipc
from awsiot.greengrasscoreipc.model import (
    QOS,
    PublishToTopicRequest,
    SubscribeToTopicRequest,
    PublishToIoTCoreRequest,
    GetConfigurationRequest,
    PublishMessage,
    JsonMessage,
    BinaryMessage,
    UnauthorizedError
    )
from abc import ABC, abstractmethod


# https://github.com/aws/aws-iot-device-sdk-python-v2/blob/main/awsiot/greengrasscoreipc/client.py

class MessageQueue(ABC):
    
    def __init__(self):
        self.ipc_client = awsiot.greengrasscoreipc.connect()
        self.TIMEOUT = 10
        self.qos = QOS.AT_LEAST_ONCE
    
    @abstractmethod
    def publish(self):
        pass

    @abstractmethod
    def subscribe(self):
        pass
    
class Mqtt(MessageQueue):
            
    def publish(self, topic:str , dict_message: dict):
        message = json.loads(str({}))
        try:
            message = json.dumps(dict_message)
        except Exception as e:
            print(f"Failed to serialize the message {dict_message}.")
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

    def subscribe(self, topic, handler):
        pass

class Ipc(MessageQueue):
       
    def get_config(self):
        """
        https://docs.aws.amazon.com/greengrass/v2/developerguide/ipc-component-configuration.html#ipc-operation-getconfiguration
        Get the component configuration from component recipe
        """
        try:
            request = GetConfigurationRequest()
            operation = self.ipc_client.new_get_configuration()
            operation.activate(request).result(self.TIMEOUT)
            result = operation.get_response().result(self.TIMEOUT)
            return result.value
        except Exception as e:
            print("Exception occured during fetching the configuration: {}".format(e))
            return None
            
    def extract_message(self, message:dict):
        """
        Method must receive a dictionary as message and
        return the json version of the if.
        If the dictionary can not be serialized to a Json, it 
        looks for the dict key "image" with a byte sequence value
        and extract its value.

        Returns a tuple (return type, value)
        """
        try:
            json_message = json.dumps(message)
            return ('json', json_message)
        except TypeError:
            # message is not serializable, so if an image was send, 
            # the image is extracted from the dict:
            image = message.get('image', b'')
            return ('bytes', image)


    # https://aws.github.io/aws-iot-device-sdk-python-v2/awsiot/greengrasscoreipc.html
    def publish(self, topic: str, dic_message):
        """
        Publish either a json message or a binary message to a specific topic.

        Returns the response of the operation.
        """
        message_type, message_value = self.extract_message(dic_message)
        
        try:
            #json_message = message # json.dumps(message)
            publish_message = PublishMessage()
            
            if message_type == 'json':
                publish_message.json_message = JsonMessage()
                publish_message.json_message.message = message_value
            else: # message_type is binary
                publish_message.binary_message = BinaryMessage()
                publish_message.binary_message.message = message_value #bytes(message_value, "utf-8")

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
            raise e
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
                print('Successfully subscribed to topic: ' + topic)
            
            except concurrent.futures.TimeoutError as e:
                print('Timeout occurred while subscribing to topic: ' + topic)
                # raise e
            
            except UnauthorizedError as e:
                print('Unauthorized error while subscribing to topic: ' + topic)
                raise e
            
            except Exception as e:
                print('Exception while subscribing to topic: ' + topic)
                raise e
            
            except InterruptedError:
                print('Subscribe interrupted.')
        
        except Exception as e:
            print('Exception occurred when using IPC.')
            traceback.print_exc()
