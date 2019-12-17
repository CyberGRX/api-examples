# Bulk API Integrations
Some sample integrations with the [CyberGRX Bulk API](https://api.cybergrx.com/bulk-v1/swagger/).  These integrations by default use the production API, if you are developing locally you can the environmental parameter `CYBERGRX_BULK_API=https://hostname-of-bulk-connector` to target a custom endpoint.

These bulk examples pull an entire ecosystem with a single API request.  This endpoint will retrieve all information for each third party.  For third parties with authorized reports, this includes the latest authorized residual_risk (gaps/findings) as well as the latest control scores.

## Integrations
- [Bulk export to an Excel file](./bulk_excel_export/README.md)
- [Bulk export to a XML file](./bulk_xml_export/README.md)
