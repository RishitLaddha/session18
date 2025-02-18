# JSON Serialization and Deserialization for Stock and Trade Objects

This project demonstrates how to perform custom JSON serialization and deserialization for two specific domain classes: a **Stock** and a **Trade**. In addition to using a custom JSON encoder/decoder pair, we also implement a solution with the Marshmallow library to perform schema‐based (de)serialization. The aim is to convert complex Python objects (which include non‐native types such as `date`, `datetime`, and `Decimal`) into JSON strings and then be able to reconstruct the original objects from those strings.

## Overview

The solution is divided into several parts. First, two classes—**Stock** and **Trade**—are defined to represent stock market data and trade activity respectively. These classes encapsulate attributes like the symbol, date, open/high/low/close prices, trade timestamps, order types, and commissions. The numerical values for prices and commissions are handled by the `Decimal` class to ensure precision.

Each class includes a method to transform its instance data into a Python dictionary. This is crucial because JSON supports only a limited set of data types. To distinguish between different object types during deserialization, the dictionary representation includes a marker key (named `__type__`). This key explicitly identifies whether the data represents a Stock or a Trade.

The custom JSON encoder subclass (inherited from Python’s standard JSONEncoder) is responsible for detecting instances of these classes and converting them to their dictionary representations. It also handles special cases for dates, datetimes, and decimals by converting them into a format that can be represented in JSON (typically ISO formatted strings or plain strings for decimals). On the other side, a custom decoder function examines the dictionary; if it finds the marker key, it reconstructs an object of the correct type by converting the date/time strings back to date or datetime objects and the numeric strings back to Decimal values.

In parallel, the solution uses the Marshmallow library to perform the same task but using a schema‐based approach. Two Marshmallow schemas are defined—one for Stock and one for Trade. Each schema specifies the expected data types for each attribute and includes a post-load hook to reconstitute an object from the deserialized data. Helper functions are provided to serialize and deserialize objects using these schemas.

## Detailed Explanation

### Stock and Trade Classes

The two main domain classes are **Stock** and **Trade**. The Stock class contains details such as the symbol (a ticker string), the date (a Python date object), and the financial figures (open, high, low, and close) represented using the Decimal class for precision. The volume is stored as an integer. In the Trade class, similar data are captured along with a timestamp (a datetime object), the order type (for example, 'buy' or 'sell'), the price, the trade volume, and the commission.  

Each class includes a method that converts its attributes to a dictionary. This method, typically named `to_dict`, is critical because JSON can only directly represent basic types like strings, numbers, booleans, lists, and dictionaries. By converting complex objects into dictionaries, we can ensure that all data can be converted into JSON. Moreover, these methods insert an extra field called `__type__` into the resulting dictionary, which explicitly indicates the type of the object (either `"Stock"` or `"Trade"`). This marker is essential for the decoding process, as it lets the decoder know which class’s constructor should be used when reconstructing the object.

For example, in the Stock class, the date attribute is transformed using the `isoformat()` method to convert it into a standardized string format. Decimal attributes are converted to strings so that they can be safely represented in JSON. The Trade class follows a similar approach with its timestamp attribute.

### Custom JSON Encoder

The custom JSON encoder inherits from Python’s built-in JSONEncoder. In the overridden `default()` method, the encoder first checks whether the object is an instance of Stock or Trade. If it is, the method calls the object’s `to_dict()` method to get a serializable dictionary representation. In addition, the encoder handles other special types: if the object is a date or datetime, it converts it into an ISO formatted string; if it is a Decimal, it converts it to a string. These conversions ensure that every piece of data in a Stock or Trade object becomes a JSON-compatible type. If none of these conditions are met, the encoder falls back to the superclass’s default behavior.

This design means that whenever you call `json.dumps()` with your custom encoder, any Stock or Trade objects (or any nested structure containing them) will automatically be converted into a dictionary with the proper type markers and string representations of special objects.

### Custom JSON Decoder

On the deserialization side, the custom decoder function is meant to be used as an `object_hook` in `json.loads()`. When JSON is loaded into a Python dictionary, this function is called for every dictionary. The decoder looks for the special key `__type__`. If the key exists and indicates that the dictionary represents a Stock object, the decoder reconstructs the Stock instance by parsing the ISO date string back into a date object and converting the string representations of the financial values back into Decimal objects. Similarly, if the type marker indicates a Trade, the timestamp is converted back into a datetime object and the corresponding strings are converted back into Decimals. If no type marker is found, the dictionary is returned as is.

This approach guarantees that after deserialization the objects are not simply plain dictionaries; instead, they are full-fledged Stock or Trade objects that can be used in the rest of your application.

### Marshmallow Schemas

Marshmallow is a powerful library used to validate and (de)serialize complex data types. In our solution, two Marshmallow schemas—one for Stock and one for Trade—are created. Each schema defines the expected fields and their types. For instance, the Stock schema expects a string for the symbol, a date for the date, and decimals (rendered as strings) for the open, high, low, and close values. It also expects an integer for the volume.

Each schema uses a post-load decorator to specify how to create an instance of the corresponding class once the data has been deserialized. In the Stock schema, after the JSON string is parsed into basic Python types, the post-load method creates a Stock object using the data. The Trade schema functions similarly for Trade objects.

Helper functions are provided to simplify serialization and deserialization with Marshmallow. The serialization function checks the type of the object and uses the correct schema to dump the object into a JSON string. The deserialization function accepts a JSON string and a schema object and returns an instance of the domain class. This method is particularly useful because Marshmallow also validates the data according to the schema definitions, ensuring that your objects have the proper types and required fields.

### Expected Outcomes and Testing

The overall goal of the implementation is to support two different approaches for serializing complex financial data into JSON and then restoring it to its original form. With the custom encoder/decoder, you have full control over the JSON representation and the reconstruction process. With Marshmallow, you get schema validation and the convenience of automatic data conversion based on defined fields.

In testing, you would typically check that:
- A Stock object is converted to JSON containing the correct symbol, date in ISO format, and string representations of decimal values.
- A Trade object is similarly serialized, including the timestamp in ISO format.
- A nested dictionary that contains a list of Stock and Trade objects serializes to a JSON string that can be deserialized back into the original object structure.
- The custom decoder correctly identifies the type markers and reconstructs the original objects.
- Marshmallow-based serialization and deserialization work as expected and validate the incoming data.

Each test case would verify that after serialization and deserialization, the types and values of the Stock and Trade objects remain correct, including their special types such as date, datetime, and Decimal.

### Conclusion

This project demonstrates two powerful techniques for serializing complex Python objects. The custom JSON encoder/decoder approach provides a straightforward method by converting objects to dictionaries with explicit type markers and then restoring them using a corresponding decoding function. In parallel, the Marshmallow approach leverages schema definitions to both validate and transform the data, providing a more declarative and robust solution. Both approaches address the challenge of converting non-standard data types (like dates and decimals) into JSON-friendly formats while ensuring that the original object structures can be recovered exactly. By following this design, the project meets the requirements for robust serialization and deserialization, and it passes all the provided test cases.

