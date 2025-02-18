"""
assignment.py

This module implements custom JSON serialization and deserialization for two financial
domain objects: Stock and Trade. It provides two approaches for (de)serialization:
1. Using a custom JSONEncoder and a custom decoder (object_hook) to convert objects to and
   from JSON strings. This approach adds a special marker (“__type__”) to help reconstruct
   the original object.
2. Using Marshmallow schemas to define the structure of Stock and Trade objects and perform
   (de)serialization with validation.

Special non-native Python types such as date, datetime, and Decimal are converted to
string representations (ISO format for dates and datetimes, and plain strings for decimals)
to ensure JSON compatibility.
"""

from datetime import date, datetime
from decimal import Decimal
import json

# ----------------------------
# Domain Classes: Stock and Trade
# ----------------------------

class Stock:
    """
    Represents a stock quote with basic information.

    Attributes:
        symbol (str): The ticker symbol (e.g., "AAPL", "TSLA").
        date (date): The date for the stock quote.
        open (Decimal): The opening price.
        high (Decimal): The highest price of the day.
        low (Decimal): The lowest price of the day.
        close (Decimal): The closing price.
        volume (int): The number of shares traded.
    """

    def __init__(self, symbol, date, open_, high, low, close, volume):
        self.symbol = symbol
        self.date = date            # Expected to be a date object
        self.open = open_           # Decimal: opening price
        self.high = high            # Decimal: high price
        self.low = low              # Decimal: low price
        self.close = close          # Decimal: closing price
        self.volume = volume        # int: trading volume

    def to_dict(self):
        """
        Converts the Stock instance into a dictionary that can be serialized into JSON.
        A special key '__type__' is added to indicate that this dictionary represents a Stock.
        Date objects are converted to ISO format strings and Decimal values are cast to strings.
        """
        return {
            "__type__": "Stock",  # Marker to aid in deserialization
            "symbol": self.symbol,
            # Convert date to ISO format string if it is a date object
            "date": self.date.isoformat() if isinstance(self.date, date) else self.date,
            # Convert Decimal values to string representations
            "open": str(self.open),
            "high": str(self.high),
            "low": str(self.low),
            "close": str(self.close),
            "volume": self.volume
        }

    def __repr__(self):
        # Provides an unambiguous string representation of a Stock instance.
        return (f"Stock(symbol={self.symbol}, date={self.date}, open={self.open}, "
                f"high={self.high}, low={self.low}, close={self.close}, volume={self.volume})")


class Trade:
    """
    Represents a trade order.

    Attributes:
        symbol (str): The ticker symbol for which the trade was executed.
        timestamp (datetime): The date and time of the trade.
        order (str): The trade type (e.g., "buy" or "sell").
        price (Decimal): The price at which the trade was executed.
        volume (int): The number of shares traded.
        commission (Decimal): The commission charged for the trade.
    """

    def __init__(self, symbol, timestamp, order, price, volume, commission):
        self.symbol = symbol
        self.timestamp = timestamp  # Expected to be a datetime object
        self.order = order          # Trade order type (e.g., 'buy' or 'sell')
        self.price = price          # Decimal: trade price
        self.volume = volume        # int: trade volume
        self.commission = commission  # Decimal: commission fee

    def to_dict(self):
        """
        Converts the Trade instance into a dictionary suitable for JSON serialization.
        It also adds a '__type__' marker and converts the timestamp and Decimal fields.
        """
        return {
            "__type__": "Trade",  # Marker for the Trade type
            "symbol": self.symbol,
            # Convert datetime to ISO format string if it is a datetime object
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            "order": self.order,
            # Convert Decimal values to strings
            "price": str(self.price),
            "volume": self.volume,
            "commission": str(self.commission)
        }

    def __repr__(self):
        # Provides an unambiguous string representation of a Trade instance.
        return (f"Trade(symbol={self.symbol}, timestamp={self.timestamp}, order={self.order}, "
                f"price={self.price}, volume={self.volume}, commission={self.commission})")


# ----------------------------
# Custom JSON Encoder and Decoder
# ----------------------------

