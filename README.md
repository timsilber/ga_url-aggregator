# Google Analytics article aggregator (GAAA)

*Google Analytics article aggregator (GAAA)* takes in a raw Google Analytics CSV file and a sorting metric from user input. Based on the user-defined sort metric, two CSVs are exported: top articles and top integrations. The top five articles and integrations are printed to the terminal.

GAAA solves two problems we were facing:

1. Two URLs for the same content

Our CMS can serve two URLs for the same article, following the format `/docs/{article}` or `/g2/docs/{article}`. GAAA aggregates the user-defined sort metric across the two URLs and outputs the sorted, aggregated articles to a CSV file in the Downloads folder.

2. Missing parent-child relationships

Our CMS serves all articles off of the root directory (`/docs/{article}`), rather than using directories as path parameters (`/docs/{category}/{article}`). As a result, there is no easy way to total traffic per category, such as the total documentation traffic to a specific integration. Additionally, some categories have several levels of nesting, making a recursive solution preferred.

GAAA calls our CMS's category API, then recursively parses the response JSON to determine the relationships between articles in parent categories and child categories. These relationships are then mapped onto the aggregated article data, then recursively totaled to get integration-level data. The sorted, aggregated integration data is exported to a CSV in the Downloads folder.