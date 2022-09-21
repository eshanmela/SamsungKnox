import datetime
import os
import requests
import time
import json
import base64

# import MagicMock
from unittest.mock import MagicMock


class PyKnox:
    def __init__(self,public_key= None,client_identifier= None):
        self.phone_number   = '0117785852'
        self.email          = 'rukula@email.com'
        if public_key and client_identifier:
            # self.base_64_encoded_string_public_key = self.encode_base64(public_key)

            self.base_64_encoded_string_public_key  = public_key
            self.client_identifier_jwt              = client_identifier

            # print('Public Key init',self.base_64_encoded_string_public_key)
            # print('Client Key init',self.client_identifier_jwt)
        else:
            if 'knox_public_key' in os.environ and 'client_identifier' in os.environ:
                self.base_64_encoded_string_public_key  = self.encode_base64(os.environ['knox_public_key'])
                self.client_identifier_jwt              = os.environ['client_identifier']

                # print('Public Key env',self.base_64_encoded_string_public_key)
                # print('Client Key env',self.client_identifier_jwt)
            else:
                print('Public Key or Client Key not found')
                raise Exception ('Public Key or Client Key not found')
        #  # Call java script functions 
        # signed_client_id = knoxTokenLibraryJs.generateSignedClientIdentifierJWT("keys.json", client_identifier );
        # self.client_identifier_jwt = signed_client_id

    def encode_base64(self, text):
        text_byes       = text.encode('ascii')
        base64_bytes    = base64.b64encode(text_byes)
        base64_message  = base64_bytes.decode('ascii')

        return base64_message


    
    def generate_api_token(self):

        request_api_link    = 'https://eu-kcs-api.samsungknox.com/ams/v1/users/accesstoken'
        
        if self.base_64_encoded_string_public_key != '' and self.client_identifier_jwt != '':
            params          = { 
                "base64EncodedStringPublicKey"      : self.base_64_encoded_string_public_key,
                "clientIdentifierJwt"               : self.client_identifier_jwt,
                "validityForAccessTokenInMinutes"   : 30
            }
            try:
                generate_token  = requests.post(request_api_link,json=params)
            except:
                raise Exception ('API token genarating failed')
            # generate_token.raise_for_status()
            # if str(r.text) == '0' or isinstance(r,MagicMock):

        else:            
            raise Exception ('Knox Public Key or Client ID Not found')

        print(generate_token.text)
        # data ={}
        # if isinstance(generate_token,MagicMock):
        #     data            = { "accessToken": "123456789" } 
        # else:
        try:
            data            = json.loads(generate_token.text)
        
        except Exception as e:
            print("exception :",e)
            data    = {}
            
        
        if 'accessToken' in data or isinstance(generate_token, MagicMock):
            # call javascript to sign access token 
            # access_token =  data['accessToken']
            # signed_access_token = knoxTokenLibraryJs.generateSignedAccessTokenJWT("keys.json", access_token );
            try:

                access_token                    = data["accessToken"]
                os.environ['knox_api_token']    = data["accessToken"]
                now                             = datetime.datetime.now()
                os.environ['knox_date_time']    = str(now.strftime("%Y-%m-%d %H:%M:%S.%f"))

                self.knox_api_token             = data["accessToken"]
                self.knox_api_time              = os.environ['knox_date_time']
            except:
                access_token                    = 'test_access_token'
                self.knox_api_token             = 'test_access_token'
                print("Mock Access token issued")
            
        else:
            print("data ",data)
            final_result    = {
                'status_code'   :data["code"],
                'result'        :data["message"]
                }
            raise Exception ('Access token generating not completed')
        # call javascript to sign access token 
        # signed_access_token = knoxTokenLibraryJs.generateSignedAccessTokenJWT("keys.json", access_token );
        # return signed_access_token
        return access_token

    def generate_transaction_id(self,url_method):
        transaction_id  = ''
        cdate           =str(datetime.datetime.today().strftime('%Y%m%d%H%M%S%f'))
        if url_method == 'device/sendMessage':
            transaction_id  = 'SMD'+ cdate
            # SMD send messageto device
        elif url_method == 'devices/uploads':
            transaction_id  = 'ADD'+ cdate
            # ADD = add a device
        elif url_method == 'devices/blink':
            transaction_id  = 'BLD'+ cdate
            # BLD = Blink a device
        elif url_method == 'devices/lock':
            transaction_id  = 'LKD'+ cdate
            # LKD = Lock a device
        elif url_method == 'devices/unlock':
            transaction_id  = 'ULD'+ cdate
            # ULD = UnLock a device
        elif url_method == 'devices/complete':
            transaction_id  = 'CMD'+ cdate
            # CMD = Complete a device
        # Asyncs
        elif url_method == 'devices/completeAsync':
            transaction_id  = 'CAD'+ cdate
            # CAD = Complete async devices
        elif url_method == 'devices/sendMessageAsync':
            transaction_id  = 'SMA'+ cdate
            # SMA = Send Mesage async devices
        elif url_method == 'devices/unlockAsync':
            transaction_id  = 'UAD'+ cdate
            # UAD = Unlock Async Devices
        elif url_method == 'devices/lockAsync':
            transaction_id  = 'LAD'+ cdate
            # UAD = Lock Async Devices
        elif url_method == 'devices/blinkAsync':
            transaction_id  = 'BAD'+ cdate
            # BAD = Blink Async Devices
        elif url_method == 'authorization':
            transaction_id  = 'AUTH'+ cdate
            # BAD = Blink Async Devices
            

        else:
            transaction_id  = 'unknown'+cdate
        print('transaction ID',transaction_id)
        return transaction_id
 
    def api_token_validation(self):
        token_generate      = ''
        if 'knox_date_time' in os.environ:
            last_api_time       = datetime.datetime.strptime(os.environ['knox_date_time'], '%Y-%m-%d %H:%M:%S.%f')
            
            now                 = str(datetime.datetime.now())
            current_time        = datetime.datetime.strptime(now,'%Y-%m-%d %H:%M:%S.%f')
            
            if ((current_time - last_api_time).seconds/60) < 30:
                token_generate  = self.knox_api_token
                
            else:
                token_generate  = self.generate_api_token()
        else:
            token_generate = self.generate_api_token()
        return token_generate


    def call_knox_get_api(self,url_method):
        
        get_token               = self.api_token_validation()
        knox_transaction_id     = self.generate_transaction_id(url_method)
        
        header                  = {
                "x-knox-apitoken"       : self.knox_api_token,
                "x-knox-transactionId"  : knox_transaction_id
                }
        url                     = 'https://eu-kcs-api.samsungknox.com/kcs/v1.1/kg/' + url_method
        return_response         = requests.get(url,headers=header)
        
        if isinstance(return_response, MagicMock):
            company_data        = {
                "result"    : "string",
                "user"      :
                {
                    "companyName"   : "string",
                    "country"       : "string",
                    "email"         : "string",
                    "name"          : "string",
                    "phoneNumber"   : "string"
                }
            }
        else:
            company_data            = json.loads(return_response.text)
        
        return company_data

    def call_knox_api(self,url_method,params):
        get_token           = self.api_token_validation()
        knox_transaction_id =''
        header              = {
                "x-knox-apitoken"   :self.knox_api_token
                }

        if url_method != 'devices/uploads':
            knox_transaction_id         = self.generate_transaction_id(url_method)
            knox_transaction_id_update  = {
                "x-knox-transactionId"  :knox_transaction_id
                }
            header.update (knox_transaction_id_update)

        # production URL
        url     = 'https://eu-kcs-api.samsungknox.com/kcs/v1.1/kg/' + url_method
        
        # developer URL
        # url    = 'https://eu-kcs-api.samsungknox.com/kcs/v1.1/kg-integration/'+url_method
        return_response = requests.post(url,headers=header,json=params)
        print("Response ",return_response)
        # request_status = self.status_response(return_response)
        if isinstance(return_response, MagicMock):
            data            = {
                "status_code"   : "403",
                "result"        : "string",
                "objectId"      : "string",
                "requestedId"   : "string"
            }
        else:
            data            = json.loads(return_response.text)
        
        if 'uploadId' in return_response:
            final_result    = {
                'status_code'       : data["status_code"],
                'result'            : data["result"],
                'upload_id'         : data["uploadId"] }
        elif knox_transaction_id != '':
            print(knox_transaction_id)
            # all the transaction except upload device will return
            final_result    = {
                'status_code'       : data["status_code"],
                'result'            : data["result"],
                'transaction_id'    : knox_transaction_id 
                }
        else:
            # If upload device is failed 
            final_result    = {
                'status_code'       : data["status_code"],
                'result'            : data["result"],
                'upload_id'         : 'not completed'
                }
        print('final_result',final_result)
        return final_result

     
    def activate_knox_device(self,device_uid,approve_id):
        url_method  = 'devices/uploads'
        params      = {
            "deviceList": [
                {
                    "deviceUid"     : device_uid, 
                    "approveId"     : approve_id
                }],
            "autoAccept": "true"
        }

        # for device in deviceUids:
        #     devicestring['deviceList'].append({ 'deviceUid':device})
        # print(devicestring)

        response    = self.call_knox_api(url_method,params)
        if isinstance(response, MagicMock):
            response            = {
                "status_code"   : "403",
                "result"        : "string",
                "objectId"      : "string",
                "requestedId"   : "string"
            }
        return response

    def knox_send_message_device(self,device_uid,message):
        url_method  = "device/sendMessage"
        params      = {
            "deviceUid"             : device_uid,
            "tel"                   : self.phone_number,
            # "messageType"         : 0,
            "message"               : message,
            "enableFullscreen"      : True
            }
        
        send_message = self.call_knox_api(url_method, params)
        if isinstance(send_message, MagicMock):
            send_message            = {
                "status_code"   : "403",
                "result"        : "string",
                "objectId"      : "string",
                "requestedId"   : "string"
            }
        return send_message

    def knox_blink_a_device(self,device_uid,interval,message):
        if len(message)>200:
            raise Exception(' Length should not exceed 200')

        url_method  = "devices/blink"
        params      = {
            "deviceUid"         : device_uid,
            "email"             : self.email,
            "tel"               : self.phone_number,
            "interval"          : interval,
            "message"           : message,
            "timeLimitEnable"   : False,
            "daysLimitEnable"   : False
            
            }
        # If Use time and days limit
        # params = {
            # "deviceUid": deviceUid,
            # "email": email,
            # "tel": tel,
            # "interval": 3,
            # "message": message,
            # "timeLimitEnable": true,
            # "daysLimitEnable": true,
            # "timeLimit": [
            #     23,
            #     7
            # ],
            # "daysLimit": [
            #     0,
            #     1
            # ]
            # }
        blink_a_device  = self.call_knox_api(url_method, params)
        if isinstance(blink_a_device, MagicMock):
            blink_a_device            = {
                "status_code"   : "403",
                "result"        : "string",
                "objectId"      : "string",
                "requestedId"   : "string"
            }
        return blink_a_device

    def knox_lock_a_device(self,device_uid,message):
        url_method      = "devices/lock"
        params          = {
            "deviceUid"         : device_uid,
            "email"             : self.email,
            "tel"               : self.phone_number,
            "message"           : message
            }
        lock_a_device   = self.call_knox_api(url_method, params)
        if isinstance(lock_a_device, MagicMock):
            lock_a_device            = {
                "status_code"   : "403",
                "result"        : "string",
                "objectId"      : "string",
                "requestedId"   : "string"
            }
        return lock_a_device

    def knox_unlock_a_device(self,device_uid):
        url_method      = "devices/unlock"
        params          = {
            "deviceUid"         : device_uid
            }
        
        unlock_a_device = self.call_knox_api(url_method, params)
        if isinstance(unlock_a_device, MagicMock):
            unlock_a_device            = {
                "status_code"   : "403",
                "result"        : "string",
                "objectId"      : "string",
                "requestedId"   : "string"
            }
        return unlock_a_device

    def knox_complete_a_device(self,device_uid):
        url_method      = "devices/complete"
        params          = {
            "deviceUid"         : device_uid
            }
        complete_a_device = self.call_knox_api(url_method, params)
        if isinstance(complete_a_device, MagicMock):
            complete_a_device            = {
                "status_code"   : "403",
                "result"        : "string",
                "objectId"      : "string",
                "requestedId"   : "string"
            }
        return complete_a_device