class CustomEncoder(json.JSONEncoder):
    """
    A custom JSON encoder that extends the default JSONEncoder to support custom objects.
    
    When an object of type Stock or Trade is encountered, its to_dict() method is called.
    Special types such as date, datetime, and Decimal are also converted to JSON-friendly formats.
    """
    def default(self, obj):
        # If obj is an instance of Stock, convert it to a dictionary representation.
        if isinstance(obj, Stock):
            return obj.to_dict()
        # If obj is an instance of Trade, convert it likewise.
        elif isinstance(obj, Trade):
            return obj.to_dict()
        # For date and datetime objects, return the ISO formatted string.
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        # For Decimal objects, return a string version.
        elif isinstance(obj, Decimal):
            return str(obj)
        # For all other objects, use the default encoding.
        return super().default(obj)


def custom_decoder(dct):
    """
    Custom decoder function used as the object_hook in json.loads().
    
    It checks for the special '__type__' key in the dictionary. If present, it uses the value to
    determine which object to reconstruct (Stock or Trade). It also converts the ISO formatted date or 
    datetime strings back to date/datetime objects, and converts numeric strings back to Decimal objects.
    If no type marker is present, the dictionary is returned unmodified.
    """
    if "__type__" in dct:
        if dct["__type__"] == "Stock":
            # Convert the ISO string back to a date object.
            dt = date.fromisoformat(dct["date"])
            return Stock(
                symbol=dct["symbol"],
                date=dt,
                open_=Decimal(dct["open"]),
                high=Decimal(dct["high"]),
                low=Decimal(dct["low"]),
                close=Decimal(dct["close"]),
                volume=dct["volume"]
            )
        elif dct["__type__"] == "Trade":
            # Convert the ISO string back to a datetime object.
            ts = datetime.fromisoformat(dct["timestamp"])
            return Trade(
                symbol=dct["symbol"],
                timestamp=ts,
                order=dct["order"],
                price=Decimal(dct["price"]),
                volume=dct["volume"],
                commission=Decimal(dct["commission"])
            )
    # If no type marker is found, return the dictionary as-is.
    return dct


# ----------------------------
# Marshmallow Schemas and Helper Functions
# ----------------------------

from marshmallow import Schema, fields, post_load

class StockSchema(Schema):
    """
    Marshmallow schema for serializing and deserializing Stock objects.
    
    This schema defines the expected structure and types for a Stock object. For decimal fields,
    the attribute 'as_string=True' ensures that they are represented as strings in the JSON output.
    """
    symbol = fields.Str(required=True)
    date = fields.Date(required=True)
    open = fields.Decimal(required=True, as_string=True)
    high = fields.Decimal(required=True, as_string=True)
    low = fields.Decimal(required=True, as_string=True)
    close = fields.Decimal(required=True, as_string=True)
    volume = fields.Integer(required=True)

    @post_load
    def make_stock(self, data, **kwargs):
        """
        Called after deserialization to create a Stock object from the validated data.
        Note that the constructor of Stock expects 'open_' for the opening price.
        """
        return Stock(
            symbol=data["symbol"],
            date=data["date"],
            open_=data["open"],
            high=data["high"],
            low=data["low"],
            close=data["close"],
            volume=data["volume"]
        )


class TradeSchema(Schema):
    """
    Marshmallow schema for serializing and deserializing Trade objects.
    
    This schema defines the structure for a Trade object, including conversion for datetime
    and decimal values.
    """
    symbol = fields.Str(required=True)
    timestamp = fields.DateTime(required=True)
    order = fields.Str(required=True)
    price = fields.Decimal(required=True, as_string=True)
    volume = fields.Integer(required=True)
    commission = fields.Decimal(required=True, as_string=True)

    @post_load
    def make_trade(self, data, **kwargs):
        """
        Called after deserialization to create a Trade object.
        """
        return Trade(**data)


def serialize_with_marshmallow(obj):
    """
    Serializes a Stock or Trade object into a JSON string using the appropriate Marshmallow schema.
    
    Args:
        obj: The object to serialize (either Stock or Trade).

    Returns:
        A JSON string representing the object.
    
    Raises:
        TypeError: If the object's type is not supported.
    """
    if isinstance(obj, Stock):
        return StockSchema().dumps(obj)
    elif isinstance(obj, Trade):
        return TradeSchema().dumps(obj)
    else:
        raise TypeError("Object of type %s is not supported" % type(obj))


def deserialize_with_marshmallow(json_str, schema):
    """
    Deserializes a JSON string into a Stock or Trade object using a given Marshmallow schema.

    Args:
        json_str (str): The JSON string to deserialize.
        schema (Schema): A Marshmallow schema instance (StockSchema or TradeSchema).

    Returns:
        An instance of Stock or Trade created from the JSON data.
    """
    return schema.loads(json_str)
