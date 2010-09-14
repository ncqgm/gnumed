from pyjamas.JSONService import JSONProxy

import jsonobjproxy # just to get it in for pyjs compiler

#======================================================
class EchoServicePython(JSONProxy):
    def __init__(self):
        JSONProxy.__init__(self, "/JSON",
                ["login",
                "logout", "get_doc_types",
                "get_schema_version",
                "get_documents",
                "get_provider_inbox_data",
                "get_patient_messages",
                "doSomething",
                "search_patient"])

#======================================================

svc = EchoServicePython()

