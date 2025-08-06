import pymongo
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def export_BTS_data(
        uri, 
        db_name, 
        collection_name, 
        feature) -> dict:
    """
    Finds unique IDs from a feature in MongoDB documents and exports them as separate DataFrames.

    Args:
        uri (str): MongoDB connection URI.
        db_name (str): Database name.
        collection_name (str): Collection to query.
        feature (str): Field name to find unique values.

    Returns:
        dict: {unique_id: DataFrame of documents with that feature value}
    """
    client = pymongo.MongoClient(uri)
    db = client[db_name]
    collection = db[collection_name]

    unique_ids = collection.distinct(feature)
    result = {}
    for uid in unique_ids:
        docs = list(collection.find({feature: uid}))
        df = pd.DataFrame(docs)
        df = df.drop(columns=['_id'], errors='ignore')
        result[uid] = df

    client.close()
    if not result:
        raise ValueError("No documents found for the specified feature.")
    
    logger.info(f"Exported {len(result)} unique IDs from MongoDB.")
    logger.debug(f"Unique IDs: {list(result.keys())}")

    return result
