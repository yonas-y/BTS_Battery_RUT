from zenml import pipeline
from steps.data_import_step import data_import_step
from steps.discharges_extraction_step import discharges_extraction_step
from app.config import OUTPUT_DIR
from app.config import MONGO_URI, DATABASE_NAME, COLLECTION_NAME, UNIQUE_ID
from typing import Tuple, Dict

@pipeline(name="data_pipeline")
def data_pipeline() -> Tuple[Dict, Dict]:
    """
    Pipeline to import data from MongoDB into the ZenML framework.
    """
    # Step to import data!
    bts_data = data_import_step(
        uri=MONGO_URI,
        db_name=DATABASE_NAME,
        collection_name=COLLECTION_NAME,
        feature=UNIQUE_ID
    )

    # Step to extract discharges from the given bts data!
    bts_discharges = discharges_extraction_step(
        bts_data=bts_data,
        output_dir=OUTPUT_DIR
    )

    return bts_data, bts_discharges