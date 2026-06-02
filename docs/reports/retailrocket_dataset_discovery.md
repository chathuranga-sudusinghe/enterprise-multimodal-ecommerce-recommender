# RetailRocket Dataset Discovery

This report was generated with header-only reads, streaming line counts, and chunked aggregation (`chunksize=100_000`). No large raw CSV file was loaded fully into memory.

## Raw File Inventory

| File | Size MB | Records | Columns |
| --- | ---: | ---: | --- |
| events.csv | 89.87 | 2,756,101 | `timestamp`, `visitorid`, `event`, `itemid`, `transactionid` |
| item_properties_part1.csv | 461.88 | 10,999,999 | `timestamp`, `itemid`, `property`, `value` |
| item_properties_part2.csv | 389.99 | 9,275,903 | `timestamp`, `itemid`, `property`, `value` |
| category_tree.csv | 0.01 | 1,669 | `categoryid`, `parentid` |

## Events Overview

- Unique visitors: 1,407,580
- Unique items: 235,061
- Timestamp range: `1430622004384` to `1442545187788` (raw Unix milliseconds)
- Non-null transaction IDs: 22,457

### Event Distribution

- `view`: 2,664,312
- `addtocart`: 69,332
- `transaction`: 22,457

## Item Property Overview

### item_properties_part1.csv

- Unique items: 417,053
- Timestamp range: `1431226800000` to `1442113200000` (raw Unix milliseconds)
- Missing values by column: `timestamp`=0, `itemid`=0, `property`=0, `value`=0
- Top property values by frequency:
- `888`: 1,629,817
- `790`: 970,800
- `available`: 817,387
- `categoryid`: 426,305
- `6`: 343,207
- `283`: 323,681
- `776`: 311,654
- `678`: 261,829
- `364`: 256,340
- `202`: 242,984
- `839`: 226,921
- `159`: 226,502
- `917`: 226,437
- `764`: 226,242
- `112`: 226,102

### item_properties_part2.csv

- Unique items: 417,053
- Timestamp range: `1431226800000` to `1442113200000` (raw Unix milliseconds)
- Missing values by column: `timestamp`=0, `itemid`=0, `property`=0, `value`=0
- Top property values by frequency:
- `888`: 1,370,581
- `790`: 819,716
- `available`: 686,252
- `categoryid`: 361,909
- `6`: 288,264
- `283`: 273,738
- `776`: 262,566
- `364`: 220,146
- `678`: 220,137
- `202`: 205,954
- `112`: 190,951
- `764`: 190,811
- `917`: 190,790
- `159`: 190,551
- `839`: 190,318

## Category Tree Overview

- Records: 1,669
- Columns: `categoryid`, `parentid`
- Unique category IDs: 1,669
- Missing parent IDs: 25

## Baseline Signals Available

- Behavioral events: `view`, `addtocart`, and `transaction`.
- Item popularity can be measured from observed interaction frequency and recency.
- Visitor histories support later personalized behavior-based methods.
- Item properties and the category tree may support later metadata-aware analysis after canonical mapping decisions.
- Event weights remain provisional until the business task and evaluation protocol are defined.

## Limitations

- RetailRocket item and visitor identifiers are specific to this dataset track.
- The event schema does not contain the synthetic fixture fields `event_id`, `user_id`, or `product_id`.
- Item properties are stored as timestamped key-value rows and require deliberate canonicalization.
- This report does not define model weights, train models, or merge RetailRocket with any other dataset.
