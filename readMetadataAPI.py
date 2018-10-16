import requests
import six
import hashlib
import hmac
import time
import base64



### Details for WorldCat APIs
client_id = 'replace with yours'
client_secret = 'replace with yours'
grant_type="client_credentials"
authenticatingInstitutionId='replace with yours'
contextInstitutionId='replace with yours'
scope="WorldCatMetadataAPI"
authorization_base_url = 'https://authn.sd00.worldcat.org/oauth2/accessToken'
principalID = 'replace with yours'
principalIDNS = 'replace with yours'


def getAccessToken():

    '''
    gets an access token for the WorldCat Metadata API
    '''
    
    q='"'
    qc='"'

    urlParameters = ("grant_type="+ grant_type +
            "&authenticatingInstitutionId=" + authenticatingInstitutionId +
            "&contextInstitutionId=" + contextInstitutionId +
            "&scope=" + scope)

    parameters = {}
    for param in urlParameters.split('&'):
        key = (param.split('='))[0]
        value = (param.split('='))[1]
        parameters[key] = value

    authRequestURL = (authorization_base_url + "?" + urlParameters)

    currentTime = str(int(time.time()))
    nonceTime = str(int(time.time()- 1))
    stringToHash = (client_id + "\n" +
                    currentTime + "\n" +
                    nonceTime + "\n" +
                    "" + "\n" +
                    "POST" + "\n" +
                    "www.oclc.org" "\n" +
                    "443" + "\n" +
                    "/wskey" + "\n")

    """URL encode normalized request per OAuth 2 Official Specification."""
    #This part taken from oclc-python-auth library
    
    for key in sorted(parameters):
        nameAndValue = six.moves.urllib.parse.urlencode({key: parameters[key]})
        nameAndValue = nameAndValue.replace('+', '%20')
        nameAndValue = nameAndValue.replace('*', '%2A')
        nameAndValue = nameAndValue.replace('%7E', '~')
        stringToHash += nameAndValue + '\n'

    digest = hmac.new(client_secret.encode('utf-8'),
                  msg = stringToHash.encode('utf-8'),
                  digestmod=hashlib.sha256).digest()

    signature = str(base64.b64encode(digest).decode())

    ###

    authorization = ("http://www.worldcat.org/wskey/v2/hmac/v1" + " " +
               'clientId=' + q + client_id + qc + "," +
               'timestamp='+ q + currentTime + qc + "," +
               'nonce=' + q + nonceTime + qc + "," +
               'signature=' + q + signature + qc + "," +
               'principalID=' + q + principalID + qc + "," +
               'principalIDNS=' + q + principalIDNS + qc)

    headers = {'Authorization': authorization}
    r = requests.post(authRequestURL, headers=headers)
    response = r.json()
    accessToken = response['access_token']

    return accessToken

def readFromMetadataAPI(oclcNumber):

    '''
    given an oclc number, gets the record from WorldCat Metadata API. Requires a generated client credential token.
    '''
    
    global authorizationToken #needed to update global token variable if token expires while script is running

    #makes request to metadata API
    recordURL= "https://worldcat.org/bib/data/" + str(oclcNumber)
    headers = {
            'Authorization': "Bearer " + authorizationToken,
            'accept':'application/atom+json;content="application/atom+json"'
    }

    r= requests.get(recordURL, headers=headers)
    
    #a 401 response indicates that the access token has expired. This checks, requests a new one if needed, and makes a new request.
    if r.status_code == 401:
       
        authorizationToken = getAccessToken()
        print("had to get new token")
        headers = {
            'Authorization': "Bearer " + authorizationToken,
            'accept':'application/atom+json;content="application/atom+json"'
            }
        r= requests.get(recordURL, headers=headers)

    # if request is successful, return record as json   
    if r.status_code == 200:
        return r.json()
    # if not successful, return error message
    else:
        return r.text
        

# gets access token to start off the process. Token is refreshed in the readFromMetadataAPI function if necessary.
authorizationToken = getAccessToken()



# do stuff below here. This is a simple example.

print(readFromMetadataAPI("45728sdfg323"))
   