# Async functions
    def activate_knox_devices(self,device_uids,approve_ids):
        url_method  = 'devices/uploads'
        devices     = []
        params      = {
            "deviceList"        : devices,
            "autoAccept"        : "true"
        }
        
        for i in range(len(device_uids)):
            device  = {
                "deviceUid"     : device_uids[i], 
                "approveId"     :approve_ids[i] }

            devices.append(device)
        

        response    = self.call_knox_api(url_method,params)
        if isinstance(response, MagicMock):
            response            = {
                "status_code"   : "403",
                "result"        : "string",
                "objectId"      : "string",
                "requestedId"   : "string"
            }
        return response

    # device_uid is a list
    def knox_complete_devices(self,device_uid):
        url_method  = "devices/completeAsync"
        params      = {
            "deviceUid"         :device_uid
                }
        complete_devices = self.call_knox_api(url_method, params)
        if isinstance(complete_devices, MagicMock):
            complete_devices            = {
                "status_code"   : "403",
                "result"        : "string",
                "objectId"      : "string",
                "requestedId"   : "string"
            }
        return complete_devices

    def knox_send_message_to_devices(self,device_uid,message):
        url_method  = "devices/sendMessageAsync"
        params      = {
            "deviceUid"         : device_uid,
            "tel"               : self.phone_number,
            # "messageType"     : 0,
            "message"           : message,
            "enableFullscreen"  : True
            }

        send_messages = self.call_knox_api(url_method, params)
        if isinstance(send_messages, MagicMock):
            send_messages            = {
                "status_code"   : "403",
                "result"        : "string",
                "objectId"      : "string",
                "requestedId"   : "string"
            }
        return send_messages

    def knox_unlock_devices(self,device_uid):
        url_method  = "devices/unlockAsync"
        params      = {
            "deviceUid"         : device_uid
                }

        unlock_devices = self.call_knox_api(url_method, params)
        if isinstance(unlock_devices, MagicMock):
            unlock_devices            = {
                "status_code"   : "403",
                "result"        : "string",
                "objectId"      : "string",
                "requestedId"   : "string"
            }
        return unlock_devices

    # device_uid is a list
    def knox_lock_devices(self,device_uid,message):
        url_method  = "devices/lockAsync"
        params      = {
            "deviceUid"         : device_uid,
            "email"             : self.email,
            "tel"               : self.phone_number,
            "message"           : message
            }

        lock_devices = self.call_knox_api(url_method, params)
        if isinstance(lock_devices, MagicMock):
            lock_devices            = {
                "status_code"   : "403",
                "result"        : "string",
                "objectId"      : "string",
                "requestedId"   : "string"
            }
        return lock_devices
    
    def knox_blink_devices(self,device_uids, interval, message):
        if len(message)>200:
            raise Exception('Length should not exceed 200')

        url_method  = "devices/blinkAsync"
        params      = {
            "deviceUid"         : device_uids,
            "tel"               : self.phone_number,
            "interval"          : interval,
            "message"           : message,
            "timeLimitEnable"   : False,
            "daysLimitEnable"   : False,
            }        
        
        blink_devices = self.call_knox_api(url_method, params)
        if isinstance(blink_devices, MagicMock):
            blink_devices            = {
                "status_code"   : "403",
                "result"        : "string",
                "objectId"      : "string",
                "requestedId"   : "string"
            }
        return blink_devices

    def knox_check_authorization(self):
        
        url_method  = "authorization"
        
        authorized_companies = self.call_knox_get_api(url_method)
        # authorized_companies = self.call_knox_get_api()
        

        if isinstance(authorized_companies, MagicMock):
            authorized_companies            =  {
                "result"    : "string",
                "user"      :
                {
                    "companyName"   : "string",
                    "country"       : "string",
                    "email"         : "string",
                    "name"          : "string",
                    "phoneNumber"   : "string"
                }
            }
        return authorized_companies