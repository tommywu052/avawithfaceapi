import logging
import requests
import json
import azure.functions as func
 

# set to your own subscription key value
subscription_key = '{Your Subscription Key}'

# replace <My Endpoint String> with the string from your endpoint URL
face_api_url = '{FaceAPI endpoint URL}/face/v1.0/detect'

detectheaders = {'Ocp-Apim-Subscription-Key': subscription_key,
            'Content-Type':'application/octet-stream'}

params = {
    'returnFaceId': 'true',
    'returnFaceLandmarks': 'false',
    'returnFaceAttributes': 'age,gender,headPose,smile,facialHair,glasses,emotion,hair,makeup,occlusion,accessories,blur,exposure,noise',
    'recognitionModel': 'recognition_02'
}

DEFAULT_BASE_URL = '{FaceAPI endpoint URL}/face/v1.0/'
imageSizeW = 416
imageSizeH = 416
GroupID = '{Your Face Group ID}'

def request(method, url, data=None, json=None, headers=None, params=None):
    # pylint: disable=too-many-arguments
    """Universal interface for request."""

    # Make it possible to call only with short name (without BaseUrl).
    if not url.startswith('https://'):
        url = DEFAULT_BASE_URL + url
    
    print(url)

    # Setup the headers with default Content-Type and Subscription Key.
    headers = headers or {}
    if 'Content-Type' not in headers:
        headers['Content-Type'] = 'application/json'
    headers['Ocp-Apim-Subscription-Key'] = subscription_key

    response = requests.request(
        method,
        url,
        params=params,
        data=data,
        json=json,
        headers=headers)

    # Handle result and raise custom exception when something wrong.
    result = None
    # `person_group.train` return 202 status code for success.
    if response.status_code not in (200, 202):
        try:
            error_msg = response.json()['error']
        except:
            print("Unexpected error:",error_msg)

    # Prevent `response.json()` complains about empty response.
    if response.text:
        result = response.json()
    else:
        result = {}

    return result


def identify(face_ids,
             person_group_id=None,
             large_person_group_id=None,
             max_candidates_return=1,
             threshold=None):
 
    url = 'identify'
    json = {
        'faceIds': face_ids,
        'personGroupId': person_group_id,
        'largePersonGroupId': large_person_group_id,
        'maxNumOfCandidatesReturned': max_candidates_return,
        'confidenceThreshold': threshold,
        'recognitionModel': 'recognition_02'
    }
    print(json)

    return request('POST', url, json=json)

def get(person_group_id, person_id):
    url = 'persongroups/{}/persons/{}'.format(person_group_id, person_id)
    return request('GET', url)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_body()
        detectresponse = requests.post(face_api_url, params=params, headers=detectheaders, data=req_body) 
        psncnt = len(detectresponse.json())
        facearray =[]
        #rtnavajson = {}
        if(psncnt > 0 ) :
            for i in range(psncnt):
                boxrec = detectresponse.json()[i]['faceRectangle']
                face_id = detectresponse.json()[i]['faceId']                  
                if( face_id and boxrec['left']) :
                    #print(face_id)
                    responseidf = identify([face_id], GroupID, None, 1, 0.5)
                    if(len(responseidf[0]['candidates'])>0):
                        personid = responseidf[0]['candidates'][0]['personId']
                        pconf = responseidf[0]['candidates'][0]['confidence']
                        responseperson = get(GroupID, personid)
                    else :
                        responseperson['name']='Unidentified'
                        pconf=1

                    facejson = {
                            "type": "entity",
                            "entity": {
                                "tag": {
                                    "value": responseperson['name'],
                                    "confidence": pconf
                                },
                                "box": {
                                    "l": boxrec['left']/imageSizeW,
                                    "t": boxrec['top']/imageSizeH,
                                    "w": boxrec['width']/imageSizeW,
                                    "h": boxrec['height']/imageSizeH
                                }
                            }
                    }
                    facearray.append(facejson)
                    
            rtnavajson ={
                "inferences": facearray
            }       
            return func.HttpResponse(json.dumps(rtnavajson), mimetype="application/json", status_code=200) 
        else :
            return func.HttpResponse(status_code=204) 
    except ValueError:
        pass

    
