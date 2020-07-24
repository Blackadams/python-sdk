import grpc

class GenerateCallCredentials(grpc.AuthMetadataPlugin):
    def __init__(self, apiKey, authToken):
        self.apiKey = apiKey
        self.authToken = authToken

    def __call__(self, context, callback):
        if self.apiKey and self.authToken:
            metadata = (('api-key', self.apiKey), ('auth-token', self.authToken), )
        elif self.apiKey:
            metadata = (('api-key', self.apiKey), )
        elif self.authToken:
            metadata = (('auth-token', self.authToken), )
            
        callback(metadata, None)
    