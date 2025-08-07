from zenml import step
import logging
from app.discharges_extraction import extract_all_discharges
from typing import Dict
from pathlib import Path
import json

logger = logging.getLogger(__name__)

@step(name="discharges extraction step", enable_cache=False)
def discharges_extraction_step(bts_data: Dict, 
                               output_dir: Path
                               ) -> Dict:

    """
    Step to extract discharges from BTS data and save them to a specified directory.
    """
    logger.info("📦 Starting discharges extraction step...")
    all_discharges = extract_all_discharges(bts_data=bts_data)

    # Save to JSON
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "all_discharges.json", "w") as f:
        json.dump(all_discharges, f, indent=2)

    logger.info("✅ Discharges extraction and storing step completed.")

    return all_discharges