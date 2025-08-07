from zenml import step
from typing import Dict
import logging
from app.data_importing import export_BTS_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@step(name="data_import_step", enable_cache=False)
def data_import_step(uri, 
                     db_name, 
                     collection_name, 
                     feature) -> Dict:
    logger.info("☁️  Starting BTS data importing step...")
    bts_data = export_BTS_data(uri, db_name, collection_name, feature)
    logger.info("✅ Data import step completed.")

    return bts_data
