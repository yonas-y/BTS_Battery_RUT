from zenml import pipeline
from typing import Dict
from steps.data_import_step import data_import_step
from app.config import MONGO_URI, DATABASE_NAME, COLLECTION_NAME, UNIQUE_ID

@pipeline(name="data_pipeline")
def data_pipeline() -> Dict:
    """
    Pipeline to import data from MongoDB into the ZenML framework.
    """
    # Step to import data
    bts_data = data_import_step(
        uri=MONGO_URI,
        db_name=DATABASE_NAME,
        collection_name=COLLECTION_NAME,
        feature=UNIQUE_ID
    )
    return bts_data