# Example CyberGRX API Integrations

This is a general purpose set of examples for the [CyberGRX API](https://api.cybergrx.com/v1/swagger/).  These examples are intented to give practical guidance for implementations with the CyberGRX API.  The CyberGRX API is self documenting with swagger, however these examples are not using auto-generated client stubs.

**Notes:**
- The CyberGRX API and Bulk API are versioned and will maintain backwards compatibility.
- You will need to pass a valid API token in the `Authorization` header to gain access to the CyberGRX API.
  - The [How To Guide](./HOW-TO.md) describes how to accomplish this.
- The CyberGRX API is self documenting using the formal API Swagger specification:
  - [CyberGRX API](https://api.cybergrx.com/v1/swagger/) allows data retrieval via standard pagination.
  - [CyberGRX Bulk API](https://api.cybergrx.com/bulk-v1/swagger/) allows bulk data retrieval with a single request.

# How To
If you are taking a look at integrating with the CyberGRX API, please take a look at the [How To Guide](./HOW-TO.md).

# Examples
Language specific examples are detailed below.

## Python Examples
Jump over to the [Python examples folder](./python_examples/README.md) and take a deeper look, some highlights:
- [SmartSheet integrated with CyberGRX](./python_examples/smart_sheet_sync/README.md)
- [Answer vendor inherent risk profile questions](./python_examples/answer_profile_questions/README.md)
- [Order assessments in bulk](./python_examples/order_assessments/README.md)
- [Bulk export to an Excel file](./python_examples/bulk_excel_export/README.md)
- [Bulk export to a XML file](./python_examples/bulk_xml_export/README.md)
