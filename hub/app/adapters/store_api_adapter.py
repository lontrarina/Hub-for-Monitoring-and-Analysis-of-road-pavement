import json
import logging
from typing import List

import requests

from app.entities.processed_agent_data import ProcessedAgentData
from app.interfaces.store_gateway import StoreGateway


class StoreApiAdapter(StoreGateway):
    def __init__(self, api_base_url):
        self.api_base_url = api_base_url

    def save_data(self, processed_agent_data_batch: List[ProcessedAgentData]) -> bool:
        """
        Save the processed road data to the Store API.
        Parameters:
            processed_agent_data_batch (dict): Processed road data to be saved.
        Returns:
            bool: True if the data is successfully saved, False otherwise.
        """

        try:
            # Serialize datetime object to ISO format for all items in the batch
            serialized_data = [
                {
                    "road_state": item.road_state,
                    "agent_data": {
                        "user_id": item.agent_data.user_id,
                        "accelerometer": {
                            "x": item.agent_data.accelerometer.x,
                            "y": item.agent_data.accelerometer.y,
                            "z": item.agent_data.accelerometer.z
                        },
                        "gps": {
                            "latitude": item.agent_data.gps.latitude,
                            "longitude": item.agent_data.gps.longitude
                        },
                        "timestamp": item.agent_data.timestamp.isoformat()
                    }
                }
                for item in processed_agent_data_batch
            ]

            # Send all serialized data to the Store API in one request
            responses = [requests.post(f"{self.api_base_url}/processed_agent_data/", json=data) for data in
                         serialized_data]

            # Check if all requests were successful
            if all(response.status_code == 200 for response in responses):
                return True
            else:
                # Log errors for failed requests
                for response, item in zip(responses, processed_agent_data_batch):
                    if response.status_code != 200:
                        logging.error( f"Error while saving data to Store API: {response.text}. Data: {item.model_dump()}")
                return False
        except requests.RequestException as e:
            logging.error(f"Error while saving data to Store API: {e}")
            return False



