# Example CyberGRX API Integrations

This is a general purpose set of examples for the [CyberGRX API](https://api.cybergrx.com/v1/swagger/).  These examples are intented to give practical guidance for implementations with the CyberGRX API.  The CyberGRX API is self documenting with swagger, however these examples are not using auto-generated client stubs.

**Notes:**
- You will need to pass a valid API token in the `Authorization` header to gain access to the CyberGRX API.  The [How To Guide](./HOW-TO.md) describes how to accomplish this.
- The CyberGRX API is self documenting using the formal API Swagger specification:
  - [CyberGRX API](https://api.cybergrx.com/v1/swagger/)
  - [CyberGRX Bulk API](https://api.cybergrx.com/bulk-v1/swagger/)

# How To
If you are taking a look at integrating with the CyberGRX API, please take a look at the [How To Guide](./HOW-TO.md).

# Examples
TODO:
- Pull an entire ecosystem with a single API request.
- Retrieve all information for each third party, this includes:
  - For authorized reports the latest authorized residual_risk (gaps/findings).
  - For authorized reports, the latest control scores.
- The CyberGRX API is versioned and will maintain backwards compatibility

