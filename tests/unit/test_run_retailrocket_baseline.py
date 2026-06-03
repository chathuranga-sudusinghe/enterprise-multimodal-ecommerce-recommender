import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from scripts.run_retailrocket_baseline import run_baseline


def test_run_baseline_aggregates_chunks_and_writes_ranked_output(tmp_path: Path) -> None:
    events_path = tmp_path / "events.csv"
    output_path = tmp_path / "processed" / "top_items.csv"
    pd.DataFrame(
        {
            "timestamp": [1, 2, 3, 4, 5],
            "visitorid": [101, 102, 103, 104, 105],
            "event": ["view", "transaction", "addtocart", "view", "view"],
            "itemid": [5001, 5002, 5001, 5004, 5003],
            "transactionid": [None, 90001, None, None, None],
        }
    ).to_csv(events_path, index=False)

    # chunk_size=2 forces item 5001 aggregation to span separate chunks.
    top_items = run_baseline(events_path, output_path, chunk_size=2, top_k=4)

    expected = pd.DataFrame(
        {
            "itemid": [5002, 5001, 5003, 5004],
            "popularity_score": [5.0, 4.0, 1.0, 1.0],
        }
    )
    pd.testing.assert_frame_equal(top_items, expected)
    pd.testing.assert_frame_equal(pd.read_csv(output_path), expected)
    assert output_path.is_file()
