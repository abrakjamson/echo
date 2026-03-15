import xml.etree.ElementTree as ET


class SoapHandler:
    """Handles SOAP protocol echo requests."""

    @staticmethod
    def handle_request(req_body: str) -> str:
        """
        Parse and handle a SOAP request, echoing back the content.
        
        Args:
            req_body: string containing the SOAP XML request body
            
        Returns:
            str: SOAP XML response object
        """
        # SOAP 1.1 Envelope namespace
        SOAP_ENV_NS = "http://schemas.xmlsoap.org/soap/envelope/"
        
        # Register namespaces for cleaner output
        ET.register_namespace('soapenv', SOAP_ENV_NS)
        
        try:
            # Parse the incoming XML
            root = ET.fromstring(req_body)
            
            # Find the Body element
            ns = {'soapenv': SOAP_ENV_NS}
            # Try to find Body directly or within Envelope
            body = root.find('.//soapenv:Body', ns)
            
            if body is None:
                # Fallback check if root itself is Body (though unlikely for valid SOAP)
                if root.tag == f"{{{SOAP_ENV_NS}}}Body":
                    body = root
                else:
                    return SoapHandler._fault_response("Client", "No Body element found in SOAP Envelope")
            
            # Extract the first child of the Body (the request operation)
            if len(body) == 0:
                return SoapHandler._fault_response("Client", "Empty SOAP Body")
            
            request_op = body[0]
            op_tag = request_op.tag
            
            # Determine response tag name (e.g., EchoRequest -> EchoResponse)
            if '}' in op_tag:
                ns_part, local_part = op_tag.split('}', 1)
                if local_part.endswith('Request'):
                    res_local = local_part[:-7] + 'Response'
                else:
                    res_local = local_part + 'Response'
                response_tag = f"{ns_part}}}{res_local}"
            else:
                if op_tag.endswith('Request'):
                    response_tag = op_tag[:-7] + 'Response'
                else:
                    response_tag = op_tag + 'Response'
                
            # Create response envelope
            resp_root = ET.Element(f"{{{SOAP_ENV_NS}}}Envelope")
            ET.SubElement(resp_root, f"{{{SOAP_ENV_NS}}}Header")
            resp_body = ET.SubElement(resp_root, f"{{{SOAP_ENV_NS}}}Body")
            
            # Create response operation
            resp_op = ET.SubElement(resp_body, response_tag)
            
            # Copy children (echo)
            for child in request_op:
                resp_op.append(child)
            
            # If no children, copy text if any
            if len(request_op) == 0:
                resp_op.text = request_op.text
                
            return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(resp_root, encoding='unicode', method='xml')
            
        except ET.ParseError as e:
            return SoapHandler._fault_response("Client", f"XML Parse Error: {str(e)}")
        except Exception as e:
            return SoapHandler._fault_response("Server", f"Internal Error: {str(e)}")

    @staticmethod
    def _fault_response(fault_code, fault_string):
        """Generate a SOAP 1.1 Fault response."""
        SOAP_ENV_NS = "http://schemas.xmlsoap.org/soap/envelope/"
        ET.register_namespace('soapenv', SOAP_ENV_NS)
        
        root = ET.Element(f"{{{SOAP_ENV_NS}}}Envelope")
        body = ET.SubElement(root, f"{{{SOAP_ENV_NS}}}Body")
        fault = ET.SubElement(body, f"{{{SOAP_ENV_NS}}}Fault")
        
        code = ET.SubElement(fault, "faultcode")
        code.text = f"soapenv:{fault_code}"
        
        string = ET.SubElement(fault, "faultstring")
        string.text = fault_string
        
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding='unicode', method='xml')
