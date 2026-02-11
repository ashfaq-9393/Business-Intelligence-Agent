"""
Monday.com API Connector Module
Handles all API communication with monday.com boards
"""

import requests
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MondayConnector:
    """
    Connector for monday.com API
    Handles authentication, queries, and data retrieval
    """
    
    def __init__(self, api_key: str, api_url: str = "https://api.monday.com/v2"):
        """
        Initialize Monday.com connector
        
        Args:
            api_key: Monday.com API key
            api_url: Monday.com API base URL
        """
        self.api_key = api_key
        self.api_url = api_url
        self.headers = {
            "Authorization": api_key,
            "Content-Type": "application/json"
        }
    
    def query(self, query_str: str) -> Optional[Dict[str, Any]]:
        """
        Execute a GraphQL query against monday.com API
        
        Args:
            query_str: GraphQL query string
            
        Returns:
            Response data or None if error
        """
        try:
            payload = {"query": query_str}
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            if "errors" in data:
                logger.error(f"API Error: {data['errors']}")
                return None
            
            return data.get("data", {})
        
        except requests.exceptions.RequestException as e:
            logger.error(f"API Request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse API response: {e}")
            return None
    
    def get_board_items(self, board_id: str, limit: int = 500) -> List[Dict[str, Any]]:
        """
        Retrieve all items from a board
        
        Args:
            board_id: Monday board ID
            limit: Maximum items to retrieve
            
        Returns:
            List of items with all columns
        """
        query = f"""
        query {{
            boards(ids: "{board_id}") {{
                items(limit: {limit}) {{
                    id
                    name
                    created_at
                    updated_at
                    column_values {{
                        id
                        text
                        value
                    }}
                }}
            }}
        }}
        """
        
        result = self.query(query)
        if result and "boards" in result and result["boards"]:
            return result["boards"][0].get("items", [])
        
        return []
    
    def get_board_schema(self, board_id: str) -> Dict[str, Any]:
        """
        Retrieve board schema (column definitions)
        
        Args:
            board_id: Monday board ID
            
        Returns:
            Board schema with column definitions
        """
        query = f"""
        query {{
            boards(ids: "{board_id}") {{
                id
                name
                columns {{
                    id
                    title
                    type
                }}
            }}
        }}
        """
        
        result = self.query(query)
        if result and "boards" in result and result["boards"]:
            return result["boards"][0]
        
        return {}
    
    def get_next_items(self, board_id: str, cursor: Optional[str] = None, limit: int = 100) -> tuple:
        """
        Retrieve items with pagination support
        
        Args:
            board_id: Monday board ID
            cursor: Pagination cursor
            limit: Items per page
            
        Returns:
            Tuple of (items, next_cursor)
        """
        cursor_param = f', cursor: "{cursor}"' if cursor else ""
        
        query = f"""
        query {{
            boards(ids: "{board_id}") {{
                items_page(limit: {limit}{cursor_param}) {{
                    items {{
                        id
                        name
                        created_at
                        updated_at
                        column_values {{
                            id
                            text
                            value
                        }}
                    }}
                    cursor
                }}
            }}
        }}
        """
        
        result = self.query(query)
        if result and "boards" in result and result["boards"]:
            page_data = result["boards"][0].get("items_page", {})
            return page_data.get("items", []), page_data.get("cursor")
        
        return [], None
    
    def get_all_board_items(self, board_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all items from a board with automatic pagination
        
        Args:
            board_id: Monday board ID
            
        Returns:
            List of all items
        """
        all_items = []
        cursor = None
        
        while True:
            items, cursor = self.get_next_items(board_id, cursor, limit=100)
            all_items.extend(items)
            
            if not cursor:
                break
        
        logger.info(f"Retrieved {len(all_items)} items from board {board_id}")
        return all_items
